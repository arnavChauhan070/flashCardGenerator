from typing import List, Dict, Optional
import re
import logging
from LLM.llm_interface import LLMInterface, FlanT5Interface

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class FlashcardGenerator:
    """Main flashcard generator class"""
    
    def __init__(self, llm_interface: Optional[LLMInterface] = None):
        logger.info("Initializing FlashcardGenerator")
        self.llm = llm_interface or FlanT5Interface()
        
        # Test data fallback
        self.test_cards = [
            {
                "question": "What is photosynthesis?",
                "answer": "Process where plants convert sunlight to energy",
                "difficulty": "Medium"
            },
            {
                "question": "What is Python?",
                "answer": "A high-level programming language",
                "difficulty": "Easy"
            }
        ]
    
    def generate_from_text(self, 
                          text: str, 
                          num_cards: int = 20,
                          difficulty: str = "Mixed") -> List[Dict[str, str]]:
        """Generate flashcards from input text"""
        
        logger.info(f"Generating {num_cards} flashcards, difficulty: {difficulty}")
        
        MIN_INPUT_LENGTH = 100
        if len(text.strip()) < MIN_INPUT_LENGTH:
            logger.warning("Input text too short for flashcard generation.")
            self.last_error = f"Input text is too short (min {MIN_INPUT_LENGTH} characters required)."
            return []
        try:
            # Preprocess text
            cleaned_text = self._preprocess_text(text)
            logger.debug(f"Cleaned text length: {len(cleaned_text)}")
            
            if not cleaned_text.strip():
                logger.warning("Empty text after preprocessing")
                self.last_error = "Input text is empty after preprocessing."
                return []
            
            # Generate flashcards
            flashcards = self.llm.generate_flashcards(cleaned_text, num_cards)
            
            # Debug output
            logger.debug(f"Raw model output: {flashcards}")
            
            # Fallback to empty if model fails
            if not flashcards:
                logger.warning("Model returned no flashcards.")
                self.last_error = "Model could not generate flashcards. Try a longer or more detailed input."
                return []
            
            # Post-process flashcards
            processed_cards = self._postprocess_flashcards(flashcards, difficulty, original_text=text)
            logger.info(f"Generated {len(processed_cards)} valid flashcards")
            self.last_error = None
            return processed_cards
            
        except Exception as e:
            logger.error(f"Error generating flashcards: {e}")
            self.last_error = f"Error generating flashcards: {e}"
            return []  # Fallback to empty list
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and prepare text for processing"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S*@\S*\s?', '', text)
        
        return text.strip()
    
    def _postprocess_flashcards(self, 
                               flashcards: List[Dict[str, str]], 
                               difficulty: str, 
                               original_text: str = None) -> List[Dict[str, str]]:
        """Clean and enhance generated flashcards. Auto-fill missing answers from input text if possible."""
        processed = []
        import difflib
        sentences = []
        if original_text:
            import re
            sentences = re.split(r'(?<=[.!?]) +', original_text)
        for card in flashcards:
            # Skip empty or very short cards
            if len(card.get('question', '')) < 5 or len(card.get('answer', '')) < 2:
                # Try to auto-fill answer if missing
                if card.get('question', '') and (not card.get('answer') or card.get('answer') == '(No answer provided)') and sentences:
                    # Find the most similar sentence from the input
                    best = difflib.get_close_matches(card['question'], sentences, n=1)
                    if best:
                        card['answer'] = best[0]
                        card['difficulty'] = difficulty if difficulty != "Mixed" else card.get('difficulty', 'Medium')
                        processed.append(card)
                continue
            # Clean up text
            question = card['question'].strip()
            answer = card['answer'].strip()
            # Remove quotes if they wrap the entire text
            if question.startswith('"') and question.endswith('"'):
                question = question[1:-1]
            if answer.startswith('"') and answer.endswith('"'):
                answer = answer[1:-1]
            processed_card = {
                'question': question,
                'answer': answer,
                'difficulty': difficulty if difficulty != "Mixed" else card.get('difficulty', 'Medium')
            }
            processed.append(processed_card)
        # Remove duplicates
        seen = set()
        unique_cards = []
        for card in processed:
            card_key = (card['question'].lower(), card['answer'].lower())
            if card_key not in seen:
                seen.add(card_key)
                unique_cards.append(card)
        return unique_cards
