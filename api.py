"""
Officina AI Assistant - REST API
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import logging

from src import OfficinaChatbot
from src.utils import save_query_log
from config import settings, validate_settings

# Setup logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Inizializza FastAPI
app = FastAPI(
    title="Officina AI Assistant API",
    description="API REST per assistente AI officine meccaniche",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chatbot globale (inizializzato all'avvio)
chatbot: Optional[OfficinaChatbot] = None


# Models
class QueryRequest(BaseModel):
    """Richiesta query"""
    question: str = Field(..., description="La domanda da porre", min_length=1)
    marca: Optional[str] = Field(None, description="Filtro marca auto")
    modello: Optional[str] = Field(None, description="Filtro modello auto")
    anno: Optional[str] = Field(None, description="Filtro anno auto")
    return_sources: bool = Field(True, description="Restituisci documenti sorgente")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Come si sostituisce l'olio motore?",
                "marca": "FIAT",
                "modello": "500",
                "anno": "2020",
                "return_sources": True
            }
        }


class Source(BaseModel):
    """Documento sorgente"""
    index: int
    marca: str
    modello: str
    anno: str
    pagina: str
    filename: str
    excerpt: str


class QueryResponse(BaseModel):
    """Risposta query"""
    answer: str = Field(..., description="Risposta alla domanda")
    sources: Optional[List[Source]] = Field(None, description="Documenti sorgente")
    
    class Config:
        json_schema_extra = {
            "example": {
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
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    llm_provider: str
    memory_enabled: bool


class ErrorResponse(BaseModel):
    """Risposta errore"""
    detail: str


# Dependency per API key (se configurata)
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verifica API key se configurata"""
    if settings.API_SECRET_KEY:
        if not x_api_key or x_api_key != settings.API_SECRET_KEY:
            raise HTTPException(
                status_code=401,
                detail="API Key non valida o mancante"
            )
    return True


# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    """Inizializza il chatbot all'avvio"""
    global chatbot
    
    try:
        logger.info("🚀 Inizializzazione Officina AI API...")
        
        # Valida configurazione
        validate_settings()
        
        # Inizializza chatbot
        chatbot = OfficinaChatbot()
        
        logger.info("✅ API pronta!")
        
    except Exception as e:
        logger.error(f"❌ Errore inizializzazione: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup alla chiusura"""
    logger.info("👋 Shutdown API...")


# Endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Officina AI Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"]
)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if chatbot else "unhealthy",
        "version": "1.0.0",
        "llm_provider": settings.LLM_PROVIDER,
        "memory_enabled": settings.ENABLE_MEMORY
    }


@app.post(
    "/query",
    response_model=QueryResponse,
    responses={
        401: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    tags=["Query"],
    dependencies=[Depends(verify_api_key)]
)
async def query(request: QueryRequest):
    """
    Poni una domanda al chatbot
    
    - **question**: La domanda da porre
    - **marca**: Filtro opzionale per marca auto
    - **modello**: Filtro opzionale per modello auto
    - **anno**: Filtro opzionale per anno auto
    - **return_sources**: Se restituire i documenti sorgente
    """
    if not chatbot:
        raise HTTPException(
            status_code=500,
            detail="Chatbot non inizializzato"
        )
    
    try:
        # Prepara filtri
        filters = {}
        if request.marca:
            filters["marca"] = request.marca.upper()
        if request.modello:
            filters["modello"] = request.modello
        if request.anno:
            filters["anno"] = request.anno
        
        # Esegui query
        response = chatbot.ask(
            question=request.question,
            filters=filters if filters else None,
            return_sources=request.return_sources
        )
        
        # Log query
        save_query_log(
            request.question,
            response.get("answer", ""),
            response.get("sources", [])
        )
        
        # Formatta risposta
        result = {
            "answer": response.get("answer", ""),
        }
        
        if request.return_sources and "sources" in response:
            result["sources"] = [
                Source(**source) for source in response["sources"]
            ]
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Errore query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Errore elaborazione query: {str(e)}"
        )


@app.get(
    "/brands",
    response_model=List[str],
    tags=["Filters"],
    dependencies=[Depends(verify_api_key)]
)
async def get_brands():
    """Ottieni lista marche disponibili"""
    from src.utils import get_available_brands
    return get_available_brands()


@app.get(
    "/models/{brand}",
    response_model=List[str],
    tags=["Filters"],
    dependencies=[Depends(verify_api_key)]
)
async def get_models(brand: str):
    """Ottieni lista modelli disponibili per una marca"""
    from src.utils import get_available_models
    return get_available_models(brand)


@app.post(
    "/clear_memory",
    tags=["Memory"],
    dependencies=[Depends(verify_api_key)]
)
async def clear_memory():
    """Pulisci la memoria conversazionale"""
    if not chatbot:
        raise HTTPException(
            status_code=500,
            detail="Chatbot non inizializzato"
        )
    
    if not settings.ENABLE_MEMORY:
        raise HTTPException(
            status_code=400,
            detail="Memoria non abilitata"
        )
    
    chatbot.clear_memory()
    return {"message": "Memoria pulita con successo"}


@app.get(
    "/history",
    tags=["Memory"],
    dependencies=[Depends(verify_api_key)]
)
async def get_history():
    """Ottieni storico conversazione"""
    if not chatbot:
        raise HTTPException(
            status_code=500,
            detail="Chatbot non inizializzato"
        )
    
    if not settings.ENABLE_MEMORY:
        raise HTTPException(
            status_code=400,
            detail="Memoria non abilitata"
        )
    
    history = chatbot.get_conversation_history()
    return {
        "messages": [
            {
                "type": msg.type,
                "content": msg.content
            }
            for msg in history
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )