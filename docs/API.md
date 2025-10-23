# ?? API Documentation

REST API per Officina AI Assistant.

## Base URL

```
http://localhost:8000
```

## Autenticazione

Se `API_SECRET_KEY` è configurato nel file `.env`, tutte le richieste devono includere l'header:

```
X-API-Key: your-secret-key
```

---

## Endpoints

### ?? Root

```http
GET /
```

Informazioni base sull'API.

**Response:**
```json
{
  "message": "Officina AI Assistant API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

### ?? Health Check

```http
GET /health
```

Verifica stato del sistema.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "llm_provider": "anthropic",
  "memory_enabled": true
}
```

---

### ?? Query (Domanda)

```http
POST /query
```

Poni una domanda al chatbot.

**Request Body:**
```json
{
  "question": "Come si sostituisce l'olio motore?",
  "marca": "FIAT",
  "modello": "500",
  "anno": "2020",
  "return_sources": true
}
```

**Parameters:**

| Campo | Tipo | Required | Descrizione |
|-------|------|----------|-------------|
| `question` | string | ? | La domanda da porre |
| `marca` | string | ? | Filtro marca (es: "FIAT") |
| `modello` | string | ? | Filtro modello (es: "500") |
| `anno` | string | ? | Filtro anno (es: "2020") |
| `return_sources` | boolean | ? | Restituisci fonti (default: true) |

**Response:**
```json
{
  "answer": "Per sostituire l'olio motore della FIAT 500...",
  "sources": [
    {
      "index": 1,
      "marca": "FIAT",
      "modello": "500",
      "anno": "2020",
      "pagina": "45",
      "filename": "FIAT_500_2020_Manuale_Officina.pdf",
      "excerpt": "Procedura cambio olio..."
    }
  ]
}
```

---

### ??? Get Brands

```http
GET /brands
```

Ottieni lista marche disponibili.

**Response:**
```json
["BMW", "FIAT", "MERCEDES", "VW"]
```

---

### ?? Get Models

```http
GET /models/{brand}
```

Ottieni lista modelli per una marca.

**Parameters:**
- `brand` (path): Nome marca (es: "FIAT")

**Response:**
```json
["500", "Panda", "Punto", "Tipo"]
```

---

### ?? Clear Memory

```http
POST /clear_memory
```

Pulisci la memoria conversazionale.

**Response:**
```json
{
  "message": "Memoria pulita con successo"
}
```

---

### ?? Get History

```http
GET /history
```

Ottieni storico conversazione (se memoria abilitata).

**Response:**
```json
{
  "messages": [
    {
      "type": "human",
      "content": "Come cambio l'olio?"
    },
    {
      "type": "ai",
      "content": "Per cambiare l'olio..."
    }
  ]
}
```

---

## Esempi di Utilizzo

### Python

```python
import requests

# Configurazione
BASE_URL = "http://localhost:8000"
API_KEY = "your-secret-key"  # Se configurato

headers = {
    "X-API-Key": API_KEY
}

# Query semplice
response = requests.post(
    f"{BASE_URL}/query",
    headers=headers,
    json={
        "question": "Coppia di serraggio bulloni testata BMW 320d?"
    }
)

result = response.json()
print(result["answer"])

# Query con filtri
response = requests.post(
    f"{BASE_URL}/query",
    headers=headers,
    json={
        "question": "Capacità olio motore?",
        "marca": "FIAT",
        "modello": "500",
        "return_sources": True
    }
)

result = response.json()
print(f"Risposta: {result['answer']}\n")

if result.get("sources"):
    print("Fonti:")
    for source in result["sources"]:
        print(f"  - {source['marca']} {source['modello']} - Pagina {source['pagina']}")
```

### cURL

```bash
# Query semplice
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{
    "question": "Come cambio le pastiglie freni?",
    "return_sources": true
  }'

# Query con filtri
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{
    "question": "Procedura cambio olio",
    "marca": "VW",
    "modello": "Golf",
    "anno": "2019"
  }'

# Get brands
curl "http://localhost:8000/brands" \
  -H "X-API-Key: your-secret-key"
```

### JavaScript (Fetch)

```javascript
const BASE_URL = "http://localhost:8000";
const API_KEY = "your-secret-key";

// Query
async function askQuestion(question, filters = {}) {
  const response = await fetch(`${BASE_URL}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY
    },
    body: JSON.stringify({
      question: question,
      ...filters,
      return_sources: true
    })
  });
  
  const result = await response.json();
  return result;
}

// Uso
askQuestion("Come si cambia l'olio?", {
  marca: "FIAT",
  modello: "500"
}).then(result => {
  console.log("Risposta:", result.answer);
  console.log("Fonti:", result.sources);
});
```

### Node.js (Axios)

```javascript
const axios = require('axios');

const client = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'X-API-Key': 'your-secret-key'
  }
});

// Query
async function query(question, filters = {}) {
  try {
    const response = await client.post('/query', {
      question: question,
      ...filters,
      return_sources: true
    });
    
    return response.data;
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
    throw error;
  }
}

// Uso
(async () => {
  const result = await query("Coppia serraggio ruote?", {
    marca: "BMW",
    modello: "320d"
  });
  
  console.log(result.answer);
})();
```

---

## Error Handling

### Error Responses

**401 Unauthorized:**
```json
{
  "detail": "API Key non valida o mancante"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Errore elaborazione query: ..."
}
```

### Retry Logic

```python
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_session():
    session = requests.Session()
    
    retry = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=[500, 502, 503, 504]
    )
    
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    return session

# Uso
session = create_session()
response = session.post(
    "http://localhost:8000/query",
    json={"question": "..."}
)
```

---

## Rate Limiting

Attualmente non implementato, ma raccomandazioni:

- Max 60 richieste/minuto per client
- Per usi intensivi, considera il caching locale

---

## Streaming (Future)

Supporto per streaming in sviluppo:

```python
# Coming soon
import requests

response = requests.post(
    "http://localhost:8000/query/stream",
    json={"question": "..."},
    stream=True
)

for chunk in response.iter_content(chunk_size=None):
    print(chunk.decode(), end='', flush=True)
```

---

## Testing

### Test con Pytest

```python
import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_query():
    response = client.post(
        "/query",
        json={"question": "test question"}
    )
    assert response.status_code == 200
    assert "answer" in response.json()

def test_brands():
    response = client.get("/brands")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

---

## OpenAPI/Swagger

Documentazione interattiva disponibile su:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## Postman Collection

Importa questa collection in Postman:

```json
{
  "info": {
    "name": "Officina AI API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Query",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "X-API-Key",
            "value": "{{api_key}}",
            "type": "text"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"question\": \"Come cambio l'olio?\",\n  \"marca\": \"FIAT\",\n  \"return_sources\": true\n}",
          "options": {
            "raw": {
              "language": "json"
            }
          }
        },
        "url": {
          "raw": "{{base_url}}/query",
          "host": ["{{base_url}}"],
          "path": ["query"]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    },
    {
      "key": "api_key",
      "value": "your-secret-key"
    }
  ]
}
```

---

## Best Practices

1. **Sempre gestisci gli errori**
2. **Usa retry logic per richieste critiche**
3. **Implementa timeout (30s raccomandato)**
4. **Cache risposte comuni localmente**
5. **Monitora l'uso delle API**
6. **Usa HTTPS in produzione**

---

## ?? Supporto

- ?? [README](../README.md)
- ?? [Setup Guide](./SETUP.md)
- ?? [GitHub Issues](https://github.com/tuousername/officina-ai-assistant/issues)