# ⚡ ElectroGuía AI — Asistente Técnico Eléctrico (RAG + Tavily)

[![Live Demo](https://shields.io🌐_Demo_en_Vivo-Probar_Aplicación-2ea44f?style=for-the-badge)](https://electroguia.144.22.231.88.nip.io)
[![OCI GenAI](https://shields.ioOracle_Cloud-Generative_AI-F80000?style=for-the-badge&logo=oracle)](https://oracle.com)
[![Python](https://shields.ioPython-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

**ElectroGuía AI** es un asistente inteligente de consulta técnica diseñado para electricistas principiantes, técnicos e instaladores en Argentina. Combina **Generación Aumentada por Recuperación (RAG)** sobre normativa oficial (**AEA 90364**, normas **IRAM**, **Ley de Ohm**, seguridad eléctrica y canalizaciones) con **búsqueda web en tiempo real (Tavily Search)**, desplegado 24/7 en **Oracle Cloud Infrastructure (OCI)**.

---

## 🌐 Prueba la Aplicación en Vivo (Live Demo)

👉 **Accede directamente desde tu navegador:** **[https://electroguia.<TU-IP-PUBLICA>.nip.io](https://electroguia.<TU-IP-PUBLICA>.nip.io)**

> *Desplegada 24/7 en una instancia Ubuntu de Oracle Cloud Infrastructure (OCI Compute) detrás de Nginx Reverse Proxy con certificado SSL/TLS (HTTPS).*

---

## 🏗️ Arquitectura del Sistema

El sistema implementa un flujo híbrido con evaluación automática de relevancia (*Self-Corrective / Adaptive RAG*):

```text
                       ┌───────────────────────────────────┐
                       │   OCI Object Storage (Bucket)     │
                       │  Manuales PDF (AEA 90364 / IRAM)  │
                       └─────────────────┬─────────────────┘
                                         │ (Ingesta inicial: ingest.py)
                                         ▼
┌──────────────┐       ┌───────────────────────────────────┐
│   Usuario    │──────▶│      Interfaz Web (Streamlit)     │
│ (Navegador)  │◀──────│   Chat + Catálogo FAQ por temas   │
└──────┬───────┘       └─────────────────┬─────────────────┘
       │ HTTPS (Certbot)                 │
       ▼                                 ▼
┌──────────────┐       ┌───────────────────────────────────┐
│ Nginx Proxy  │──────▶│   Motor RAG (ElectroGuiaEngine)   │
│  (*.nip.io)  │       │     OCI Generative AI (Cohere)    │
└──────────────┘       └─────────┬───────────────┬─────────┘
                                 │               │
                 1. Búsqueda     │               │ 2. Fallback / Actualidad
                    Semántica    ▼               ▼    (Si falta info local)
                       ┌─────────────────┐ ┌───────────────┐
                       │ Base Vectorial  │ │ Tavily Search │
                       │  FAISS (Local)  │ │   (API Web)   │
                       └─────────────────┘ └───────────────┘
```

### ✨ Características Principales
* **Ingesta Automatizada desde la Nube:** Descarga los manuales técnicos directamente desde **OCI Object Storage**, los fragmenta respetando contexto normativo y genera embeddings vectoriales con **OCI Cohere** almacenados localmente en **FAISS**.
* **Motor Híbrido Inteligente (`rag_engine.py`):** Evalúa automáticamente si los fragmentos recuperados de los PDFs locales son suficientes para responder la consulta. Si la pregunta requiere precios de mercado, disponibilidad de materiales en Argentina o información externa, activa **Tavily Search** de forma autónoma.
* **Trazabilidad Transparente:** Cada respuesta cita explícitamente el documento PDF y número de página consultado o los enlaces web verificados.
* **Catálogo Interactivo de Preguntas Frecuentes (`faqs.py`):** 16 preguntas fundamentales organizadas en 4 módulos pedagógicos (*Fundamentos*, *Instalaciones Domiciliarias*, *Seguridad Eléctrica* y *Tableros y Protecciones*).
* **Despliegue Multi-Proyecto 24/7:** Configurado como servicio `systemd` en Ubuntu (OCI Compute) detrás de **Nginx Reverse Proxy** con subdominios dinámicos (`nip.io`) y cifrado **SSL/TLS (Let's Encrypt)**.

---

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3.11+
* **Orquestación LLM & RAG:** LangChain (`langchain-oci`, `langchain-community`, `langchain-tavily`)
* **Modelos de IA:** Oracle Cloud Infrastructure (OCI) Generative AI (`cohere.command-r-plus` / `cohere.embed-multilingual-v3.0`)
* **Base Vectorial:** FAISS (Facebook AI Similarity Search)
* **Búsqueda Web en Tiempo Real:** Tavily Search API
* **Almacenamiento Cloud:** OCI Object Storage
* **Frontend:** Streamlit
* **Infraestructura & Seguridad:** OCI Compute (Ubuntu), `systemd`, Nginx Reverse Proxy, `nip.io`, Certbot (HTTPS)

---

## 📂 Estructura del Proyecto

```text
ElectroGuia-RAG-Tavily/
├── data/                   # Directorio local para manuales PDF (ignorado en Git)
├── faiss_index/            # Base de datos vectorial generada (ignorado en Git)
├── src/
│   ├── config.py           # Gestión y validación de variables de entorno
│   ├── ingest.py           # Descarga desde OCI Bucket, chunking e indexación FAISS
│   ├── rag_engine.py       # Motor híbrido RAG + Juez de relevancia + Tavily
│   ├── faqs.py             # Catálogo de preguntas frecuentes por categoría
│   ├── app.py              # Aplicación web interactiva en Streamlit
│   ├── test_connections.py # Validación de conectividad con OCI y Tavily
│   └── test_pipeline.py    # Suite de pruebas integradas de extremo a extremo
├── evidencia_tests.txt     # Reporte automático de ejecución de pruebas
├── .env.example            # Plantilla de variables de entorno requeridas
├── .gitignore              # Exclusión de credenciales, entornos y binarios pesados
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Documentación técnica
```

---

## 🚀 Instalación y Uso Local

### 1. Clonar el repositorio y crear entorno virtual
```bash
git clone https://github.com
cd ElectroGuia-RAG-Tavily
python -m venv venv

# En Windows:
.\venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configurar variables de entorno
Copia `.env.example` a `.env` y completa tus credenciales de **OCI** y **Tavily**:
```bash
cp .env.example .env
```

### 3. Validar conexiones e indexar documentos
```bash
# Verificar acceso a OCI LLM, OCI Embeddings y Tavily
python src/test_connections.py

# Descargar PDFs desde OCI Object Storage (o leer data/) y crear índice FAISS
python src/ingest.py
```

### 4. Ejecutar pruebas integradas y lanzar la aplicación
```bash
# Ejecutar suite de validación (genera evidencia_tests.txt)
python src/test_pipeline.py

# Iniciar interfaz web en Streamlit
streamlit run src/app.py
```

---

## 🧪 Evidencia de Pruebas

El proyecto incluye una suite de pruebas automatizadas (`src/test_pipeline.py`) que valida la configuración, el índice vectorial FAISS, el catálogo de FAQs, las consultas normativas sobre PDFs locales y el enrutamiento hacia Tavily Search. Los resultados de la última ejecución se encuentran documentados en [`evidencia_tests.txt`](./evidencia_tests.txt).

---

## ⚠️ Aviso Técnico y de Seguridad
Este asistente tiene fines educativos y de apoyo técnico. Toda intervención en instalaciones eléctricas reales debe ser ejecutada o supervisada por un **electricista matriculado**, respetando estrictamente las **5 Reglas de Oro de Seguridad Eléctrica** y la **Reglamentación AEA 90364** vigente en la República Argentina.