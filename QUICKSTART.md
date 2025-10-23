# ? Quick Start

Inizia in 5 minuti con Officina AI Assistant!

## ?? Setup Rapido

### 1. Clone & Install

```bash
git clone https://github.com/tuousername/officina-ai-assistant.git
cd officina-ai-assistant
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configura API Keys

```bash
cp .env.example .env
nano .env  # Modifica con le tue API keys
```

**Minimo richiesto:**
```env
ANTHROPIC_API_KEY=sk-ant-api-...
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=gcp-starter
```

### 3. Aggiungi Manuali

```bash
# Crea directory
mkdir -p data/manuali

# Copia i tuoi PDF (formato: MARCA_MODELLO_ANNO_Tipo.pdf)
cp ~/Downloads/FIAT_500_2020_Manuale.pdf data/manuali/
```

### 4. Indicizza

```bash
python scripts/index_manuals.py
```

### 5. Avvia!

```bash
# Interfaccia web
streamlit run app.py

# Oppure API
uvicorn api:app --reload

# Oppure test
python scripts/test_queries.py -i
```

## ?? Primo Test

Apri `http://localhost:8501` e prova:

```
? "Come si sostituisce l'olio motore?"
```

## ?? Next Steps

- ? [Setup Completo](docs/SETUP.md) - Guida dettagliata
- ?? [API Docs](docs/API.md) - Documentazione API
- ?? [Examples](docs/EXAMPLES.md) - Esempi pratici

## ?? Problemi?

```bash
# Verifica sistema
python src/utils.py

# Check configurazione
python -c "from config import validate_settings; validate_settings()"
```

## ?? Pro Tips

1. **Usa filtri** per risultati migliori
2. **Nomi file corretti**: `MARCA_MODELLO_ANNO.pdf`
3. **OCR per PDF scansionati**: `--ocr` flag
4. **Test prima**: `python scripts/test_queries.py`

**Buon lavoro! ??**