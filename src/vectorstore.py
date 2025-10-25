"""
Modulo per la gestione del vector database (Pinecone)
"""
import logging
from typing import List, Dict, Optional
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
import time

from config import settings

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Gestisce il vector database Pinecone"""
    
    def __init__(self):
        self.pc = None
        self.index = None
        self.embeddings = None
        self.vectorstore = None
        
        self._initialize()
    
    def _initialize(self):
        """Inizializza connessione a Pinecone"""
        try:
            logger.info("🔌 Connessione a Pinecone...")
            
            # Inizializza client Pinecone
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            
            # Inizializza embeddings con modello locale
            self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.OPENAI_API_KEY
            )
            
            logger.info("✅ Connessione stabilita")
            
        except Exception as e:
            logger.error(f"❌ Errore connessione Pinecone: {e}")
            raise
    
    def create_index_if_not_exists(self, dimension: int = 1536):
        """
        Crea l'indice Pinecone se non esiste
        
        Args:
            dimension: Dimensione dei vettori (1536 per OpenAI ada-002)
        """
        try:
            index_name = settings.PINECONE_INDEX_NAME
            
            # Controlla se l'indice esiste già
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if index_name in existing_indexes:
                logger.info(f"📊 Indice '{index_name}' già esistente")
                self.index = self.pc.Index(index_name)
                return
            
            logger.info(f"🆕 Creazione nuovo indice '{index_name}'...")
            
            # Determina il cloud e region dal PINECONE_ENVIRONMENT
            env = settings.PINECONE_ENVIRONMENT
            if 'aws' in env:
                cloud = 'aws'
                region = env.replace('-aws', '')
            elif 'gcp' in env:
                cloud = 'gcp'
                region = env.replace('-gcp', '')
            else:
                # Default
                cloud = 'aws'
                region = 'us-east-1'
            
            # Crea l'indice
            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=cloud,
                    region=region
                )
            )
            
            # Aspetta che l'indice sia pronto
            logger.info("⏳ Attendo che l'indice sia pronto...")
            while not self.pc.describe_index(index_name).status['ready']:
                time.sleep(1)
            
            self.index = self.pc.Index(index_name)
            logger.info(f"✅ Indice '{index_name}' creato con successo")
            
        except Exception as e:
            logger.error(f"❌ Errore creazione indice: {e}")
            raise
    
    def index_documents(self, documents: List[Document], batch_size: int = 100):
        """
        Indicizza documenti nel vector store
        
        Args:
            documents: Lista di documenti da indicizzare
            batch_size: Dimensione batch per l'indicizzazione
        """
        if not documents:
            logger.warning("⚠️  Nessun documento da indicizzare")
            return
        
        try:
            logger.info(f"📝 Inizio indicizzazione di {len(documents)} documenti...")
            
            # Crea l'indice se non esiste
            self.create_index_if_not_exists()
            
            # Crea vectorstore usando LangChain
            self.vectorstore = PineconeVectorStore.from_documents(
                documents=documents,
                embedding=self.embeddings,
                index_name=settings.PINECONE_INDEX_NAME
            )
            
            logger.info(f"✅ Indicizzazione completata!")
            
            # Mostra statistiche
            stats = self.get_index_stats()
            logger.info(f"📊 Statistiche indice: {stats.get('total_vector_count', 0)} vettori totali")
            
        except Exception as e:
            logger.error(f"❌ Errore indicizzazione: {e}")
            raise
    
    def get_vectorstore(self) -> PineconeVectorStore:
        """Ottieni il vectorstore (crea connessione se necessario)"""
        if self.vectorstore is None:
            try:
                logger.info("🔌 Connessione al vectorstore esistente...")
                
                self.vectorstore = PineconeVectorStore(
                    index_name=settings.PINECONE_INDEX_NAME,
                    embedding=self.embeddings
                )
                
                logger.info("✅ Connesso al vectorstore")
                
            except Exception as e:
                logger.error(f"❌ Errore connessione vectorstore: {e}")
                raise
        
        return self.vectorstore
    
    def search(
        self,
        query: str,
        k: int = None,
        filter_dict: Optional[Dict] = None
    ) -> List[Document]:
        """
        Cerca documenti simili alla query
        
        Args:
            query: Query di ricerca
            k: Numero di risultati da restituire
            filter_dict: Filtri metadata (es: {"marca": "FIAT"})
        
        Returns:
            Lista di documenti rilevanti
        """
        if k is None:
            k = settings.RETRIEVAL_K
        
        try:
            vectorstore = self.get_vectorstore()
            
            if filter_dict:
                results = vectorstore.similarity_search(query, k=k, filter=filter_dict)
            else:
                results = vectorstore.similarity_search(query, k=k)
            
            logger.info(f"🔍 Trovati {len(results)} risultati per: '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"❌ Errore ricerca: {e}")
            return []
    
    def search_with_score(
        self,
        query: str,
        k: int = None,
        filter_dict: Optional[Dict] = None
    ) -> List[tuple]:
        """
        Cerca documenti con score di similarità
        
        Returns:
            Lista di tuple (Document, score)
        """
        if k is None:
            k = settings.RETRIEVAL_K
        
        try:
            vectorstore = self.get_vectorstore()
            
            if filter_dict:
                results = vectorstore.similarity_search_with_score(query, k=k, filter=filter_dict)
            else:
                results = vectorstore.similarity_search_with_score(query, k=k)
            
            # Filtra per threshold
            filtered_results = [
                (doc, score) for doc, score in results
                if score >= settings.SIMILARITY_THRESHOLD
            ]
            
            logger.info(
                f"🔍 Trovati {len(filtered_results)}/{len(results)} risultati "
                f"sopra threshold {settings.SIMILARITY_THRESHOLD}"
            )
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"❌ Errore ricerca con score: {e}")
            return []
    
    def get_index_stats(self) -> Dict:
        """Ottieni statistiche sull'indice"""
        try:
            if self.index is None:
                self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
            
            stats = self.index.describe_index_stats()
            return stats
            
        except Exception as e:
            logger.error(f"❌ Errore recupero statistiche: {e}")
            return {}
    
    def delete_all(self, confirm: bool = False):
        """
        Elimina tutti i vettori dall'indice
        
        Args:
            confirm: Deve essere True per confermare l'eliminazione
        """
        if not confirm:
            logger.warning("⚠️  Eliminazione annullata. Passa confirm=True per confermare.")
            return
        
        try:
            logger.warning("🗑️  Eliminazione di tutti i vettori...")
            
            if self.index is None:
                self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
            
            self.index.delete(delete_all=True)
            logger.info("✅ Tutti i vettori eliminati")
            
        except Exception as e:
            logger.error(f"❌ Errore eliminazione: {e}")
            raise
    
    def delete_by_filter(self, filter_dict: Dict, confirm: bool = False):
        """
        Elimina vettori per filtro metadata
        
        Args:
            filter_dict: Filtro (es: {"marca": "FIAT"})
            confirm: Deve essere True per confermare
        """
        if not confirm:
            logger.warning("⚠️  Eliminazione annullata. Passa confirm=True per confermare.")
            return
        
        try:
            logger.info(f"🗑️  Eliminazione vettori con filtro: {filter_dict}")
            
            if self.index is None:
                self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
            
            self.index.delete(filter=filter_dict)
            logger.info("✅ Vettori eliminati")
            
        except Exception as e:
            logger.error(f"❌ Errore eliminazione: {e}")
            raise
    
    def get_retriever(self, search_kwargs: Optional[Dict] = None):
        """
        Ottieni un retriever configurato per LangChain
        
        Args:
            search_kwargs: Parametri di ricerca personalizzati
        """
        vectorstore = self.get_vectorstore()
        
        if search_kwargs is None:
            search_kwargs = {"k": settings.RETRIEVAL_K}
        
        return vectorstore.as_retriever(search_kwargs=search_kwargs)


