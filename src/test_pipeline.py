import os
import sys
from datetime import datetime

# Asegurar que Python encuentre los módulos dentro de src/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from faqs import FAQS_POR_CATEGORIA
from rag_engine import ElectroGuiaEngine


def ejecutar_suite_pruebas():
    lineas_reporte = []

    def log(texto: str):
        print(texto)
        lineas_reporte.append(texto)

    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log("=" * 75)
    log(f"🧪 REPORTE DE EVIDENCIA - ELECTROGUÍA RAG + TAVILY")
    log(f"📅 Fecha y hora de ejecución: {fecha_actual}")
    log("=" * 75)

    # TEST 1: Verificación de configuración y variables críticas
    log("\n[TEST 1] Verificando variables de entorno (.env)...")
    try:
        settings.validate()
        log("✅ PASS: Variables críticas de OCI y Tavily configuradas correctamente.")
    except Exception as e:
        log(f"❌ FAIL: Error en configuración: {e}")
        return

    # TEST 2: Verificación de base vectorial local FAISS
    log("\n[TEST 2] Verificando existencia de índice vectorial FAISS...")
    index_file = os.path.join(settings.VECTOR_DB_DIR, "index.faiss")
    pkl_file = os.path.join(settings.VECTOR_DB_DIR, "index.pkl")
    if os.path.exists(index_file) and os.path.exists(pkl_file):
        tamano_kb = round(os.path.getsize(index_file) / 1024, 2)
        log(f"✅ PASS: Índice FAISS encontrado ({tamano_kb} KB) en '{settings.VECTOR_DB_DIR}'.")
    else:
        log(f"❌ FAIL: No se encontró el índice FAISS en '{settings.VECTOR_DB_DIR}'.")
        return

    # TEST 3: Verificación del catálogo de Preguntas Frecuentes (FAQs)
    log("\n[TEST 3] Verificando catálogo de Preguntas Frecuentes (src/faqs.py)...")
    total_categorias = len(FAQS_POR_CATEGORIA)
    total_preguntas = sum(len(lista) for lista in FAQS_POR_CATEGORIA.values())
    assert total_categorias > 0 and total_preguntas >= 10, "Catálogo de FAQs incompleto"
    log(f"✅ PASS: Catálogo cargado con {total_categorias} categorías y {total_preguntas} preguntas.")

    # TEST 4: Inicialización del Motor Inteligente (OCI LLM + Embeddings + Tavily)
    log("\n[TEST 4] Inicializando ElectroGuiaEngine...")
    try:
        motor = ElectroGuiaEngine()
        log("✅ PASS: Motor ElectroGuiaEngine inicializado sin errores.")
    except Exception as e:
        log(f"❌ FAIL: No se pudo inicializar el motor: {e}")
        return

    # TEST 5: Consulta normativa (Debe resolverse desde PDFs locales sin requerir web)
    pregunta_local = "¿Qué colores de cables exige la reglamentación argentina para Fase, Neutro y Tierra?"
    log(f"\n[TEST 5] Ejecutando consulta de normativa local (RAG FAISS)...")
    log(f"   ❓ Pregunta: {pregunta_local}")
    res_local = motor.consultar(pregunta_local)
    assert len(res_local["respuesta"]) > 50, "La respuesta local es demasiado corta"
    assert len(res_local["fuentes_locales"]) > 0, "No se recuperaron fuentes de los PDFs locales"
    log(f"   🌐 ¿Usó búsqueda web?: {'SÍ' if res_local['uso_web'] else 'NO (100% PDF local)'}")
    log(f"   📚 Fuentes PDF recuperadas: {', '.join(res_local['fuentes_locales'])}")
    log(f"   📝 Extracto de respuesta: {res_local['respuesta'][:220].replace(chr(10), ' ')}...")
    log("✅ PASS: Consulta RAG local validada correctamente.")

    # TEST 6: Consulta de actualidad/mercado (Debe activar Tavily Search)
    pregunta_web = "¿Qué marcas de interruptores diferenciales homologados IRAM se consiguen hoy en Argentina?"
    log(f"\n[TEST 6] Ejecutando consulta híbrida con búsqueda web (Tavily)...")
    log(f"   ❓ Pregunta: {pregunta_web}")
    res_web = motor.consultar(pregunta_web, forzar_web=True)
    assert res_web["uso_web"] is True, "Tavily no se activó correctamente"
    assert len(res_web["fuentes_web"]) > 0, "Tavily no devolvió enlaces web"
    titulos_web = [w["titulo"] for w in res_web["fuentes_web"]]
    log(f"   🌐 Fuentes Web (Tavily): {titulos_web}")
    log(f"   📝 Extracto de respuesta: {res_web['respuesta'][:220].replace(chr(10), ' ')}...")
    log("✅ PASS: Integración con Tavily Search validada correctamente.")

    # Resumen final y guardado en archivo de evidencia
    log("\n" + "=" * 75)
    log("🎉 RESULTADO FINAL: 6/6 PRUEBAS SUPERADAS CON ÉXITO")
    log("=" * 75)

    ruta_evidencia = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evidencia_tests.txt")
    with open(ruta_evidencia, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas_reporte))

    print(f"\n💾 Evidencia guardada automáticamente en: {ruta_evidencia}")


if __name__ == "__main__":
    ejecutar_suite_pruebas()
