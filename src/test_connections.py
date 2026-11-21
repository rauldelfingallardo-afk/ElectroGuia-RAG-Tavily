import sys
import os

# Asegurar que Python encuentre el módulo config dentro de src/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from langchain_oci import ChatOCIGenAI, OCIGenAIEmbeddings
from langchain_tavily import TavilySearch

def test_oci_llm():
    print("\n--- 1. Probando conexión con OCI Generative AI (LLM Cohere) ---")
    try:
        llm = ChatOCIGenAI(
            model_id=settings.OCI_LLM_MODEL_ID,
            service_endpoint=settings.OCI_GENAI_ENDPOINT,
            compartment_id=settings.OCI_COMPARTMENT_ID,
            auth_profile=settings.OCI_CONFIG_PROFILE,
            model_kwargs={"temperature": 0.2, "max_tokens": 150}
        )
        respuesta = llm.invoke(
            "Hola, responde en una oración corta: ¿Qué es la reglamentación AEA 90364 en Argentina?"
        )
        print("✅ Conexión OCI LLM exitosa!")
        print(f"🤖 Respuesta: {respuesta.content}")
    except Exception as e:
        print(f"❌ Error conectando con OCI LLM: {e}")

def test_oci_embeddings():
    print("\n--- 2. Probando conexión con OCI Embeddings (Cohere Embed) ---")
    try:
        embeddings = OCIGenAIEmbeddings(
            model_id=settings.OCI_EMBEDDING_MODEL_ID,
            service_endpoint=settings.OCI_GENAI_ENDPOINT,
            compartment_id=settings.OCI_COMPARTMENT_ID,
            auth_profile=settings.OCI_CONFIG_PROFILE,
        )
        vector = embeddings.embed_query("Ley de Ohm y seguridad eléctrica en Argentina")
        print("✅ Conexión OCI Embeddings exitosa!")
        print(f"📊 Dimensión del vector generado: {len(vector)} valores")
    except Exception as e:
        print(f"❌ Error conectando con OCI Embeddings: {e}")

def test_tavily():
    print("\n--- 3. Probando conexión con Tavily Search API ---")
    try:
        tavily_tool = TavilySearch(
            max_results=settings.TAVILY_MAX_RESULTS,
            topic="general"
        )
        resultados = tavily_tool.invoke({"query": "reglamento AEA 90364 instalaciones electricas Argentina"})
        print("✅ Conexión Tavily exitosa!")
        
        lista_resultados = resultados.get("results", []) if isinstance(resultados, dict) else resultados
        if lista_resultados:
            primer_resultado = lista_resultados[0]
            print(f"🌐 Primer resultado encontrado: {primer_resultado.get('title', 'Sin título')}")
            print(f"🔗 URL: {primer_resultado.get('url', 'Sin URL')}")
        else:
            print("⚠️ Tavily respondió, pero no devolvió resultados para la búsqueda.")
    except Exception as e:
        print(f"❌ Error conectando con Tavily: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de conexión para ElectroGuia-RAG-Tavily...")
    try:
        settings.validate()
        print("✅ Variables críticas cargadas correctamente desde .env")
    except ValueError as err:
        print(f"❌ Error de configuración: {err}")
        sys.exit(1)

    test_oci_llm()
    test_oci_embeddings()
    test_tavily()
    print("\n🏁 Pruebas finalizadas.")
