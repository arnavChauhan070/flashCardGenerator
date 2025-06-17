import pandas as pd
import json
import csv
from typing import List, Dict
from pathlib import Path

class FlashcardExporter:
    """Handle different export formats for flashcards"""
    
    @staticmethod
    def to_csv(flashcards: List[Dict[str, str]], filename: str) -> str:
        """Export flashcards to CSV format"""
        df = pd.DataFrame(flashcards)
        filepath = Path(filename)
        df.to_csv(filepath, index=False)
        return str(filepath)
    
    @staticmethod
    def to_json(flashcards: List[Dict[str, str]], filename: str) -> str:
        """Export flashcards to JSON format"""
        filepath = Path(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'flashcards': flashcards,
                'total_cards': len(flashcards),
                'generated_by': 'Flan-T5 Flashcard Generator'
            }, f, indent=2, ensure_ascii=False)
        return str(filepath)
    
    @staticmethod
    def to_anki(flashcards: List[Dict[str, str]], filename: str) -> str:
        """Export flashcards to Anki-compatible CSV format"""
        filepath = Path(filename)
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for card in flashcards:
                writer.writerow([card['question'], card['answer']])
        return str(filepath)
    
    @staticmethod
    def to_quizlet(flashcards: List[Dict[str, str]], filename: str) -> str:
        """Export flashcards to Quizlet-compatible format"""
        filepath = Path(filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            for card in flashcards:
                f.write(f"{card['question']}\t{card['answer']}\n")
        return str(filepath)
