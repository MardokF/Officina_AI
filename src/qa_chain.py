"""
Modulo per la gestione delle chain RAG e interazione con LLM
"""
import logging
from typing import Dict, List, Optional
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from config import settings, get_llm_config
from src.vectorstore import VectorStoreManager

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


class OfficinaChatbot:
    """Chatbot principale per officine meccaniche"""
    
    def __init__(self):
        self.vectorstore_manager = VectorStoreManager()
        self.llm = self._initialize_llm()
        self.memory = None
        self.qa_chain = None
        
        if settings.ENABLE_MEMORY:
            self._initialize_memory()
        
        self._initialize_chain()
    
    def _initialize_llm(self):
        """Inizializza il modello LLM"""
        try:
            llm_config = get_llm_config()
            logger.info(f"🤖 Inizializzazione LLM: {llm_config['provider']} - {llm_config['model']}")
            
            if llm_config['provider'] == "anthropic":
                llm = ChatAnthropic(
                    model=llm_config['model'],
                    anthropic_api_key=llm_config['api_key'],
                    temperature=llm_config['temperature'],
                    max_tokens=llm_config['max_tokens']
                )
            elif llm_config['provider'] == "openai":
                llm = ChatOpenAI(
                    model=llm_config['model'],
                    openai_api_key=llm_config['api_key'],
                    temperature=llm_config['temperature'],
                    max_tokens=llm_config['max_tokens']
                )
            else:
                raise ValueError(f"Provider non supportato: {llm_config['provider']}")
            
            logger.info("✅ LLM inizializzato")
            return llm
            
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione LLM: {e}")
            raise
    
    def _initialize_memory(self):
        """Inizializza la memoria conversazionale"""
        try:
            logger.info(f"🧠 Inizializzazione memoria: {settings.MEMORY_TYPE}")
            
            if settings.MEMORY_TYPE == "buffer":
                self.memory = ConversationBufferMemory(
                    memory_key="chat_history",
                    return_messages=True,
                    output_key="answer"
                )
            
            logger.info("✅ Memoria inizializzata")
            
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione memoria: {e}")
            self.memory = None
    
    def _initialize_chain(self):
        """Inizializza la chain RAG"""
        try:
            logger.info("⛓️  Inizializzazione RAG chain...")
            
            retriever = self.vectorstore_manager.get_retriever()
            
            prompt_template = PromptTemplate(
                template=settings.QA_PROMPT_TEMPLATE,
                input_variables=["context", "question"]
            )
            
            if self.memory:
                self.qa_chain = ConversationalRetrievalChain.from_llm(
                    llm=self.llm,
                    retriever=retriever,
                    memory=self.memory,
                    return_source_documents=True,
                    verbose=settings.DEBUG
                )
            else:
                self.qa_chain = RetrievalQA.from_chain_type(
                    llm=self.llm,
                    chain_type="stuff",
                    retriever=retriever,
                    return_source_documents=True,
                    chain_type_kwargs={"prompt": prompt_template},
                    verbose=settings.DEBUG
                )
            
            logger.info("✅ Chain inizializzata")
            
        except Exception as e:
            logger.error(f"❌ Errore inizializzazione chain: {e}")
            raise
    
    def ask(
        self,
        question: str,
        filters: Optional[Dict] = None,
        return_sources: bool = True
    ) -> Dict:
        """Poni una domanda al chatbot"""
        try:
            logger.info(f"💬 Domanda: {question}")
            
            if filters:
                logger.info(f"🔍 Filtri applicati: {filters}")
                search_kwargs = {"k": settings.RETRIEVAL_K, "filter": filters}
                retriever = self.vectorstore_manager.get_retriever(search_kwargs)
                
                if self.memory:
                    self.qa_chain.retriever = retriever
                else:
                    self.qa_chain = RetrievalQA.from_chain_type(
                        llm=self.llm,
                        chain_type="stuff",
                        retriever=retriever,
                        return_source_documents=True,
                        verbose=settings.DEBUG
                    )
            
            if self.memory:
                result = self.qa_chain({"question": question})
            else:
                result = self.qa_chain({"query": question})
            
            response = {
                "answer": result.get("answer", result.get("result", "")),
            }
            
            if return_sources and "source_documents" in result:
                response["sources"] = self._format_sources(result["source_documents"])
            
            logger.info(f"✅ Risposta generata ({len(response['answer'])} caratteri)")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Errore elaborazione domanda: {e}")
            return {
                "answer": "Mi dispiace, si è verificato un errore nell'elaborazione della tua domanda. Riprova.",
                "error": str(e)
            }
    
    def _format_sources(self, source_docs: List) -> List[Dict]:
        """Formatta i documenti sorgente per la risposta"""
        sources = []
        
        for i, doc in enumerate(source_docs):
            source = {
                "index": i + 1,
                "marca": doc.metadata.get("marca", "N/A"),
                "modello": doc.metadata.get("modello", "N/A"),
                "anno": doc.metadata.get("anno", "N/A"),
                "pagina": doc.metadata.get("page", "N/A"),
                "filename": doc.metadata.get("filename", "N/A"),
                "excerpt": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
            }
            sources.append(source)
        
        return sources
    
    def clear_memory(self):
        """Pulisce la memoria conversazionale"""
        if self.memory:
            self.memory.clear()
            logger.info("🧹 Memoria conversazionale pulita")
    
    def get_conversation_history(self) -> List:
        """Ottieni lo storico della conversazione"""
        if self.memory:
            return self.memory.chat_memory.messages
        return []


