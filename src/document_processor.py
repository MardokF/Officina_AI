"""
Modulo per l'elaborazione e preprocessing dei manuali PDF
"""
import os
from pathlib import Path
from typing import List, Dict, Optional
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from tqdm import tqdm
import logging

from config import settings

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


class ManualProcessor:
    """Processa manuali PDF e li prepara per l'indicizzazione"""
    
    def __init__(self, manuals_dir: Optional[Path] = None):
        self.manuals_dir = manuals_dir or settings.MANUALS_PATH
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=settings.TEXT_SEPARATORS,
            length_function=len,
        )
    
    def extract_metadata_from_filename(self, filename: str) -> Dict[str, str]:
        """
        Estrae metadata dal nome del file
        Formato atteso: MARCA_MODELLO_ANNO_Tipo.pdf
        Es: FIAT_500_2020_Manuale_Officina.pdf
        """
        stem = Path(filename).stem
        parts = stem.split("_")
        
        metadata = {
            "filename": filename,
            "tipo": "officina"
        }
        
        if len(parts) >= 2:
            metadata["marca"] = parts[0].upper()
            metadata["modello"] = parts[1]
        
        if len(parts) >= 3 and parts[2].isdigit():
            metadata["anno"] = parts[2]
        
        if len(parts) >= 4:
            metadata["tipo"] = "_".join(parts[3:]).lower()
        
        return metadata
    
    def load_pdf(self, pdf_path: Path) -> List[Document]:
        """Carica un singolo PDF"""
        try:
            logger.info(f"Caricamento PDF: {pdf_path.name}")
            
            loader = PyPDFLoader(str(pdf_path))
            documents = loader.load()
            
            # Aggiungi metadata
            base_metadata = self.extract_metadata_from_filename(pdf_path.name)
            
            for doc in documents:
                doc.metadata.update(base_metadata)
                doc.metadata["file_path"] = str(pdf_path)
            
            logger.info(f"✅ Caricato {len(documents)} pagine da {pdf_path.name}")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Errore caricamento {pdf_path.name}: {e}")
            return []
    
    def load_pdf_with_ocr(self, pdf_path: Path) -> List[Document]:
        """
        Carica PDF usando OCR (per PDF scansionati)
        Richiede: pytesseract e pdf2image
        """
        try:
            from pdf2image import convert_from_path
            import pytesseract
            
            logger.info(f"Caricamento PDF con OCR: {pdf_path.name}")
            
            images = convert_from_path(str(pdf_path))
            documents = []
            
            base_metadata = self.extract_metadata_from_filename(pdf_path.name)
            base_metadata["file_path"] = str(pdf_path)
            base_metadata["ocr_processed"] = True
            
            for i, image in enumerate(tqdm(images, desc="OCR pagine")):
                text = pytesseract.image_to_string(image, lang=settings.OCR_LANGUAGE)
                
                if text.strip():  # Solo se c'è testo
                    doc = Document(
                        page_content=text,
                        metadata={
                            **base_metadata,
                            "page": i + 1,
                            "source": str(pdf_path)
                        }
                    )
                    documents.append(doc)
            
            logger.info(f"✅ Elaborato con OCR {len(documents)} pagine da {pdf_path.name}")
            return documents
            
        except ImportError:
            logger.warning("OCR non disponibile. Installa: pip install pdf2image pytesseract")
            return self.load_pdf(pdf_path)
        except Exception as e:
            logger.error(f"❌ Errore OCR {pdf_path.name}: {e}")
            return []
    
    def extract_tables(self, pdf_path: Path) -> List[Dict]:
        """
        Estrae tabelle dal PDF
        Richiede: tabula-py
        """
        if not settings.EXTRACT_TABLES:
            return []
        
        try:
            import tabula
            
            logger.info(f"Estrazione tabelle da: {pdf_path.name}")
            
            tables = tabula.read_pdf(
                str(pdf_path),
                pages='all',
                multiple_tables=True,
                silent=True
            )
            
            if tables:
                logger.info(f"✅ Estratte {len(tables)} tabelle da {pdf_path.name}")
            
            return tables
            
        except ImportError:
            logger.warning("Estrazione tabelle non disponibile. Installa: pip install tabula-py")
            return []
        except Exception as e:
            logger.warning(f"Impossibile estrarre tabelle da {pdf_path.name}: {e}")
            return []
    
    def process_all_manuals(self, use_ocr: bool = None) -> List[Document]:
        """
        Processa tutti i manuali nella directory
        
        Args:
            use_ocr: Se True usa OCR, se False usa estrazione testo normale,
                    se None decide automaticamente
        """
        if use_ocr is None:
            use_ocr = settings.ENABLE_OCR
        
        all_documents = []
        pdf_files = list(self.manuals_dir.glob("**/*.pdf"))
        
        if not pdf_files:
            logger.warning(f"⚠️  Nessun PDF trovato in {self.manuals_dir}")
            logger.info(f"💡 Aggiungi i tuoi manuali in: {self.manuals_dir}")
            return []
        
        logger.info(f"\n📚 Trovati {len(pdf_files)} manuali da processare\n")
        
        for pdf_path in pdf_files:
            # Prova prima estrazione normale
            docs = self.load_pdf(pdf_path)
            
            # Se OCR è abilitato e il testo estratto è scarso, usa OCR
            if use_ocr and docs:
                avg_length = sum(len(doc.page_content) for doc in docs) / len(docs)
                if avg_length < 100:  # Testo troppo scarso, probabilmente scansionato
                    logger.info(f"📄 PDF scansionato rilevato, uso OCR...")
                    docs = self.load_pdf_with_ocr(pdf_path)
            
            all_documents.extend(docs)
            
            # Estrai tabelle (opzionale)
            if settings.EXTRACT_TABLES:
                tables = self.extract_tables(pdf_path)
                # TODO: Converti tabelle in Documents e aggiungi
        
        logger.info(f"\n✅ Totale documenti caricati: {len(all_documents)}")
        return all_documents
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Divide i documenti in chunks"""
        logger.info(f"🔪 Suddivisione documenti in chunks...")
        
        chunks = self.text_splitter.split_documents(documents)
        
        logger.info(f"✅ Creati {len(chunks)} chunks (dimensione media: {settings.CHUNK_SIZE} caratteri)")
        return chunks
    
    def process_and_split(self, use_ocr: bool = None) -> List[Document]:
        """Pipeline completa: carica e divide tutti i manuali"""
        documents = self.process_all_manuals(use_ocr=use_ocr)
        
        if not documents:
            return []
        
        chunks = self.split_documents(documents)
        return chunks
    
    def get_manual_stats(self) -> Dict:
        """Ottieni statistiche sui manuali disponibili"""
        pdf_files = list(self.manuals_dir.glob("**/*.pdf"))
        
        stats = {
            "total_manuals": len(pdf_files),
            "by_brand": {},
            "files": []
        }
        
        for pdf_path in pdf_files:
            metadata = self.extract_metadata_from_filename(pdf_path.name)
            marca = metadata.get("marca", "UNKNOWN")
            
            if marca not in stats["by_brand"]:
                stats["by_brand"][marca] = 0
            stats["by_brand"][marca] += 1
            
            stats["files"].append({
                "name": pdf_path.name,
                "size_mb": pdf_path.stat().st_size / (1024 * 1024),
                "metadata": metadata
            })
        
        return stats


# Utility functions
def preview_chunks(chunks: List[Document], n: int = 3):
    """Visualizza un'anteprima dei primi n chunks"""
    print(f"\n{'='*80}")
    print(f"ANTEPRIMA CHUNKS (primi {n})")
    print(f"{'='*80}\n")
    
    for i, chunk in enumerate(chunks[:n]):
        print(f"--- Chunk {i+1} ---")
        print(f"Marca: {chunk.metadata.get('marca', 'N/A')}")
        print(f"Modello: {chunk.metadata.get('modello', 'N/A')}")
        print(f"Pagina: {chunk.metadata.get('page', 'N/A')}")
        print(f"\nContenuto (primi 300 caratteri):")
        print(chunk.page_content[:300])
        print(f"\n{'='*80}\n")


if __name__ == "__main__":
    # Test del processor
    processor = ManualProcessor()
    
    # Mostra statistiche
    stats = processor.get_manual_stats()
    print(f"\n📊 STATISTICHE MANUALI")
    print(f"{'='*50}")
    print(f"Totale manuali: {stats['total_manuals']}")
    print(f"\nPer marca:")
    for marca, count in stats['by_brand'].items():
        print(f"  - {marca}: {count} manuali")
    
    # Processa manuali
    if stats['total_manuals'] > 0:
        print(f"\n🚀 Inizio elaborazione...")
        chunks = processor.process_and_split()
        
        if chunks:
            preview_chunks(chunks, n=2)
    else:
        print(f"\n💡 Aggiungi i tuoi manuali PDF in: {settings.MANUALS_PATH}")