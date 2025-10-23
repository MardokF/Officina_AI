# 📂 Struttura Progetto

Documentazione completa della struttura del progetto Officina AI Assistant.

## 📁 Root Directory

```
officina-ai-assistant/
├── 📄 README.md              # Documentazione principale
├── 📄 QUICKSTART.md          # Guida rapida
├── 📄 LICENSE                # Licenza MIT
├── 📄 .env.example           # Template variabili ambiente
├── 📄 .gitignore             # File da ignorare in Git
├── 📄 requirements.txt       # Dipendenze Python
├── 📄 Dockerfile             # Container Docker
├── 📄 docker-compose.yml     # Orchestrazione Docker
├── 🐍 app.py                 # Applicazione Streamlit
├── 🐍 api.py                 # API REST FastAPI
│
├── 📁 config/                # Configurazioni
│   ├── __init__.py
│   └── settings.py           # Settings centralizzate
│
├── 📁 src/                   # Codice sorgente
│   ├── __init__.py
│   ├── document_processor.py # Elaborazione PDF
│   ├── vectorstore.py        # Gestione Pinecone
│   ├── qa_chain.py           # Chain RAG e LLM
│   └── utils.py              # Utility functions
│
├── 📁 scripts/               # Script utility
│   ├── index_manuals.py      # Indicizzazione manuali
│   ├── test_queries.py       # Test chatbot
│   └── cleanup_index.py      # Pulizia indice
│
├── 📁 data/                  # Dati
│   └── manuali/              # PDF manuali (gitignored)
│
├── 📁 tests/                 # Test
│   ├── __init__.py
│   └── test_basic.py         # Test base
│
└── 📁 docs/                  # Documentazione
    ├── SETUP.md              # Guida setup
    ├── API.md                # Docs API
    └── EXAMPLES.md           # Esempi pratici
```

## 📝 Descrizione Dettagliata

### 📄 File Principali

#### `README.md`
- Documentazione principale del progetto
- Overview caratteristiche
- Istruzioni installazione base
- Link a docs dettagliate

#### `QUICKSTART.md`
- Guida setup rapida (5 minuti)
- Comandi essenziali
- Primo test

#### `app.py`
- Applicazione web Streamlit
- Interfaccia chat interattiva
- Filtri e configurazione UI
- Visualizzazione fonti

#### `api.py`
- API REST con FastAPI
- Endpoints: /query, /health, /brands, etc.
- Documentazione OpenAPI integrata
- Autenticazione opzionale

#### `requirements.txt`
```
langchain
anthropic/openai
pinecone-client
streamlit
fastapi
... (vedi file completo)
```

### 📁 config/

#### `settings.py`
Configurazioni centralizzate del sistema:

```python
class Settings:
    # LLM Configuration
    LLM_PROVIDER: str
    ANTHROPIC_API_KEY: str
    
    # RAG Configuration
    CHUNK_SIZE: int
    RETRIEVAL_K: int
    
    # Pinecone
    PINECONE_API_KEY: str
    ...
```

**Importanza:**
- Singolo punto per tutte le config
- Validazione settings
- Type hints con Pydantic
- Facile override via .env

### 📁 src/

#### `document_processor.py`
Elaborazione e preprocessing PDF:

**Classi:**
- `ManualProcessor`: Classe principale

**Funzionalità:**
- Caricamento PDF
- OCR per PDF scansionati
- Estrazione tabelle
- Chunking intelligente
- Metadata extraction

**Uso:**
```python
processor = ManualProcessor()
chunks = processor.process_and_split()
```

#### `vectorstore.py`
Gestione vector database Pinecone:

**Classi:**
- `VectorStoreManager`: Gestione completa Pinecone

**Funzionalità:**
- Creazione indice
- Indicizzazione documenti
- Ricerca semantica
- Filtri metadata
- Statistiche indice

**Uso:**
```python
manager = VectorStoreManager()
manager.index_documents(chunks)
results = manager.search("query", filter_dict={"marca": "FIAT"})
```

#### `qa_chain.py`
Chain RAG e interazione LLM:

**Classi:**
- `OfficinaChatbot`: Chatbot completo con memoria
- `SimpleChatbot`: Versione semplificata

**Funzionalità:**
- Chain RAG con LangChain
- Memoria conversazionale
- Gestione prompt
- Formattazione risposte
- Multi-provider LLM

**Uso:**
```python
chatbot = OfficinaChatbot()
response = chatbot.ask("domanda", filters={...})
```

#### `utils.py`
Funzioni utility:

**Funzioni:**
- `validate_pdf_file()`: Validazione PDF
- `get_available_brands()`: Lista marche
- `save_query_log()`: Logging queries
- `check_system_requirements()`: Verifica sistema
- Altre utility...

### 📁 scripts/

#### `index_manuals.py`
Script principale per indicizzazione:

