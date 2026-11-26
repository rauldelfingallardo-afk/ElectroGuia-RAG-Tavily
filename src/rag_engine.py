import os
import sys

# Asegurar que Python encuentre config.py dentro de src/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from langchain_oci import ChatOCIGenAI, OCIGenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_tavily import TavilySearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class ElectroGuiaEngine:
    def __init__(self):
        settings.validate()

        # 1. Inicializar modelo de lenguaje (Cohere en OCI)
        self.llm = ChatOCIGenAI(
            model_id=settings.OCI_LLM_MODEL_ID,
            service_endpoint=settings.OCI_GENAI_ENDPOINT,
            compartment_id=settings.OCI_COMPARTMENT_ID,
            auth_profile=settings.OCI_CONFIG_PROFILE,
            model_kwargs={"temperature": 0.2, "max_tokens": 900},
        )

        # 2. Inicializar embeddings y cargar base vectorial FAISS local
        self.embeddings = OCIGenAIEmbeddings(
            model_id=settings.OCI_EMBEDDING_MODEL_ID,
            service_endpoint=settings.OCI_GENAI_ENDPOINT,
            compartment_id=settings.OCI_COMPARTMENT_ID,
            auth_profile=settings.OCI_CONFIG_PROFILE,
        )

        if not os.path.exists(settings.VECTOR_DB_DIR):
            raise FileNotFoundError(
                f"No se encontró el índice FAISS en '{settings.VECTOR_DB_DIR}'. "
                "Ejecuta primero 'python src/ingest.py'."
            )

        self.vectorstore = FAISS.load_local(
            settings.VECTOR_DB_DIR,
            self.embeddings,
            allow_dangerous_deserialization=True,
        )
        # Recuperar los 4 fragmentos más relevantes por consulta
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})

        # 3. Inicializar herramienta de búsqueda web en tiempo real (Tavily)
        self.tavily = TavilySearch(
            max_results=settings.TAVILY_MAX_RESULTS,
            topic="general",
        )

    def _evaluar_relevancia_local(self, pregunta: str, contexto_local: str) -> bool:
        """Usa el LLM para decidir si los PDFs locales alcanzan para responder bien."""
        if not contexto_local.strip():
            return False

        prompt_juez = ChatPromptTemplate.from_template(
            "Eres un evaluador técnico. Analiza si el siguiente CONTEXTO extraído de manuales "
            "eléctricos (como AEA 90364 y Ley de Ohm) contiene información suficiente y directa "
            "para responder la PREGUNTA del usuario.\n"
            "Responde únicamente con la palabra SI o NO.\n\n"
            "CONTEXTO:\n{contexto}\n\n"
            "PREGUNTA: {pregunta}\n"
            "RESPUESTA (SI/NO):"
        )
        cadena_juez = prompt_juez | self.llm | StrOutputParser()
        veredicto = cadena_juez.invoke(
            {"contexto": contexto_local, "pregunta": pregunta}
        ).strip().upper()
        return veredicto.startswith("SI")

    def _buscar_en_web(self, pregunta: str) -> tuple[str, list[dict]]:
        """Consulta Tavily agregando contexto técnico eléctrico de Argentina."""
        query_enriquecida = f"{pregunta} instalaciones electricas normativa Argentina"
        resultados_raw = self.tavily.invoke({"query": query_enriquecida})

        lista = (
            resultados_raw.get("results", [])
            if isinstance(resultados_raw, dict)
            else resultados_raw
        )

        fragmentos_web = []
        fuentes_web = []
        for r in lista:
            titulo = r.get("title", "Fuente web")
            url = r.get("url", "")
            contenido = r.get("content", "")
            fragmentos_web.append(f"[{titulo}]({url}): {contenido}")
            fuentes_web.append({"titulo": titulo, "url": url})

        return "\n\n".join(fragmentos_web), fuentes_web

    def consultar(self, pregunta: str, forzar_web: bool = False) -> dict:
        """
        Ejecuta el flujo completo RAG + Tavily:
        1. Busca en FAISS (PDFs locales).
        2. Evalúa si alcanza o si necesita complementar con Tavily.
        3. Genera una respuesta didáctica para electricistas principiantes.
        """
        # Paso A: Búsqueda en PDFs locales (FAISS)
        docs_locales = self.retriever.invoke(pregunta)
        contexto_local = ""
        fuentes_locales = []

        for doc in docs_locales:
            archivo = doc.metadata.get("source_file", "Documento local")
            pagina = doc.metadata.get("page", 0) + 1
            etiqueta = f"{archivo} (Pág. {pagina})"
            if etiqueta not in fuentes_locales:
                fuentes_locales.append(etiqueta)
            contexto_local += f"--- Fuente: {etiqueta} ---\n{doc.page_content}\n\n"

        # Paso B: Decidir si necesitamos Tavily (búsqueda web)
        usar_web = forzar_web or not self._evaluar_relevancia_local(pregunta, contexto_local)
        contexto_web = ""
        fuentes_web = []

        if usar_web:
            try:
                contexto_web, fuentes_web = self._buscar_en_web(pregunta)
            except Exception as e:
                contexto_web = f"(No se pudo consultar Tavily: {e})"

        # Paso C: Redactar respuesta final clara, segura y pedagógica
        prompt_final = ChatPromptTemplate.from_template(
            "Eres 'ElectroGuía', un instructor técnico experto en electricidad domiciliaria e industrial "
            "en Argentina (Reglamentación AEA 90364, normas IRAM y seguridad eléctrica).\n"
            "Tu alumno es un electricista principiante: explica con claridad, paso a paso, usando "
            "ejemplos prácticos y destacando siempre las medidas de seguridad obligatorias.\n\n"
            "Reglas estrictas:\n"
            "1. Prioriza siempre la información del CONTEXTO DE MANUALES PDF.\n"
            "2. Usa el CONTEXTO WEB (Tavily) para complementar, actualizar o responder temas que no "
            "estén en los manuales.\n"
            "3. Cita de dónde sacaste cada dato técnico (nombre del PDF/página o fuente web).\n"
            "4. Si una maniobra implica riesgo eléctrico, incluye una advertencia breve de seguridad.\n\n"
            "CONTEXTO DE MANUALES PDF:\n{contexto_local}\n\n"
            "CONTEXTO WEB (TAVILY):\n{contexto_web}\n\n"
            "PREGUNTA DEL ALUMNO: {pregunta}\n\n"
            "RESPUESTA DIDÁCTICA:"
        )

        cadena_final = prompt_final | self.llm | StrOutputParser()
        respuesta = cadena_final.invoke(
            {
                "contexto_local": contexto_local or "Sin fragmentos locales relevantes.",
                "contexto_web": contexto_web or "No fue necesario consultar la web.",
                "pregunta": pregunta,
            }
        )

        return {
            "respuesta": respuesta,
            "uso_web": usar_web,
            "fuentes_locales": fuentes_locales,
            "fuentes_web": fuentes_web,
        }


# Bloque de prueba rápida por consola
if __name__ == "__main__":
    print("⚡ Inicializando ElectroGuiaEngine...")
    motor = ElectroGuiaEngine()

    preguntas_prueba = [
        "¿Qué sección mínima de cable y qué protección termomagnética lleva un circuito TUG según AEA 90364?",
        "¿Cuál es el precio aproximado hoy en Argentina de un interruptor diferencial de 2x40A 30mA marca Schneider o ABB?",
    ]

    for idx, q in enumerate(preguntas_prueba, start=1):
        print(f"\n{'='*70}")
        print(f"❓ PRUEBA {idx}: {q}")
        print("=" * 70)
        resultado = motor.consultar(q)
        print(f"🌐 ¿Consultó Tavily (Web)?: {'SÍ' if resultado['uso_web'] else 'NO (Solo PDFs locales)'}")
        print(f"📚 Fuentes PDF: {resultado['fuentes_locales']}")
        if resultado["fuentes_web"]:
            print(f"🔗 Fuentes Web: {[f['titulo'] for f in resultado['fuentes_web']]}")
        print(f"\n🤖 RESPUESTA:\n{resultado['respuesta']}")