def display_search_results(results: List[tuple], max_content_length: int = 200):
    """Utility per visualizzare risultati ricerca"""
    print(f"\n{'='*80}")
    print(f"RISULTATI RICERCA ({len(results)} documenti)")
    print(f"{'='*80}\n")
    
    for i, (doc, score) in enumerate(results, 1):
        print(f"--- Risultato {i} (Score: {score:.3f}) ---")
        print(f"Marca: {doc.metadata.get('marca', 'N/A')}")
        print(f"Modello: {doc.metadata.get('modello', 'N/A')}")
        print(f"Anno: {doc.metadata.get('anno', 'N/A')}")
        print(f"Pagina: {doc.metadata.get('page', 'N/A')}")
        print(f"\nContenuto:")
        content = doc.page_content[:max_content_length]
        print(content + ("..." if len(doc.page_content) > max_content_length else ""))
        print(f"\n{'='*80}\n")


if __name__ == "__main__":
    # Test del vector store
    manager = VectorStoreManager()
    
    # Mostra statistiche
    stats = manager.get_index_stats()
    print(f"\n📊 STATISTICHE VECTOR STORE")
    print(f"{'='*50}")
    print(f"Indice: {settings.PINECONE_INDEX_NAME}")
    print(f"Vettori totali: {stats.get('total_vector_count', 0)}")
    print(f"Dimensione: {stats.get('dimension', 'N/A')}")