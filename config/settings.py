"""
Configurazioni centralizzate per Officina AI Assistant
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Carica variabili d'ambiente
load_dotenv()

# Supporto per Streamlit Cloud secrets
try:
    import streamlit as st
    if hasattr(st, 'secrets'):
        # Siamo su Streamlit Cloud, usa secrets
        os.environ.update(st.secrets)
except:
    pass

class Settings(BaseSettings):
    """Configurazioni dell'applicazione"""
    
    # ===== PATHS =====
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    MANUALS_PATH: Path = DATA_DIR / "manuali"
    
    # ===== LLM PROVIDER =====
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "anthropic")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # ===== MODEL CONFIGURATION =====
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2000"))
    
    # ===== PINECONE =====
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "officina-manuali")
    
    # ===== RAG CONFIGURATION =====
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "300"))
    RETRIEVAL_K: int = int(os.getenv("RETRIEVAL_K", "5"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
    
    # ===== HYBRID SEARCH =====
    ENABLE_HYBRID_SEARCH: bool = os.getenv("ENABLE_HYBRID_SEARCH", "false").lower() == "true"
    HYBRID_KEYWORD_WEIGHT: float = float(os.getenv("HYBRID_KEYWORD_WEIGHT", "0.3"))
    HYBRID_SEMANTIC_WEIGHT: float = float(os.getenv("HYBRID_SEMANTIC_WEIGHT", "0.7"))
    
    # ===== DOCUMENT PROCESSING =====
    ENABLE_OCR: bool = os.getenv("ENABLE_OCR", "true").lower() == "true"
    OCR_LANGUAGE: str = os.getenv("OCR_LANGUAGE", "ita")
    EXTRACT_TABLES: bool = os.getenv("EXTRACT_TABLES", "true").lower() == "true"
    
    # ===== APPLICATION =====
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))
    
    # ===== ADVANCED FEATURES =====
    ENABLE_VISION: bool = os.getenv("ENABLE_VISION", "false").lower() == "true"
    VISION_MODEL: str = os.getenv("VISION_MODEL", "claude-sonnet-4-5-20250929")
    ENABLE_MEMORY: bool = os.getenv("ENABLE_MEMORY", "true").lower() == "true"
    MEMORY_TYPE: str = os.getenv("MEMORY_TYPE", "buffer")
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "true").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))
    
    # ===== SECURITY =====
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "")
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "").split(",")
    
    # ===== TEXT SPLITTER SEPARATORS =====
    TEXT_SEPARATORS: list = [
        "\n\n",
        "\n",
        ". ",
        "! ",
        "? ",
        "; ",
        ": ",
        " ",
        ""
    ]
    
    # ===== PROMPT TEMPLATES =====
    SYSTEM_PROMPT: str = """Sei un assistente esperto per officine meccaniche. 
Il tuo compito è rispondere a domande tecniche basandoti esclusivamente sui manuali di officina forniti.

Regole importanti:
1. Rispondi SOLO basandoti sulle informazioni presenti nei manuali
2. Se non trovi l'informazione, dillo chiaramente
3. Cita sempre la fonte (marca, modello, pagina)
4. Usa un linguaggio tecnico ma chiaro
5. Se ci sono procedure di sicurezza, menzionale sempre
6. Includi valori numerici specifici (coppie di serraggio, capacità, etc.)
7. Se la domanda è ambigua, chiedi chiarimenti su marca e modello

Formato risposta:
- Risposta diretta alla domanda
- Dettagli tecnici rilevanti
- Avvertenze di sicurezza (se applicabili)
- Fonte: [Marca Modello - Pagina X]
"""
    
    QA_PROMPT_TEMPLATE: str = """Usa le seguenti informazioni per rispondere alla domanda.

Contesto dai manuali:
{context}

Domanda: {question}

Risposta dettagliata:"""

    class Config:
        env_file = ".env"
        case_sensitive = True


# Istanza globale delle settings
settings = Settings()


def validate_settings():
    """Valida che le impostazioni essenziali siano configurate"""
    errors = []
    
    # Controlla LLM API Keys
    if settings.LLM_PROVIDER == "anthropic" and not settings.ANTHROPIC_API_KEY:
        errors.append("ANTHROPIC_API_KEY non configurata")
    elif settings.LLM_PROVIDER == "openai" and not settings.OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY non configurata")
    
    # Controlla Pinecone
    if not settings.PINECONE_API_KEY:
        errors.append("PINECONE_API_KEY non configurata")
    if not settings.PINECONE_ENVIRONMENT:
        errors.append("PINECONE_ENVIRONMENT non configurato")
    
    # Controlla path manuali
    if not settings.MANUALS_PATH.exists():
        settings.MANUALS_PATH.mkdir(parents=True, exist_ok=True)
    
    if errors:
        error_msg = "\n".join([f"❌ {error}" for error in errors])
        raise ValueError(f"Configurazione non valida:\n{error_msg}\n\nVedi .env.example per un template")
    
    return True


def get_llm_config():
    """Ritorna la configurazione per l'LLM selezionato"""
    if settings.LLM_PROVIDER == "anthropic":
        return {
            "provider": "anthropic",
            "api_key": settings.ANTHROPIC_API_KEY,
            "model": settings.ANTHROPIC_MODEL,
            "temperature": settings.LLM_TEMPERATURE,
            "max_tokens": settings.MAX_TOKENS
        }
    elif settings.LLM_PROVIDER == "openai":
        return {
            "provider": "openai",
            "api_key": settings.OPENAI_API_KEY,
            "model": settings.OPENAI_MODEL,
            "temperature": settings.LLM_TEMPERATURE,
            "max_tokens": settings.MAX_TOKENS
        }
    else:
        raise ValueError(f"LLM Provider non supportato: {settings.LLM_PROVIDER}")


if __name__ == "__main__":
    # Test configurazione
    try:
        validate_settings()
        print("✅ Configurazione valida!")
        print(f"\n📋 Riepilogo:")
        print(f"   LLM Provider: {settings.LLM_PROVIDER}")
        print(f"   Model: {settings.ANTHROPIC_MODEL if settings.LLM_PROVIDER == 'anthropic' else settings.OPENAI_MODEL}")
        print(f"   Vector DB: Pinecone ({settings.PINECONE_INDEX_NAME})")
        print(f"   Manuali: {settings.MANUALS_PATH}")
    except ValueError as e:
        print(f"\n{e}")