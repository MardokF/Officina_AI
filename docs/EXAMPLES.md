# 📚 Esempi d'Uso

Esempi pratici di utilizzo di Officina AI Assistant.

## Indice

1. [Esempi Streamlit UI](#streamlit-ui)
2. [Esempi API REST](#api-rest)
3. [Esempi Python SDK](#python-sdk)
4. [Casi d'Uso Reali](#casi-duso-reali)

---

## Streamlit UI

### Esempio 1: Domanda Semplice

**Domanda:** "Come si sostituisce l'olio motore?"

**Risposta:**
```
Per sostituire l'olio motore:

1. Riscalda il motore per 5-10 minuti
2. Solleva il veicolo e metti in sicurezza
3. Posiziona una bacinella sotto il tappo di scarico
4. Rimuovi il tappo e lascia defluire l'olio
5. Sostituisci la guarnizione del tappo
6. Riavvita il tappo con coppia 25-30 Nm
7. Sostituisci il filtro olio
8. Riempi con olio nuovo (vedi specifiche)
9. Verifica livello con l'asta
10. Avvia il motore e controlla perdite

📚 Fonti:
1. FIAT 500 (2020) - Pagina 45
   FIAT_500_2020_Manuale_Officina.pdf
```

### Esempio 2: Con Filtri

**Filtri:**
- Marca: FIAT
- Modello: 500
- Anno: 2020

**Domanda:** "Capacità olio motore?"

**Risposta:**
```
La capacità dell'olio motore per FIAT 500 2020 è:

• Con filtro: 3.5 litri
• Senza filtro: 3.2 litri

Specifiche olio raccomandate:
• Tipo: 5W-40 o 10W-40
• Standard: ACEA A3/B3 o superiore
• Gradazione inverno: 5W-30 (temperature sotto -15°C)

📚 Fonti:
1. FIAT 500 (2020) - Pagina 28
```

---

## API REST

### Esempio 1: Query Base

```python
import requests

url = "http://localhost:8000/query"
headers = {"Content-Type": "application/json"}

payload = {
    "question": "Coppia di serraggio bulloni ruota?",
    "return_sources": True
}

response = requests.post(url, headers=headers, json=payload)
result = response.json()

print(f"Risposta: {result['answer']}")
```

**Output:**
```
Risposta: La coppia di serraggio per i bulloni delle ruote è generalmente:
- Cerchi in lega: 110 Nm
- Cerchi in acciaio: 120 Nm

Sequenza di serraggio: a croce, in due fasi (50% poi 100% della coppia).
```

### Esempio 2: Query con Filtri

```python
payload = {
    "question": "Procedura reset service?",
    "marca": "BMW",
    "modello": "320d",
    "anno": "2021",
    "return_sources": True
}

response = requests.post(url, headers=headers, json=payload)
result = response.json()

# Mostra risposta e fonti
print(result['answer'])
for source in result['sources']:
    print(f"Fonte: {source['filename']} - Pag. {source['pagina']}")
```

### Esempio 3: Ottenere Marche Disponibili

```python
# Get lista marche
brands_response = requests.get("http://localhost:8000/brands")
brands = brands_response.json()
print(f"Marche disponibili: {brands}")

# Get modelli per una marca
models_response = requests.get("http://localhost:8000/models/FIAT")
models = models_response.json()
print(f"Modelli FIAT: {models}")
```

---

## Python SDK

### Esempio 1: Uso Base

```python
from src import OfficinaChatbot

# Inizializza chatbot
chatbot = OfficinaChatbot()

# Fai una domanda
response = chatbot.ask(
    question="Come si cambiano le pastiglie freni?",
    return_sources=True
)

print(response['answer'])
```

### Esempio 2: Con Filtri

```python
response = chatbot.ask(
    question="Specifiche candele?",
    filters={
        "marca": "VW",
        "modello": "Golf",
        "anno": "2019"
    }
)

print(response['answer'])

# Mostra fonti
for source in response.get('sources', []):
    print(f"\n{source['marca']} {source['modello']} - Pag. {source['pagina']}")
    print(f"Excerpt: {source['excerpt'][:100]}...")
```

### Esempio 3: Conversazione Multi-Turn

```python
from src import OfficinaChatbot

chatbot = OfficinaChatbot()

# Prima domanda
r1 = chatbot.ask("Come cambio l'olio della Golf?")
print(f"AI: {r1['answer']}\n")

# Follow-up (usa memoria conversazionale)
r2 = chatbot.ask("Quanto olio serve?")  # "serve" si riferisce alla Golf
print(f"AI: {r2['answer']}\n")

# Altra follow-up
r3 = chatbot.ask("E che tipo di olio devo usare?")
print(f"AI: {r3['answer']}\n")

# Pulisci memoria
chatbot.clear_memory()
```

### Esempio 4: Batch Processing

```python
questions = [
    ("Coppia bulloni testata?", {"marca": "FIAT"}),
    ("Pressione gomme?", {"marca": "BMW"}),
    ("Capacità radiatore?", {"marca": "VW"}),
]

results = []
for question, filters in questions:
    response = chatbot.ask(question, filters=filters)
    results.append({
        "question": question,
        "answer": response['answer'],
        "brand": filters.get('marca')
    })

# Esporta risultati
import json
with open("results.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
```

---

## Casi d'Uso Reali

### Caso 1: Assistente per Meccanico

**Scenario:** Un meccanico deve cambiare le pastiglie freni di una FIAT 500 ma non ricorda la procedura esatta.

```python
response = chatbot.ask(
    question="Procedura completa cambio pastiglie freni anteriori",
    filters={"marca": "FIAT", "modello": "500"}
)
```

**Risultato:**
```
Procedura cambio pastiglie freni anteriori FIAT 500:

1. PREPARAZIONE
   - Solleva veicolo
   - Rimuovi ruota
   - Pulisci zona pinza

2. RIMOZIONE
   - Rimuovi perni pinza (chiave 13mm)
   - Solleva pinza (non scollegare tubo freno)
   - Rimuovi pastiglie vecchie
   - Pulisci sede pastiglie

3. INSTALLAZIONE
   - Comprimi pistone con apposito attrezzo
   - Inserisci pastiglie nuove
   - Riposiziona pinza
   - Installa perni (coppia 25 Nm)

4. CONTROLLO
   - Pompa pedale freno 2-3 volte
   - Verifica livello liquido freni
   - Test su strada

⚠️ AVVERTENZE:
- Non comprimere pistone senza aprire serbatoio
- Sostituisci sempre entrambi i lati
- Verifica spessore disco (min 9mm)
```

### Caso 2: Call Center Ricambi

**Scenario:** Cliente chiama per sapere quale olio comprare.

```python
# Sistema automatico riceve: marca=BMW, modello=320d, anno=2021
response = chatbot.ask(
    question="Che olio motore devo comprare?",
    filters={"marca": "BMW", "modello": "320d", "anno": "2021"}
)
```

**Risultato:**
```
Per BMW 320d 2021:

Specifiche Olio Motore:
• Tipo: 5W-30
• Standard BMW: Longlife-04 (LL-04)
• Capacità: 5.2 litri (con filtro)
• Intervallo cambio: 30.000 km o 2 anni

Oli Raccomandati:
1. BMW Original 5W-30 LL-04
2. Castrol EDGE Professional LL-04 5W-30
3. Mobil 1 ESP 5W-30
4. Shell Helix Ultra Professional AV-L 5W-30

⚠️ IMPORTANTE: Usa SOLO oli con specifica LL-04
```

### Caso 3: Formazione Apprendisti

**Scenario:** Apprendista meccanico sta imparando.

```python
# Lezione 1: Cambio olio
questions = [
    "Perché è importante cambiare l'olio?",
    "Ogni quanto va cambiato?",
    "Come si verifica il livello?",
    "Cosa succede se l'olio è troppo vecchio?"
]

for q in questions:
    response = chatbot.ask(q)
    print(f"\nQ: {q}")
    print(f"A: {response['answer']}\n")
    print("-" * 80)
```

### Caso 4: Diagnosi Errori

**Scenario:** Auto ha spia motore accesa, codice errore P0420.

```python
response = chatbot.ask(
    question="Cosa significa codice errore P0420 e come si risolve?",
    filters={"marca": "VW"}
)
```

**Risultato:**
```
Codice Errore P0420: "Catalyst System Efficiency Below Threshold"

SIGNIFICATO:
Il catalizzatore non funziona efficientemente come dovrebbe.

CAUSE POSSIBILI:
1. Catalizzatore deteriorato/guasto (più comune)
2. Sensori O2 difettosi
3. Perdite nel sistema scarico
4. Problema nel sistema alimentazione
5. Olio motore deteriorato

DIAGNOSI:
1. Verifica con scan tool dati sensori O2
2. Controllo visivo catalizzatore (danneggiamenti)
3. Test pressione/contropressione scarico
4. Verifica perdite aria sistema

RISOLUZIONE:
- Se catalizzatore guasto → Sostituzione (parte OEM: 18D-131-702-B)
- Costo: €450-800 + manodopera
- Tempo: 2-3 ore

⚠️ Non ignorare: può causare danni ulteriori
```

### Caso 5: Preventivo Rapido

**Scenario:** Cliente chiede preventivo cambio distribuzione.

```python
response = chatbot.ask(
    question="Cosa include servizio cambio cinghia distribuzione e ogni quanto va fatto?",
    filters={"marca": "FIAT", "modello": "Panda", "anno": "2018"}
)
```

**Risultato:**
```
SERVIZIO CINGHIA DISTRIBUZIONE - FIAT Panda 2018

INTERVALLO:
• Ogni 120.000 km
• Ogni 6 anni (quello che arriva prima)

COSA INCLUDE:
✓ Cinghia distribuzione
✓ Tenditore automatico
✓ Rullo tenditore
✓ Pompa acqua (raccomandata)
✓ Cinghia servizi (se consumata)
✓ Guarnizioni/sigillanti

PROCEDURA:
- Tempo stimato: 4-5 ore
- Richiede attrezzi speciali calettamento
- Verifica giochi alberi

PARTI NECESSARIE:
1. Kit distribuzione completo (cod. 71754919)
2. Pompa acqua (cod. 46842804)
3. Antigelo (1.5L)

⚠️ CRITICO: Non superare km/anni indicati!
Rottura cinghia = danno motore grave (€2000-4000)
```

---

## Script Automation

### Script 1: Report Giornaliero

```python
#!/usr/bin/env python3
"""
Genera report delle query giornaliere
"""
import json
from datetime import datetime
from pathlib import Path

# Leggi log queries
log_file = Path("logs/queries/query_log.jsonl")
queries_today = []

with open(log_file) as f:
    for line in f:
        entry = json.loads(line)
        if datetime.fromisoformat(entry['timestamp']).date() == datetime.now().date():
            queries_today.append(entry)

# Statistiche
print(f"REPORT QUERIES - {datetime.now().date()}")
print(f"{'='*50}")
print(f"Totale queries: {len(queries_today)}")
print(f"Media lunghezza risposta: {sum(q['answer_length'] for q in queries_today) / len(queries_today):.0f} caratteri")
print(f"Queries con fonti: {sum(1 for q in queries_today if q['sources_count'] > 0)}")
```

### Script 2: Indicizzazione Automatica

```bash
#!/bin/bash
# auto_index.sh - Monitora cartella manuali e indicizza automaticamente

MANUALS_DIR="./data/manuali"
LAST_CHECK_FILE=".last_check"

# Calcola hash directory
current_hash=$(find "$MANUALS_DIR" -type f -exec md5sum {} \; | md5sum | cut -d' ' -f1)

# Confronta con ultimo check
if [ ! -f "$LAST_CHECK_FILE" ] || [ "$(cat $LAST_CHECK_FILE)" != "$current_hash" ]; then
    echo "Nuovi manuali rilevati, inizio indicizzazione..."
    python scripts/index_manuals.py
    echo "$current_hash" > "$LAST_CHECK_FILE"
else
    echo "Nessun cambiamento rilevato"
fi
```

---

## Integrazioni

### Telegram Bot

```python
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from src import OfficinaChatbot

chatbot = OfficinaChatbot()

def ask(update: Update, context):
    question = update.message.text
    response = chatbot.ask(question)
    update.message.reply_text(response['answer'])

updater = Updater("YOUR_BOT_TOKEN")
updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, ask))
updater.start_polling()
```

### WhatsApp (Twilio)

```python
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from src import OfficinaChatbot

app = Flask(__name__)
chatbot = OfficinaChatbot()

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    question = request.form.get('Body')
    response = chatbot.ask(question)
    
    resp = MessagingResponse()
    resp.message(response['answer'])
    
    return str(resp)
```

---

## 💡 Tips & Tricks

### Migliora le Risposte

**Domande specifiche danno risposte migliori:**

❌ Cattivo: "cambio olio"
✅ Buono: "Come si cambia l'olio motore della FIAT 500?"

**Usa filtri quando possibile:**

```python
response = chatbot.ask(
    "capacità serbatoio",
    filters={"marca": "BMW", "modello": "320d"}
)
```

### Performance

**Cache risposte comuni:**

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def ask_cached(question, marca=None):
    return chatbot.ask(question, filters={"marca": marca} if marca else None)
```

---

## 📞 Prossimi Passi

- Vedi [Setup Guide](./SETUP.md) per installazione
- Vedi [API Docs](./API.md) per documentazione completa API
- Apri un [Issue](https://github.com/tuousername/officina-ai-assistant/issues) per domande