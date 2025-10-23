"""
Utility functions per Officina AI Assistant
"""
import os
import logging
from pathlib import Path
from typing import Dict, List
import json

from config import settings

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


def setup_logging(log_file: str = "officina_ai.log"):
    """Setup logging con file e console"""
    log_path = settings.BASE_DIR / "logs" / log_file
    log_path.parent.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )


def validate_pdf_file(file_path: Path) -> bool:
    """Valida che un file sia un PDF valido"""
    if not file_path.exists():
        logger.error(f"File non trovato: {file_path}")
        return False
    
    if file_path.suffix.lower() != '.pdf':
        logger.error(f"File non è un PDF: {file_path}")
        return False
    
    if file_path.stat().st_size == 0:
        logger.error(f"File vuoto: {file_path}")
        return False
    
    return True


def format_file_size(size_bytes: int) -> str:
    """Formatta dimensione file in formato leggibile"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def extract_car_info(text: str) -> Dict[str, str]:
    """
    Estrae informazioni auto da un testo
    (marca, modello, anno se presenti)
    """
    info = {
        "marca": None,
        "modello": None,
        "anno": None
    }
    
    # Lista marche comuni
    marche = [
        "FIAT", "VOLKSWAGEN", "VW", "BMW", "MERCEDES", "AUDI",
        "FORD", "OPEL", "RENAULT", "PEUGEOT", "CITROEN",
        "TOYOTA", "HONDA", "NISSAN", "MAZDA", "HYUNDAI", "KIA"
    ]
    
    text_upper = text.upper()
    
    # Cerca marca
    for marca in marche:
        if marca in text_upper:
            info["marca"] = marca
            break
    
    # Cerca anno (4 cifre tra 1900 e 2030)
    import re
    anno_match = re.search(r'\b(19\d{2}|20[0-3]\d)\b', text)
    if anno_match:
        info["anno"] = anno_match.group(1)
    
    return info


def save_query_log(question: str, answer: str, sources: List[Dict] = None):
    """Salva log delle query per analisi"""
    log_dir = settings.BASE_DIR / "logs" / "queries"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "query_log.jsonl"
    
    log_entry = {
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "question": question,
        "answer_length": len(answer),
        "sources_count": len(sources) if sources else 0
    }
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')


def get_available_brands() -> List[str]:
    """Ottieni lista marche disponibili dai manuali"""
    manuals_path = settings.MANUALS_PATH
    
    if not manuals_path.exists():
        return []
    
    brands = set()
    
    for pdf_file in manuals_path.glob("**/*.pdf"):
        # Estrai marca dal nome file
        parts = pdf_file.stem.split("_")
        if len(parts) >= 1:
            brands.add(parts[0].upper())
    
    return sorted(list(brands))


def get_available_models(brand: str = None) -> List[str]:
    """Ottieni lista modelli disponibili (opzionalmente per una marca)"""
    manuals_path = settings.MANUALS_PATH
    
    if not manuals_path.exists():
        return []
    
    models = set()
    
    for pdf_file in manuals_path.glob("**/*.pdf"):
        parts = pdf_file.stem.split("_")
        
        # Se è specificata una marca, filtra
        if brand and len(parts) >= 1:
            if parts[0].upper() != brand.upper():
                continue
        
        # Aggiungi modello
        if len(parts) >= 2:
            models.add(parts[1])
    
    return sorted(list(models))


def sanitize_filename(filename: str) -> str:
    """Rimuovi caratteri non validi da un nome file"""
    import re
    # Rimuovi caratteri non alfanumerici, trattini e underscore
    sanitized = re.sub(r'[^\w\s-]', '', filename)
    # Sostituisci spazi con underscore
    sanitized = re.sub(r'\s+', '_', sanitized)
    return sanitized


def create_backup(source_dir: Path, backup_name: str = None):
    """Crea backup di una directory"""
    import shutil
    from datetime import datetime
    
    if backup_name is None:
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    backup_dir = settings.BASE_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    backup_path = backup_dir / backup_name
    
    logger.info(f"📦 Creazione backup: {backup_path}")
    shutil.copytree(source_dir, backup_path)
    logger.info(f"✅ Backup creato")
    
    return backup_path


def print_colored(text: str, color: str = "white"):
    """Stampa testo colorato nel terminale"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }
    
    color_code = colors.get(color, colors["white"])
    print(f"{color_code}{text}{colors['reset']}")


def check_system_requirements():
    """Verifica requisiti di sistema"""
    print("\n🔍 Verifica Requisiti di Sistema\n")
    print("="*50)
    
    # Python version
    import sys
    python_version = sys.version.split()[0]
    print(f"✅ Python: {python_version}")
    
    # Required packages
    required_packages = [
        "langchain",
        "openai",
        "anthropic",
        "pinecone",
        "streamlit",
        "fastapi"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: Installato")
        except ImportError:
            print(f"❌ {package}: NON installato")
            missing_packages.append(package)
    
    # Environment variables
    print(f"\n{'='*50}")
    print("Variabili d'Ambiente:")
    
    required_vars = [
        "ANTHROPIC_API_KEY" if settings.LLM_PROVIDER == "anthropic" else "OPENAI_API_KEY",
        "PINECONE_API_KEY",
        "PINECONE_ENVIRONMENT"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var}: Configurata")
        else:
            print(f"❌ {var}: NON configurata")
            missing_vars.append(var)
    
    # Directory structure
    print(f"\n{'='*50}")
    print("Struttura Directory:")
    
    dirs_to_check = [
        settings.DATA_DIR,
        settings.MANUALS_PATH,
    ]
    
    for dir_path in dirs_to_check:
        if dir_path.exists():
            print(f"✅ {dir_path.name}: Esiste")
        else:
            print(f"⚠️  {dir_path.name}: Non esiste (verrà creata)")
    
    # Summary
    print(f"\n{'='*50}")
    if missing_packages or missing_vars:
        print_colored("❌ Sistema NON pronto", "red")
        if missing_packages:
            print(f"\n💡 Installa pacchetti mancanti:")
            print(f"   pip install {' '.join(missing_packages)}")
        if missing_vars:
            print(f"\n💡 Configura variabili d'ambiente nel file .env")
    else:
        print_colored("✅ Sistema PRONTO!", "green")
    
    print(f"{'='*50}\n")


if __name__ == "__main__":
    # Test utilities
    check_system_requirements()
    
    print("\n📊 Informazioni Configurazione:")
    print(f"   Marche disponibili: {get_available_brands()}")
    print(f"   Path manuali: {settings.MANUALS_PATH}")
    print(f"   LLM Provider: {settings.LLM_PROVIDER}")