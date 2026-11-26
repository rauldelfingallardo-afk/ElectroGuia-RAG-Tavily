import os
import sys
import streamlit as st

# Asegurar que Python encuentre los módulos dentro de src/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_engine import ElectroGuiaEngine
from faqs import FAQS_POR_CATEGORIA

# 1. Configuración visual de la página
st.set_page_config(
    page_title="ElectroGuía AI - Asistente Técnico Eléctrico",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Cargar el motor RAG + Tavily en caché (se inicializa una sola vez)
@st.cache_resource(show_spinner="⚡ Conectando con OCI Generative AI y cargando manuales AEA...")
def cargar_motor():
    return ElectroGuiaEngine()

try:
    motor = cargar_motor()
except Exception as e:
    st.error(f"❌ Error al inicializar ElectroGuía: {e}")
    st.stop()

# 3. Inicializar estado de sesión (historial de chat y consulta seleccionada desde FAQ)
if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {
            "role": "assistant",
            "content": (
                "¡Hola! Soy **ElectroGuía** ⚡, tu instructor técnico en electricidad domiciliaria "
                "y normativa argentina (**AEA 90364** e **IRAM**).\n\n"
                "Puedes escribir tu duda aquí abajo o elegir una **Pregunta Frecuente** en el menú "
                "de la izquierda para empezar a aprender."
            ),
            "fuentes_locales": [],
            "fuentes_web": [],
            "uso_web": False,
        }
    ]

if "pregunta_pendiente" not in st.session_state:
    st.session_state.pregunta_pendiente = None

# 4. Barra lateral: Opciones y Catálogo de Preguntas Frecuentes (FAQs)
with st.sidebar:
    st.title("⚡ ElectroGuía AI")
    st.caption("Asistente RAG (OCI Cohere) + Búsqueda Web (Tavily)")

    forzar_web = st.toggle(
        "🌐 Forzar búsqueda web (Tavily)",
        value=False,
        help="Actívalo si deseas complementar siempre la normativa de tus PDFs con información actualizada de internet.",
    )

    if st.button("🗑️ Limpiar conversación", use_container_width=True):
        st.session_state.mensajes = [st.session_state.mensajes[0]]
        st.rerun()

    st.divider()
    st.subheader("📚 Preguntas Frecuentes (FAQ)")
    st.caption("Haz clic en cualquier tema para consultarlo al instante:")

    for categoria, preguntas in FAQS_POR_CATEGORIA.items():
        with st.expander(categoria, expanded=False):
            for idx, pregunta_faq in enumerate(preguntas):
                if st.button(
                    pregunta_faq,
                    key=f"faq_{categoria}_{idx}",
                    use_container_width=True,
                ):
                    st.session_state.pregunta_pendiente = pregunta_faq

# 5. Encabezado principal
st.title("⚡ ElectroGuía: Tu Instructor de Electricidad y Normativa AEA")
st.markdown(
    "Consulta sobre **Ley de Ohm**, **seguridad eléctrica**, **tableros**, **puesta a tierra** "
    "o **Reglamentación AEA 90364** con respaldo de manuales técnicos y búsqueda en tiempo real."
)

# 6. Mostrar historial de mensajes en pantalla
for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Mostrar trazabilidad de fuentes en las respuestas del asistente
        if msg["role"] == "assistant" and (msg.get("fuentes_locales") or msg.get("fuentes_web")):
            with st.expander("🔍 Ver fuentes consultadas"):
                if msg.get("uso_web"):
                    st.info("🌐 Se consultó la web en tiempo real mediante **Tavily Search**.")
                else:
                    st.success("📘 Respondido directamente desde tus **Manuales PDF locales (FAISS)**.")

                if msg.get("fuentes_locales"):
                    st.markdown("**📄 Documentos locales:**")
                    for f in msg["fuentes_locales"]:
                        st.markdown(f"- {f}")

                if msg.get("fuentes_web"):
                    st.markdown("**🔗 Enlaces web (Tavily):**")
                    for w in msg["fuentes_web"]:
                        st.markdown(f"- [{w['titulo']}]({w['url']})")

# 7. Capturar entrada del usuario (por teclado o por clic en una FAQ)
prompt_usuario = st.chat_input("Escribe tu consulta eléctrica aquí (ej: ¿Cómo se calcula la caída de tensión?)...")

if st.session_state.pregunta_pendiente:
    prompt_usuario = st.session_state.pregunta_pendiente
    st.session_state.pregunta_pendiente = None

# 8. Procesar la consulta y generar respuesta
if prompt_usuario:
    # Mostrar y guardar pregunta del usuario
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
    with st.chat_message("user"):
        st.markdown(prompt_usuario)

    # Consultar al motor RAG + Tavily y mostrar respuesta
    with st.chat_message("assistant"):
        with st.spinner("⚡ Analizando manuales AEA 90364 y verificando fuentes..."):
            try:
                resultado = motor.consultar(prompt_usuario, forzar_web=forzar_web)
                respuesta_texto = resultado["respuesta"]

                st.markdown(respuesta_texto)

                if resultado["fuentes_locales"] or resultado["fuentes_web"]:
                    with st.expander("🔍 Ver fuentes consultadas"):
                        if resultado["uso_web"]:
                            st.info("🌐 Se consultó la web en tiempo real mediante **Tavily Search**.")
                        else:
                            st.success("📘 Respondido directamente desde tus **Manuales PDF locales (FAISS)**.")

                        if resultado["fuentes_locales"]:
                            st.markdown("**📄 Documentos locales:**")
                            for f in resultado["fuentes_locales"]:
                                st.markdown(f"- {f}")

                        if resultado["fuentes_web"]:
                            st.markdown("**🔗 Enlaces web (Tavily):**")
                            for w in resultado["fuentes_web"]:
                                st.markdown(f"- [{w['titulo']}]({w['url']})")

                st.session_state.mensajes.append(
                    {
                        "role": "assistant",
                        "content": respuesta_texto,
                        "fuentes_locales": resultado["fuentes_locales"],
                        "fuentes_web": resultado["fuentes_web"],
                        "uso_web": resultado["uso_web"],
                    }
                )
            except Exception as e:
                st.error(f"❌ Ocurrió un error al procesar tu consulta: {e}")
