# 🔧 Guida Setup Dettagliata

Questa guida ti accompagnerà passo-passo nel setup completo di Officina AI Assistant.

## 📋 Indice

1. [Prerequisiti](#prerequisiti)
2. [Installazione](#installazione)
3. [Configurazione API Keys](#configurazione-api-keys)
4. [Preparazione Manuali](#preparazione-manuali)
5. [Indicizzazione](#indicizzazione)
6. [Avvio Applicazione](#avvio-applicazione)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisiti

### Software Necessario

- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **Git** - [Download](https://git-scm.com/downloads)
- **Tesseract OCR** (opzionale, per PDF scansionati)
  - Windows: [Download](https://github.com/UB-Mannheim/tesseract/wiki)
  - Linux: `sudo apt install tesseract-ocr tesseract-ocr-ita`
  - Mac: `brew install tesseract tesseract-lang`

### Account Richiesti

1. **LLM Provider** (scegli uno):
   - [Anthropic Claude](https://console.anthropic.com/) - Raccomandato
   - [OpenAI](https://platform.openai.com/)

2. **Vector Database**:
   - [Pinecone](https://www.pinecone.io/) - Free tier disponibile

---

## Installazione

### 1. Clone Repository

```bash
git clone https://github.com/tuousername/officina-ai-assistant.git
cd officina-ai-assistant
```

### 2. Crea Ambiente Virtuale

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installa Dipendenze

```bash
pip install -r requirements.txt
```

**Verifica installazione:**
```bash
python -c "import langchain; print('✅ LangChain installato')"
```

---

## Configurazione API Keys

### 1. Ottieni le API Keys

#### Anthropic Claude (Raccomandato)

1. Vai su [console.anthropic.com](https://console.anthropic.com/)
2. Registrati o fai login
3. Vai su "API Keys"
4. Crea una nuova API key
5. Copia la chiave (inizia con `sk-ant-api...`)

**Costi stimati:**
- $3 per 1M token input
- $15 per 1M token output
- ~$0.50-2 per 1000 domande

#### OpenAI (Alternativa)

1. Vai su [platform.openai.com](https://platform.openai.com/)
2. Registrati o fai login
3. Vai su "API keys"
4. Crea una nuova API key
5. Copia la chiave (inizia con `sk-...`)

**Costi stimati:**
- ~$1-3 per 1000 domande (GPT-4)

#### Pinecone

1. Vai su [pinecone.io](https://www.pinecone.io/)
2. Registrati (free tier: 1 index, 100k vettori)
3. Crea un nuovo progetto
4. Copia:
   - API Key
   - Environment (es: `gcp-starter`, `us-east-1-aws`)

### 2. Configura File .env

```bash
# Copia il template
cp .env.example .env

# Modifica con il tuo editor
nano .env  # oppure code .env, vim .env, etc.
```

**Configurazione minima:**

```env
# Scegli Anthropic O OpenAI
ANTHROPIC_API_KEY=sk-ant-api-03-your-key-here
# OPENAI_API_KEY=sk-your-key-here

# Pinecone
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=officina-manuali

# Provider (anthropic o openai)
LLM_PROVIDER=anthropic
```

### 3. Testa Configurazione

```bash
python -c "from config import validate_settings; validate_settings(); print('✅ Config OK!')"
```

---

## Preparazione Manuali

### 1. Crea Struttura Directory

```bash
mkdir -p data/manuali
```

### 2. Aggiungi i Manuali PDF

Copia i tuoi manuali in `data/manuali/`

**Convenzione nomi file importante:**

```
MARCA_MODELLO_ANNO_Tipo.pdf
```

**Esempi:**
```
FIAT_500_2020_Manuale_Officina.pdf
VW_Golf_2019_Service_Manual.pdf
BMW_320d_2021_Workshop_Manual.pdf
```

**Tips:**
- Usa MAIUSCOLO per la marca
- Nessuno spazio nei nomi
- L'anno è opzionale ma raccomandato
- Puoi organizzare in sottocartelle

### 3. Verifica Manuali

```bash
python -c "from src import ManualProcessor; p = ManualProcessor(); print(p.get_manual_stats())"
```

---

## Indicizzazione

### 1. Primo Tentativo (Senza OCR)

```bash
python scripts/index_manuals.py
```

**Cosa fa:**
1. Legge tutti i PDF in `data/manuali/`
2. Estrae il testo
3. Divide in chunks
4. Crea embeddings
5. Carica su Pinecone

**Tempo stimato:** 2-10 minuti (dipende dal numero e dimensione dei PDF)

### 2. Se i PDF sono Scansionati (Con OCR)

Se il testo estratto è scarso o inesistente:

```bash
python scripts/index_manuals.py --ocr
```

**Nota:** L'OCR è MOLTO più lento (10-30 min per manuale grande)

### 3. Re-indicizzazione

Se devi rifare l'indicizzazione:

```bash
# Elimina indice esistente e ricrea
python scripts/index_manuals.py --clear
```

### 4. Verifica Indicizzazione

```bash
python -c "from src import VectorStoreManager; v = VectorStoreManager(); print(v.get_index_stats())"
```

Dovresti vedere:
```
{'total_vector_count': 1234, 'dimension': 1536, ...}
```

---

## Avvio Applicazione

### Opzione 1: Streamlit (Web UI)

```bash
streamlit run app.py
```

Apri browser su: `http://localhost:8501`

### Opzione 2: API REST

```bash
uvicorn api:app --reload
```

API disponibile su: `http://localhost:8000`
Documentazione: `http://localhost:8000/docs`

### Opzione 3: Test da Terminale

```bash
# Test automatico
python scripts/test_queries.py

# Modalità interattiva
python scripts/test_queries.py -i
```

### Opzione 4: Docker

```bash
# Build
docker-compose build

# Avvia
docker-compose up

# In background
docker-compose up -d
```

---

## Troubleshooting

### ❌ Errore: "ANTHROPIC_API_KEY non configurata"

**Soluzione:**
1. Controlla che il file `.env` esista
2. Verifica che `ANTHROPIC_API_KEY=...` sia presente
3. Assicurati di non avere spazi: `ANTHROPIC_API_KEY=sk-ant-...` (no spazi!)
4. Riavvia il terminale

### ❌ Errore: "Nessun manuale trovato"

**Soluzione:**
1. Verifica path: `ls data/manuali/`
2. Assicurati che i file siano `.pdf`
3. Controlla i permessi file

### ❌ Errore: "Pinecone index not found"

**Soluzione:**
```bash
# L'indice viene creato automaticamente all'indicizzazione
python scripts/index_manuals.py
```

### ❌ OCR non funziona

**Soluzione:**

**Windows:**
1. Installa Tesseract da [qui](https://github.com/UB-Mannheim/tesseract/wiki)
2. Aggiungi a PATH: `C:\Program Files\Tesseract-OCR`

**Linux:**
```bash
sudo apt install tesseract-ocr tesseract-ocr-ita
```

**Mac:**
```bash
brew install tesseract tesseract-lang
```

### ❌ Memoria RAM insufficiente

**Soluzione:**
Riduci chunk_size in `.env`:
```env
CHUNK_SIZE=1000
RETRIEVAL_K=3
```

### ❌ Costi API troppo alti

**Soluzione:**
1. Riduci temperatura: `LLM_TEMPERATURE=0.0`
2. Limita retrieval: `RETRIEVAL_K=3`
3. Usa modello più economico: `OPENAI_MODEL=gpt-3.5-turbo`
4. Abilita cache: `ENABLE_CACHE=true`

### 🐛 Debug Mode

Abilita logging dettagliato:

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

Poi controlla i log:
```bash
tail -f logs/officina_ai.log
```

---

## Comandi Utili

### Verifica Sistema

```bash
python src/utils.py
```

### Test Singolo Modulo

```bash
# Test processor
python src/document_processor.py

# Test vectorstore
python src/vectorstore.py

# Test chatbot
python src/qa_chain.py
```

### Pulizia

```bash
# Elimina cache
find . -type d -name __pycache__ -exec rm -rf {} +

# Elimina logs
rm -rf logs/*

# Elimina indice Pinecone
python -c "from src import VectorStoreManager; v = VectorStoreManager(); v.delete_all(confirm=True)"
```

---

## Prossimi Passi

1. ✅ Setup completato
2. ✅ Manuali indicizzati
3. ✅ App funzionante
4. 🔜 Aggiungi più manuali
5. 🔜 Personalizza UI
6. 🔜 Deploy in produzione

---

## 📞 Supporto

- 📖 [README principale](../README.md)
- 📚 [Esempi d'uso](./EXAMPLES.md)
- 🐛 [GitHub Issues](https://github.com/tuousername/officina-ai-assistant/issues)

---

**Buon lavoro! 🚀**