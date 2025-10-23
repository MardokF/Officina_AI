#!/usr/bin/env python3
"""
Script per indicizzare i manuali PDF nel vector database
"""
import sys
import argparse
from pathlib import Path

# Aggiungi la root al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import ManualProcessor, VectorStoreManager
from src.utils import print_colored, check_system_requirements
from config import validate_settings, settings


def main():
    parser = argparse.ArgumentParser(
        description="Indicizza manuali PDF nel vector database"
    )
    parser.add_argument(
        "--ocr",
        action="store_true",
        help="Usa OCR per PDF scansionati"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Elimina indice esistente prima di indicizzare"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verifica solo la configurazione senza indicizzare"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("🔧 OFFICINA AI - INDICIZZAZIONE MANUALI")
    print("="*80 + "\n")
    
    # Verifica sistema
    if args.check:
        check_system_requirements()
        return
    
    try:
        # Valida configurazione
        print("⚙️  Validazione configurazione...")
        validate_settings()
        print_colored("✅ Configurazione valida\n", "green")
        
        # Inizializza processor
        print("📚 Inizializzazione processor documenti...")
        processor = ManualProcessor()
        
        # Mostra statistiche manuali
        stats = processor.get_manual_stats()
        print(f"\n📊 Manuali trovati: {stats['total_manuals']}")
        
        if stats['total_manuals'] == 0:
            print_colored(f"\n⚠️  Nessun manuale trovato in: {settings.MANUALS_PATH}", "yellow")
            print("\n💡 Per iniziare:")
            print(f"   1. Crea la cartella: mkdir -p {settings.MANUALS_PATH}")
            print(f"   2. Aggiungi i tuoi PDF nella cartella")
            print(f"   3. Esegui nuovamente questo script")
            return
        
        print("\nPer marca:")
        for marca, count in stats['by_brand'].items():
            print(f"  - {marca}: {count} manuale/i")
        
        # Processa documenti
        print(f"\n🚀 Inizio elaborazione...")
        print(f"   OCR: {'Abilitato' if args.ocr else 'Disabilitato'}")
        
        chunks = processor.process_and_split(use_ocr=args.ocr)
        
        if not chunks:
            print_colored("\n❌ Nessun chunk generato. Controlla i file PDF.", "red")
            return
        
        print_colored(f"\n✅ Generati {len(chunks)} chunks", "green")
        
        # Inizializza vector store
        print(f"\n🗄️  Connessione a Pinecone...")
        vectorstore_manager = VectorStoreManager()
        
        # Elimina indice se richiesto
        if args.clear:
            print_colored("\n⚠️  Eliminazione indice esistente...", "yellow")
            response = input("Sei sicuro? (si/no): ")
            if response.lower() in ['si', 's', 'yes', 'y']:
                vectorstore_manager.delete_all(confirm=True)
                print_colored("✅ Indice eliminato\n", "green")
            else:
                print("Eliminazione annullata\n")
        
        # Indicizza
        print(f"📝 Indicizzazione in Pinecone...")
        print(f"   Questo può richiedere alcuni minuti...\n")
        
        vectorstore_manager.index_documents(chunks)
        
        # Mostra statistiche finali
        final_stats = vectorstore_manager.get_index_stats()
        
        print("\n" + "="*80)
        print_colored("✅ INDICIZZAZIONE COMPLETATA!", "green")
        print("="*80)
        print(f"\n📊 Statistiche finali:")
        print(f"   Indice: {settings.PINECONE_INDEX_NAME}")
        print(f"   Vettori totali: {final_stats.get('total_vector_count', 0)}")
        print(f"   Dimensione: {final_stats.get('dimension', 'N/A')}")
        
        print(f"\n💡 Prossimi passi:")
        print(f"   1. Avvia l'app: streamlit run app.py")
        print(f"   2. Oppure testa: python scripts/test_queries.py")
        print(f"   3. Oppure usa l'API: uvicorn api:app --reload")
        
        print("\n" + "="*80 + "\n")
        
    except KeyboardInterrupt:
        print_colored("\n\n❌ Indicizzazione interrotta dall'utente", "yellow")
        sys.exit(1)
    except Exception as e:
        print_colored(f"\n❌ Errore durante l'indicizzazione: {e}", "red")
        
        if settings.DEBUG:
            import traceback
            traceback.print_exc()
        
        sys.exit(1)


if __name__ == "__main__":
    main()