import os
from dotenv import load_dotenv

# Cargar variables desde el archivo .env
load_dotenv()

class Settings:
    # --- OCI Base ---
    OCI_COMPARTMENT_ID = os.getenv("OCI_COMPARTMENT_ID")
    OCI_BUCKET_NAME = os.getenv("OCI_BUCKET_NAME", "electroguia-documents")
    OCI_NAMESPACE = os.getenv("OCI_NAMESPACE")
    OCI_CONFIG_PROFILE = os.getenv("OCI_CONFIG_PROFILE", "DEFAULT")

    # --- OCI Generative AI (Cohere) ---
    OCI_GENAI_ENDPOINT = os.getenv(
        "OCI_GENAI_ENDPOINT",
        "https://inference.generativeai.sa-saopaulo-1.oci.oraclecloud.com"
    )
    OCI_LLM_MODEL_ID = os.getenv("OCI_LLM_MODEL_ID", "cohere.command-a-03-2025")
    OCI_EMBEDDING_MODEL_ID = os.getenv("OCI_EMBEDDING_MODEL_ID", "cohere.embed-v4.0")

    # --- Búsqueda Web en Tiempo Real (Tavily) ---
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    TAVILY_MAX_RESULTS = int(os.getenv("TAVILY_MAX_RESULTS", 3))

    # --- Rutas Locales y Parámetros RAG ---
    LOCAL_DATA_DIR = os.path.join(os.getcwd(), os.getenv("DATA_DIR", "data"))
    VECTOR_DB_DIR = os.path.join(os.getcwd(), os.getenv("VECTOR_DB_DIR", "faiss_index"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))

    def validate(self):
        """Verifica que las variables críticas estén configuradas antes de ejecutar."""
        missing = []
        if not self.OCI_COMPARTMENT_ID or "xxxxxx" in self.OCI_COMPARTMENT_ID:
            missing.append("OCI_COMPARTMENT_ID (revisa que no tenga el valor de ejemplo 'xxxxxx')")
        if not self.TAVILY_API_KEY or "tu-api-key" in self.TAVILY_API_KEY:
            missing.append("TAVILY_API_KEY")
        if missing:
            raise ValueError(f"Faltan variables críticas o tienen valores de ejemplo en .env: {', '.join(missing)}")

settings = Settings()
