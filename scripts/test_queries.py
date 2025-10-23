#!/usr/bin/env python3
"""
Script per testare il chatbot con domande predefinite
"""
import sys
from pathlib import Path
import time

# Aggiungi la root al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import OfficinaChatbot
from src.qa_chain import format_answer_with_sources
from src.utils import print_colored
from config import validate_settings


# Domande di test
TEST_QUESTIONS = [
    {
        "question": "Come si sostituisce l'olio motore?",
        "filters": None
    },
    {
        "question": "Qual è la coppia di serraggio per i bulloni della testata?",
        "filters": None
    },
    {
        "question": "Capacità del serbatoio carburante",
        "filters": None
    },
    {
        "question": "Procedura cambio pastiglie freni anteriori",
        "filters": None
    },
    {
        "question": "Specifiche olio motore raccomandato",
        "filters": None
    }
]


def run_tests(interactive: bool = False):
    """
    Esegue i test predefiniti
    
    Args:
        interactive: Se True, chiede conferma prima di ogni domanda
    """
    print("\n" + "="*80)
    print("🧪 TEST OFFICINA AI CHATBOT")
    print("="*80 + "\n")
    
    try:
        # Valida configurazione
        print("⚙️  Validazione configurazione...")
        validate_settings()
        print_colored("✅ Configurazione valida\n", "green")
        
        # Inizializza chatbot
        print("🤖 Inizializzazione chatbot...")
        chatbot = OfficinaChatbot()
        print_colored("✅ Chatbot pronto\n", "green")
        
        # Esegui domande di test
        for i, test in enumerate(TEST_QUESTIONS, 1):
            print("\n" + "="*80)
            print(f"TEST {i}/{len(TEST_QUESTIONS)}")
            print("="*80)
            
            print(f"\n❓ Domanda: {test['question']}")
            
            if test['filters']:
                print(f"🔍 Filtri: {test['filters']}")
            
            if interactive:
                response = input("\n▶️  Continuare? (invio per sì, 'n' per saltare): ")
                if response.lower() == 'n':
                    print_colored("⏭️  Test saltato\n", "yellow")
                    continue
            
            # Esegui query
            start_time = time.time()
            result = chatbot.ask(
                question=test['question'],
                filters=test['filters'],
                return_sources=True
            )
            elapsed_time = time.time() - start_time
            
            # Mostra risposta
            print(f"\n💬 Risposta ({elapsed_time:.2f}s):")
            print("-" * 80)
            formatted = format_answer_with_sources(result)
            print(formatted)
            print("-" * 80)
            
            # Pausa tra domande
            if i < len(TEST_QUESTIONS):
                time.sleep(2)
        
        # Summary
        print("\n" + "="*80)
        print_colored("✅ TUTTI I TEST COMPLETATI!", "green")
        print("="*80 + "\n")
        
    except KeyboardInterrupt:
        print_colored("\n\n⚠️  Test interrotti dall'utente", "yellow")
        sys.exit(0)
    except Exception as e:
        print_colored(f"\n❌ Errore durante i test: {e}", "red")
        sys.exit(1)


def interactive_mode():
    """Modalità interattiva - inserisci le tue domande"""
    print("\n" + "="*80)
    print("💬 MODALITÀ INTERATTIVA")
    print("="*80)
    print("\nInserisci le tue domande (digita 'exit' per uscire)\n")
    
    try:
        validate_settings()
        chatbot = OfficinaChatbot()
        print_colored("✅ Chatbot pronto!\n", "green")
        
        while True:
            print("-" * 80)
            question = input("\n❓ La tua domanda: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['exit', 'quit', 'esci']:
                print_colored("\n👋 Arrivederci!\n", "cyan")
                break
            
            # Chiedi filtri (opzionale)
            marca = input("🏷️  Marca (opzionale, invio per skip): ").strip().upper()
            modello = input("🏷️  Modello (opzionale, invio per skip): ").strip()
            
            filters = {}
            if marca:
                filters['marca'] = marca
            if modello:
                filters['modello'] = modello
            
            # Genera risposta
            print(f"\n🤔 Pensando...")
            start_time = time.time()
            
            result = chatbot.ask(
                question=question,
                filters=filters if filters else None,
                return_sources=True
            )
            
            elapsed_time = time.time() - start_time
            
            # Mostra risposta
            print(f"\n💬 Risposta ({elapsed_time:.2f}s):")
            print("-" * 80)
            formatted = format_answer_with_sources(result)
            print(formatted)
    
    except KeyboardInterrupt:
        print_colored("\n\n👋 Arrivederci!\n", "cyan")
    except Exception as e:
        print_colored(f"\n❌ Errore: {e}", "red")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test del chatbot Officina AI"
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Modalità interattiva per inserire domande personalizzate"
    )
    parser.add_argument(
        "-p", "--prompt",
        action="store_true",
        help="Chiedi conferma prima di ogni test"
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    else:
        run_tests(interactive=args.prompt)


if __name__ == "__main__":
    main()