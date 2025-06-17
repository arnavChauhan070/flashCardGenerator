# flashCardGenerator
Features
AI-powered flashcard generation from any text (notes, articles, etc.)
Customizable number of cards and difficulty level
Export to CSV, JSON, Anki, and Quizlet formats
Modern, easy-to-use Streamlit UI
No API keys required (runs locally)

// steps to run this 

1) Clone this repository:
   git clone (https://github.com/arnavChauhan070/flashCardGenerator.git)
   cd flashCardGenerator

2) Create and activate a virtual environment (recommended): or may be    conflict arise if u do direclty

   python3 -m venv venv
   # mac
   source venv/bin/activate
   # windows
    venv\Scripts\activate
3) Install dependencies :
    pip install -r requirements.txt

4) Run app 
      streamlit run UI/app.py

   
You will be redirected if not then open the local host as said in terminal
for the first time it will take time to download Flan -T5 - base model

# Model Limitations
This app uses the open-source Flan-T5-base model.
Sometimes, the model may only generate questions or a limited number of flashcards, even with long input.
This is a limitation of the model, not the app code.
For best results, use clear, factual, and detailed input text.


