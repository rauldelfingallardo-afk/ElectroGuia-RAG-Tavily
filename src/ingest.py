import os
import sys
import time
from pathlib import Path

# Asegurar que Python encuentre config.py dentro de src/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from langchain_community.document_loaders.pdf import PyMuPDFLoader # type: ignore
from langchain_text_splitters import RecursiveCharacterTextSplitter # type: ignore
from langchain_oci import OCIGenAIEmbeddings # type: ignore
from langchain_community.vectorstores import FAISS # type: ignore

def cargar_documentos_pdf(data_dir: str):
    """Recorre la carpeta data/ y extrae el texto de todos los archivos PDF."""
    ruta_datos = Path(data_dir)
    if not ruta_datos.exists():
        ruta_datos.mkdir(parents=True, exist_ok=True)
        print(f"📁 Se creó la carpeta '{data_dir}'. Coloca allí tus PDFs y vuelve a ejecutar.")
        return []

    archivos_pdf = list(ruta_datos.glob("*.pdf"))
    if not archivos_pdf:
        print(f"⚠️ No se encontraron archivos .pdf en '{data_dir}'.")
        return []

    documentos_totales = []
    print(f"📚 Se encontraron {len(archivos_pdf)} archivo(s) PDF para procesar:\n")

    for pdf_path in archivos_pdf:
        print(f"  📄 Leyendo: {pdf_path.name} ...", end=" ")
        try:
            loader = PyMuPDFLoader(str(pdf_path))
            docs = loader.load()
            # Agregar el nombre limpio del archivo a los metadatos para citar la fuente luego
            for doc in docs:
                doc.metadata["source_file"] = pdf_path.name
            documentos_totales.extend(docs)
            print(f"✅ ({len(docs)} páginas)")
        except Exception as e:
            print(f"❌ Error al leer {pdf_path.name}: {e}")

    return documentos_totales

def dividir_en_chunks(documentos):
    """Divide las páginas en fragmentos manejables respetando párrafos y oraciones."""
    print(f"\n✂️ Dividiendo documentos en fragmentos (size={settings.CHUNK_SIZE}, overlap={settings.CHUNK_OVERLAP})...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_documents(documentos)
    print(f"✅ Total de fragmentos generados: {len(chunks)}")
    return chunks

def crear_vectorstore_faiss(chunks):
    """Genera los embeddings con OCI Cohere por lotes y guarda el índice FAISS en disco."""
    print("\n🧠 Conectando con OCI Generative AI Embeddings (Cohere)...")
    embeddings = OCIGenAIEmbeddings(
        model_id=settings.OCI_EMBEDDING_MODEL_ID,
        service_endpoint=settings.OCI_GENAI_ENDPOINT,
        compartment_id=settings.OCI_COMPARTMENT_ID,
        auth_profile=settings.OCI_CONFIG_PROFILE,
    )

    # Procesamos en lotes (batches) de 90 chunks para respetar los límites de la API de OCI
    batch_size = 90
    total_chunks = len(chunks)
    vectorstore = None

    print(f"⚙️ Vectorizando {total_chunks} fragmentos en lotes de {batch_size}...")
    for i in range(0, total_chunks, batch_size):
        lote = chunks[i : i + batch_size]
        lote_num = (i // batch_size) + 1
        total_lotes = (total_chunks + batch_size - 1) // batch_size
        print(f"  🔄 Procesando lote {lote_num}/{total_lotes} ({len(lote)} fragmentos)...")

        if vectorstore is None:
            vectorstore = FAISS.from_documents(lote, embeddings)
        else:
            vectorstore.add_documents(lote)

        # Pausa breve para evitar saturar la cuota de peticiones por minuto en OCI
        if i + batch_size < total_chunks:
            time.sleep(1)

    # Guardar el índice localmente en disco
    os.makedirs(settings.VECTOR_DB_DIR, exist_ok=True)
    vectorstore.save_local(settings.VECTOR_DB_DIR)
    print(f"\n💾 ¡Base vectorial FAISS guardada exitosamente en '{settings.VECTOR_DB_DIR}'!")

def main():
    print("🚀 Iniciando proceso de ingesta de documentos para ElectroGuia-RAG-Tavily...")
    try:
        settings.validate()
    except ValueError as err:
        print(f"❌ Error de configuración: {err}")
        sys.exit(1)

    documentos = cargar_documentos_pdf(settings.LOCAL_DATA_DIR)
    if not documentos:
        print("🛑 Proceso detenido: no hay documentos para indexar.")
        return

    chunks = dividir_en_chunks(documentos)
    if not chunks:
        print("🛑 Proceso detenido: no se pudieron generar fragmentos de texto.")
        return

    crear_vectorstore_faiss(chunks)
    print("\n🎉 ¡Ingesta completada con éxito! Ya puedes construir el motor de consultas RAG.")

if __name__ == "__main__":
    main()
