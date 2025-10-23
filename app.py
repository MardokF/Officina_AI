"""
Officina AI Assistant - Streamlit App
"""
import streamlit as st
import sys
from pathlib import Path

# Aggiungi src al path
sys.path.insert(0, str(Path(__file__).parent))

from src import OfficinaChatbot, get_available_brands, get_available_models
from src.utils import save_query_log
from config import settings, validate_settings

# Configurazione pagina
st.set_page_config(
    page_title="Officina AI Assistant",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizzato
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 0.5rem;
        border-left: 3px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)


def initialize_app():
    """Inizializza l'applicazione e il chatbot"""
    if 'initialized' not in st.session_state:
        try:
            with st.spinner("🔧 Inizializzazione Officina AI..."):
                # Valida configurazione
                validate_settings()
                
                # Inizializza chatbot
                st.session_state.chatbot = OfficinaChatbot()
                st.session_state.initialized = True
                st.session_state.messages = []
                
        except Exception as e:
            st.error(f"❌ Errore inizializzazione: {e}")
            st.info("💡 Assicurati di aver configurato correttamente il file .env")
            st.stop()


def format_sources(sources):
    """Formatta le fonti in HTML"""
    if not sources:
        return ""
    
    html = "<div class='source-box'>"
    html += "<strong>📚 Fonti:</strong><br><br>"
    
    for source in sources:
        html += f"<strong>{source['index']}. {source['marca']} {source['modello']}</strong>"
        if source['anno'] != "N/A":
            html += f" ({source['anno']})"
        html += f" - Pagina {source['pagina']}<br>"
        html += f"<em style='font-size: 0.9em;'>{source['filename']}</em><br><br>"
    
    html += "</div>"
    return html


def main():
    # Header
    st.markdown("<h1 class='main-header'>🔧 Officina AI Assistant</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Inizializza app
    initialize_app()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurazione")
        
        # Ottieni marche disponibili
        available_brands = ["Tutte"] + get_available_brands()
        
        # Filtro marca
        selected_brand = st.selectbox(
            "🏷️ Marca",
            available_brands,
            key="brand_filter"
        )
        
        # Filtro modello (dipende dalla marca)
        if selected_brand != "Tutte":
            available_models = ["Tutti"] + get_available_models(selected_brand)
            selected_model = st.selectbox(
                "🚗 Modello",
                available_models,
                key="model_filter"
            )
        else:
            selected_model = "Tutti"
        
        # Filtro anno (opzionale)
        anno = st.text_input("📅 Anno (opzionale)", key="year_filter")
        
        st.markdown("---")
        
        # Info sistema
        st.subheader("ℹ️ Info Sistema")
        st.info(f"""
        **LLM:** {settings.LLM_PROVIDER.upper()}  
        **Model:** {settings.ANTHROPIC_MODEL if settings.LLM_PROVIDER == 'anthropic' else settings.OPENAI_MODEL}  
        **Memoria:** {'Abilitata' if settings.ENABLE_MEMORY else 'Disabilitata'}
        """)
        
        # Pulsanti azione
        st.markdown("---")
        if st.button("🧹 Pulisci Chat", use_container_width=True):
            st.session_state.messages = []
            if settings.ENABLE_MEMORY:
                st.session_state.chatbot.clear_memory()
            st.rerun()
        
        if st.button("🔄 Ricarica Sistema", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    
    # Area principale - Chat
    st.subheader("💬 Chat")
    
    # Mostra storico chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Mostra fonti se presenti
            if "sources" in message and message["sources"]:
                st.markdown(format_sources(message["sources"]), unsafe_allow_html=True)
    
    # Input utente
    if prompt := st.chat_input("Fai una domanda sui manuali..."):
        # Aggiungi messaggio utente
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Genera risposta
        with st.chat_message("assistant"):
            with st.spinner("🔍 Cerco nei manuali..."):
                # Prepara filtri
                filters = {}
                if selected_brand != "Tutte":
                    filters["marca"] = selected_brand
                if selected_model != "Tutti":
                    filters["modello"] = selected_model
                if anno:
                    filters["anno"] = anno
                
                # Ottieni risposta
                try:
                    response = st.session_state.chatbot.ask(
                        question=prompt,
                        filters=filters if filters else None,
                        return_sources=True
                    )
                    
                    answer = response.get("answer", "Mi dispiace, non ho potuto generare una risposta.")
                    sources = response.get("sources", [])
                    
                    # Mostra risposta
                    st.markdown(answer)
                    
                    # Mostra fonti
                    if sources:
                        st.markdown(format_sources(sources), unsafe_allow_html=True)
                    
                    # Salva nel log
                    save_query_log(prompt, answer, sources)
                    
                    # Aggiungi a storico
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                    
                except Exception as e:
                    error_msg = f"❌ Errore: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💬 Messaggi", len(st.session_state.messages))
    
    with col2:
        st.metric("🏷️ Filtri Attivi", 
                 sum([selected_brand != "Tutte", 
                      selected_model != "Tutti", 
                      bool(anno)]))
    
    with col3:
        st.metric("🤖 LLM", settings.LLM_PROVIDER.upper())


if __name__ == "__main__":
    main()