class SimpleChatbot:
    """Versione semplificata del chatbot senza memoria"""
    
    def __init__(self):
        self.vectorstore_manager = VectorStoreManager()
        self.llm = self._initialize_llm()
        self.retriever = self.vectorstore_manager.get_retriever()
    
    def _initialize_llm(self):
        """Inizializza LLM"""
        llm_config = get_llm_config()
        
        if llm_config['provider'] == "anthropic":
            return ChatAnthropic(
                model=llm_config['model'],
                anthropic_api_key=llm_config['api_key'],
                temperature=llm_config['temperature'],
                max_tokens=llm_config['max_tokens']
            )
        else:
            return ChatOpenAI(
                model=llm_config['model'],
                openai_api_key=llm_config['api_key'],
                temperature=llm_config['temperature'],
                max_tokens=llm_config['max_tokens']
            )
    
    def ask(self, question: str, filters: Optional[Dict] = None) -> str:
        """Versione semplice: restituisce solo la risposta"""
        try:
            if filters:
                docs = self.vectorstore_manager.search(question, filter_dict=filters)
            else:
                docs = self.vectorstore_manager.search(question)
            
            if not docs:
                return "Non ho trovato informazioni rilevanti nei manuali disponibili."
            
            context = "\n\n".join([doc.page_content for doc in docs])
            
            prompt = f"""{settings.SYSTEM_PROMPT}

Contesto dai manuali:
{context}

Domanda: {question}

Risposta:"""
            
            response = self.llm.invoke(prompt)
            
            return response.content
            
        except Exception as e:
            logger.error(f"❌ Errore: {e}")
            return f"Errore: {str(e)}"


def format_answer_with_sources(response: Dict) -> str:
    """Formatta risposta con fonti in modo leggibile"""
    output = f"{response['answer']}\n\n"
    
    if "sources" in response and response['sources']:
        output += "📚 **Fonti:**\n"
        for source in response['sources']:
            output += f"\n{source['index']}. **{source['marca']} {source['modello']}** "
            if source['anno'] != "N/A":
                output += f"({source['anno']}) "
            output += f"- Pagina {source['pagina']}\n"
            output += f"   _{source['filename']}_\n"
    
    return output