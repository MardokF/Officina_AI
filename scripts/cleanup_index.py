#!/usr/bin/env python3
"""
Script per gestire pulizia e manutenzione dell'indice Pinecone
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src import VectorStoreManager
from src.utils import print_colored
from config import validate_settings


def main():
    parser = argparse.ArgumentParser(
        description="Gestione e pulizia indice Pinecone"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Mostra statistiche indice"
    )
    parser.add_argument(
        "--delete-all",
        action="store_true",
        help="Elimina tutti i vettori"
    )
    parser.add_argument(
        "--delete-brand",
        type=str,
        help="Elimina vettori di una specifica marca"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Conferma eliminazione (richiesto per delete)"
    )
    
    args = parser.parse_args()
    
    try:
        validate_settings()
        manager = VectorStoreManager()
        
        # Mostra statistiche
        if args.stats or not any([args.delete_all, args.delete_brand]):
            stats = manager.get_index_stats()
            print("\n📊 STATISTICHE INDICE")
            print("=" * 50)
            print(f"Vettori totali: {stats.get('total_vector_count', 0)}")
            print(f"Dimensione: {stats.get('dimension', 'N/A')}")
            print(f"Namespaces: {stats.get('namespaces', {})}")
            print()
        
        # Elimina tutti
        if args.delete_all:
            if not args.confirm:
                print_colored("⚠️  ATTENZIONE: Stai per eliminare TUTTI i vettori!", "yellow")
                response = input("Sei sicuro? Scrivi 'DELETE' per confermare: ")
                if response != "DELETE":
                    print("Operazione annullata")
                    return
            
            print_colored("🗑️  Eliminazione in corso...", "yellow")
            manager.delete_all(confirm=True)
            print_colored("✅ Indice svuotato", "green")
        
        # Elimina per marca
        if args.delete_brand:
            if not args.confirm:
                print_colored(f"⚠️  Eliminazione vettori marca: {args.delete_brand}", "yellow")
                response = input("Confermi? (si/no): ")
                if response.lower() not in ['si', 's', 'yes', 'y']:
                    print("Operazione annullata")
                    return
            
            print(f"🗑️  Eliminazione vettori {args.delete_brand}...")
            manager.delete_by_filter(
                {"marca": args.delete_brand.upper()},
                confirm=True
            )
            print_colored(f"✅ Vettori {args.delete_brand} eliminati", "green")
    
    except Exception as e:
        print_colored(f"❌ Errore: {e}", "red")
        sys.exit(1)


if __name__ == "__main__":
    main()