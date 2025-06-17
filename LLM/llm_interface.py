from abc import ABC, abstractmethod
from transformers import pipeline, T5ForConditionalGeneration, T5Tokenizer
import torch
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMInterface(ABC):
    """Abstract base class for LLM interfaces"""
    
    @abstractmethod
    def generate_flashcards(self, text: str, num_cards: int = 20) -> List[Dict[str, str]]:
        pass

class FlanT5Interface(LLMInterface):
    """Flan-T5 implementation for flashcard generation"""
    
    def __init__(self, model_name: str = "google/flan-t5-base"):
        """
        Initialize Flan-T5 model
        Options: flan-t5-small, flan-t5-base, flan-t5-large
        """
        logger.info(f"Loading {model_name}...")
        
        # Check if CUDA is available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Load model and tokenizer
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        self.model.to(self.device)
        
        logger.info("Model loaded successfully!")
    
    def _create_prompt(self, text: str, num_cards: int) -> str:
        """Create optimized prompt for Flan-T5"""
        # Add more and better Q/A examples to guide the model
        example_qa = """
Q: What is photosynthesis?
A: Photosynthesis is the process by which green plants use sunlight to synthesize food from carbon dioxide and water.
---
Q: Who painted the Mona Lisa?
A: Leonardo da Vinci painted the Mona Lisa.
---
Q: What is the capital of France?
A: Paris is the capital of France.
---
Q: Who led the Salt March in India?
A: Mahatma Gandhi led the Salt March in India.
---
Q: When did India gain independence from British rule?
A: India gained independence on August 15, 1947.
---
Q: What is the main idea of the passage?
A: The main idea is the struggle for India's independence from British rule.
---
Q: What is the significance of the Renaissance?
A: The Renaissance marked a period of cultural, artistic, and scientific rebirth in Europe.
---
Q: What is Python used for?
A: Python is used for web development, data science, artificial intelligence, and automation.
---
Q: What is the Ganges River known for?
A: The Ganges River is considered sacred in Hinduism and is a major river in India.
---
Q: What is the process of human respiration?
A: Human respiration is the process of inhaling oxygen and exhaling carbon dioxide.
---
"""
        prompt = f"""Read the following text and generate {num_cards} flashcards. For each flashcard, you MUST provide both a question and a short, factual answer, based only on the text. Format each as:
Q: <question>
A: <answer>
---

Here are some examples:
{example_qa}
Text:
{text}

Flashcards:
"""
        return prompt
    
    def _chunk_text(self, text: str, max_tokens: int = 400) -> List[str]:
        """Split text into chunks if too long"""
        tokens = self.tokenizer.encode(text)
        if len(tokens) <= max_tokens:
            return [text]
        
        # Simple sentence-based chunking
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            test_chunk = current_chunk + sentence + ". "
            if len(self.tokenizer.encode(test_chunk)) > max_tokens and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
            else:
                current_chunk = test_chunk
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def generate_flashcards(self, text: str, num_cards: int = 20) -> List[Dict[str, str]]:
        """Generate flashcards from text"""
        try:
            # Chunk text if necessary
            chunks = self._chunk_text(text)
            all_flashcards = []
            
            cards_per_chunk = max(1, num_cards // len(chunks))
            
            for i, chunk in enumerate(chunks):
                # Adjust cards for last chunk
                if i == len(chunks) - 1:
                    remaining_cards = num_cards - len(all_flashcards)
                    cards_to_generate = max(remaining_cards, 1)
                else:
                    cards_to_generate = cards_per_chunk
                
                prompt = self._create_prompt(chunk, cards_to_generate)
                
                # Generate response
                inputs = self.tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
                inputs = inputs.to(self.device)
                
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs,
                        max_length=300,
                        num_return_sequences=1,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                logger.info(f"MODEL RAW OUTPUT: {response}")
                
                # Parse flashcards from response
                flashcards = self._parse_flashcards(response)
                all_flashcards.extend(flashcards)
                
                if len(all_flashcards) >= num_cards:
                    break
            
            return all_flashcards[:num_cards]
        
        except Exception as e:
            logger.error(f"Error generating flashcards: {e}")
            return []
    
    def _parse_flashcards(self, response: str) -> List[Dict[str, str]]:
        """Parse flashcards from model response (flexible for unlabeled Q/A)"""
        flashcards = []
        
        # Split by --- or double newlines
        sections = response.split('---')
        if len(sections) == 1:
            sections = response.split('\n\n')
        
        for section in sections:
            lines = [l.strip() for l in section.strip().split('\n') if l.strip()]
            question = None
            answer = None
            
            # Try to find Q:/A: labels first
            for line in lines:
                if line.startswith('Q:'):
                    question = line[2:].strip()
                elif line.startswith('A:'):
                    answer = line[2:].strip()
            
            # If not found, try to infer question/answer
            if not question and lines:
                # If the first line looks like a question
                if lines[0].endswith('?'):
                    question = lines[0]
                    if len(lines) > 1:
                        answer = lines[1]
                else:
                    # If only one line, treat as question
                    question = lines[0]
            
            if question:
                flashcards.append({
                    'question': question,
                    'answer': answer if answer else '(No answer provided)',
                    'difficulty': 'Medium'  # Default difficulty
                })
        
        return flashcards