**Uso:**
```bash
python scripts/index_manuals.py           # Normale
python scripts/index_manuals.py --ocr     # Con OCR
python scripts/index_manuals.py --clear   # Reset indice
```

**Funzionalità:**
- Processa tutti i PDF in data/manuali
- Crea/aggiorna indice Pinecone
- Progress bar
- Statistiche finali

#### `test_queries.py`
Test automatici del chatbot:

**Uso:**
```bash
python scripts/test_queries.py           # Test automatici
python scripts/test_queries.py -i        # Modalità interattiva
```

**Funzionalità:**
- Suite test predefiniti
- Modalità interattiva
- Benchmark performance
- Logging risultati

#### `cleanup_index.py`
Manutenzione indice:

**Uso:**
```bash
python scripts/cleanup_index.py --stats            # Statistiche
python scripts/cleanup_index.py --delete-all       # Elimina tutto
python scripts/cleanup_index.py --delete-brand FIAT  # Elimina marca
```

### 📁 data/

#### `manuali/`
Directory per PDF manuali:

**Struttura:**
```
data/manuali/
├── FIAT_500_2020_Manuale_Officina.pdf
├── VW_Golf_2019_Service_Manual.pdf
├── BMW/
│   ├── BMW_320d_2021_Workshop.pdf
│   └── BMW_X5_2020_Service.pdf
└── ...
```

**Convenzione nomi:**
```
MARCA_MODELLO_ANNO_Tipo.pdf
```

**Note:**
- Directory gitignored (PDF non su Git)
- Supporta sottocartelle
- Metadata estratti da nome file

### 📁 tests/

#### `test_basic.py`
Test base del sistema:

**Test inclusi:**
- Import moduli
- Configurazione
- Processor manuali
- Utility functions

**Uso:**
```bash
pytest tests/
pytest tests/test_basic.py -v
```

### 📁 docs/

#### `SETUP.md`
Guida setup completa:
- Prerequisiti dettagliati
- Installazione passo-passo
- Configurazione API keys
- Troubleshooting completo

#### `API.md`
Documentazione API:
- Tutti gli endpoints
- Request/Response examples
- Esempi in Python/cURL/JavaScript
- Rate limiting
- Error handling

#### `EXAMPLES.md`
Esempi pratici:
- Uso Streamlit
- Chiamate API
- Python SDK
- Casi d'uso reali
- Script automation

## 🔄 Flusso di Lavoro

### 1. Setup Iniziale
```
.env.example → .env → validate_settings()
```

### 2. Preparazione Manuali
```
PDF → data/manuali/ → ManualProcessor → chunks
```

### 3. Indicizzazione
```
chunks → embeddings → Pinecone → index
```

### 4. Query
```
User Question → Retriever → LLM → Answer + Sources
```

## 🎯 Entry Points

### Per Sviluppatori

```python
# Uso diretto dei moduli
from src import OfficinaChatbot, ManualProcessor, VectorStoreManager

# Chatbot
chatbot = OfficinaChatbot()
response = chatbot.ask("domanda")

# Processor
processor = ManualProcessor()
chunks = processor.process_and_split()

# Vector store
manager = VectorStoreManager()
manager.index_documents(chunks)
```

### Per Utenti

```bash
# Web UI
streamlit run app.py

# API
uvicorn api:app --reload

# CLI
python scripts/test_queries.py -i
```

## 📊 Dipendenze

### Core
- `langchain`: Framework RAG
- `anthropic`/`openai`: LLM providers
- `pinecone-client`: Vector DB

### Processing
- `pypdf`: Lettura PDF
- `pdf2image` + `pytesseract`: OCR
- `tabula-py`: Estrazione tabelle

### Web/API
- `streamlit`: UI
- `fastapi` + `uvicorn`: API REST

### Utilities
- `python-dotenv`: Environment vars
- `tqdm`: Progress bars
- `pydantic`: Validazione

## 🔐 File Sensibili

**Non committare mai:**
- `.env` - API keys e secrets
- `data/manuali/*.pdf` - Manuali (copyright)
- `logs/` - Log files
- `__pycache__/` - Cache Python

**Gitignore include tutto questo.**

## 🚀 Estensioni Future

Possibili aggiunte alla struttura:

```
officina-ai-assistant/
├── 📁 frontend/              # React frontend separato
├── 📁 mobile/                # App mobile (React Native)
├── 📁 skills/                # Custom skills/plugins
├── 📁 models/                # Fine-tuned models
└── 📁 migrations/            # DB migrations
```

## 📞 Riferimenti

- [README](../README.md) - Main docs
- [SETUP](./SETUP.md) - Setup guide
- [API](./API.md) - API docs
- [EXAMPLES](./EXAMPLES.md) - Examples

---

**Struttura progettata per:**
✅ Scalabilità
✅ Manutenibilità
✅ Estensibilità
✅ Facilità d'uso