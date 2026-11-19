# ⚡ ElectroGuia-RAG-Tavily

Asistente técnico inteligente basado en Inteligencia Artificial, diseñado para **electricistas principiantes y estudiantes en Argentina**. 

> **⚠️ Nota Normativa Importante:** Si bien la electricidad es un fenómeno físico universal, las instalaciones y criterios de seguridad se rigen por las normativas vigentes de cada país. Este proyecto está adaptado específicamente al marco regulatorio y técnico de la **República Argentina** (Reglamentación AEA 90364).

---

## 🎯 Objetivo del Proyecto

Construir un pipeline en Python que combine **RAG (Retrieval-Augmented Generation)** utilizando **LangChain** junto con búsqueda web en tiempo real mediante **Tavily**. 

El sistema responderá consultas técnicas basándose prioritariamente en documentación oficial local (archivos `.pdf`) y complementará las respuestas con sugerencias, normativas complementarias o precios/materiales actualizados desde la web en español latinoamericano.

---

## 📚 Base de Conocimientos (Documentos `.pdf`)

El sistema se alimentará inicialmente de una carpeta local (`/data` o `/docs`) con bibliografía técnica en formato PDF enfocada en el aprendizaje en Argentina:
* **Reglamentación AEA 90364** (Asociación Electrotécnica Argentina).
* **Fundamentos teóricos:** Ley de Ohm, potencia eléctrica, circuitos serie y paralelo.
* **Seguridad eléctrica:** Protecciones (interruptores termomagnéticos, diferenciales/disyuntores), puesta a tierra (PAT) y elementos de protección personal (EPP).
* **Canalizaciones y cableado:** Cálculo de secciones de conductores, caños, bandejas y tableros eléctricos.

---

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3.10+
* **Orquestación LLM / RAG:** LangChain
* **Búsqueda Web (Agente/Herramienta):** Tavily Search API
* **Procesamiento de PDFs y Embeddings:** PyPDF / ChromaDB o FAISS *(a definir en el desarrollo)*
* **Entorno de Desarrollo:** Visual Studio Code (VS Code) + Git / GitHub

---

## 📁 Estructura Inicial del Proyecto

```text
ElectroGuia-RAG-Tavily/
├── data/                   # Archivos .pdf técnicos (AEA 90364, Ley de Ohm, etc.)
├── src/                    # Código fuente del pipeline en Python
├── .env                    # Variables de entorno (API Keys - NO subir a GitHub)
├── .gitignore              # Archivos y carpetas ignorados por Git
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Documentación principal del proyecto
```

---

## 🚀 Cómo empezar (Paso a Paso Local)

1. **Clonar este repositorio en tu PC:**
   ```bash
   git clone https://github.com
   cd ElectroGuia-RAG-Tavily
   ```

2. **Crear y activar un entorno virtual:**
   * En Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   * En Linux/Mac:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Instalar las dependencias:** *(una vez creado el archivo `requirements.txt`)*
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar las variables de entorno:**
   Crear un archivo `.env` en la raíz del proyecto con tus claves:
   ```env
   OPENAI_API_KEY=tu_clave_aqui
   TAVILY_API_KEY=tu_clave_aqui
   ```

---

## 📌 Estado del Proyecto

- [x] Creación del repositorio y documentación inicial (`README.md`).
- [ ] Configuración del entorno local en VS Code, `.gitignore` y `requirements.txt`.
- [ ] Carga y procesamiento (chunking + embeddings) de los archivos PDF técnicos.
- [ ] Integración de LangChain + Tavily para respuestas híbridas (PDFs + Web).
- [ ] Pruebas con casos prácticos de instalaciones eléctricas domiciliarias en Argentina.

---

## ⚠️ Descargo de Responsabilidad (Disclaimer)

Este software es una herramienta educativa y de consulta rápida. **No reemplaza el criterio profesional** ni la firma de un electricista matriculado habilitado por los entes reguladores correspondientes en Argentina. Siempre respete las normas de seguridad vigentes antes de intervenir una instalación eléctrica.
