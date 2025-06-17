import argparse
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from LLM.flashCard_genrator import FlashcardGenerator
from LLM.export import FlashcardExporter

def main():
    parser = argparse.ArgumentParser(description='Generate flashcards from text using Flan-T5')
    parser.add_argument('--input', '-i', required=True, help='Input text file')
    parser.add_argument('--output', '-o', default='flashcards.csv', help='Output file')
    parser.add_argument('--num-cards', '-n', type=int, default=20, help='Number of flashcards to generate')
    parser.add_argument('--difficulty', '-d', choices=['Easy', 'Medium', 'Hard', 'Mixed'], 
                       default='Mixed', help='Difficulty level')
    parser.add_argument('--format', '-f', choices=['csv', 'json', 'anki', 'quizlet'], 
                       default='csv', help='Export format')
    
    args = parser.parse_args()
    
    # Read input file
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.input}' not found")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    print("Initializing Flan-T5 model...")
    generator = FlashcardGenerator()
    
    print(f"Generating {args.num_cards} flashcards...")
    flashcards = generator.generate_from_text(text, args.num_cards, args.difficulty)
    
    if not flashcards:
        print("No flashcards generated. Please check your input text.")
        return
    
    # Export flashcards
    exporter = FlashcardExporter()
    
    if args.format == 'csv':
        output_file = exporter.to_csv(flashcards, args.output)
    elif args.format == 'json':
        output_file = exporter.to_json(flashcards, args.output)
    elif args.format == 'anki':
        output_file = exporter.to_anki(flashcards, args.output)
    elif args.format == 'quizlet':
        output_file = exporter.to_quizlet(flashcards, args.output)
    
    print(f"Generated {len(flashcards)} flashcards")
    print(f"Exported to: {output_file}")
    
    # Preview first few cards
    print("\nPreview:")
    for i, card in enumerate(flashcards[:3]):
        print(f"\nCard {i+1}:")
        print(f"Q: {card['question']}")
        print(f"A: {card['answer']}")

if __name__ == "__main__":
    main()
