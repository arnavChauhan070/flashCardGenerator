import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from LLM.flashCard_genrator import FlashcardGenerator
from  LLM.export import FlashcardExporter
import pandas as pd
import io

# Page config
st.set_page_config(
    page_title="Flashcard Generator",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 AI Flashcard Generator")
st.markdown("Generate flashcards from your study materials using Flan-T5")

# Initialize session state
if 'flashcards' not in st.session_state:
    st.session_state.flashcards = []
if 'generator' not in st.session_state:
    with st.spinner("Loading Flan-T5 model..."):
        st.session_state.generator = FlashcardGenerator()

# Sidebar for configuration
st.sidebar.header("⚙️ Configuration")

num_cards = st.sidebar.slider("Number of flashcards", 5, 50, 20)
difficulty = st.sidebar.selectbox("Difficulty level", 
                                 ["Mixed", "Easy", "Medium", "Hard"])

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Input")
    
    # Input method selection
    input_method = st.radio("Choose input method:", 
                           ["Upload file", "Paste text"])
    
    text_input = ""
    
    if input_method == "Upload file":
        uploaded_file = st.file_uploader("Choose a text file", 
                                       type=['txt', 'md'])
        if uploaded_file is not None:
            text_input = str(uploaded_file.read(), "utf-8")
            st.text_area("File content preview:", text_input[:500] + "...", 
                        height=200, disabled=True)
    else:
        st.info("Please enter at least 100 characters for best results.")
        text_input = st.text_area("Paste your text here:", 
                                height=300, 
                                placeholder="Enter the text you want to create flashcards from...")
    
    # Generate button
    if st.button("🚀 Generate Flashcards", type="primary"):
        if text_input.strip():
            with st.spinner("Generating flashcards..."):
                st.session_state.flashcards = st.session_state.generator.generate_from_text(
                    text_input, num_cards, difficulty
                )
            
            if st.session_state.flashcards:
                st.success(f"Generated {len(st.session_state.flashcards)} flashcards!")
            else:
                error_msg = getattr(st.session_state.generator, 'last_error', None)
                if error_msg:
                    st.error(error_msg)
                else:
                    st.error("No flashcards generated. Please check your input text.")
        else:
            st.warning("Please provide some text to generate flashcards from.")

with col2:
    st.header("🎴 Generated Flashcards")
    
    if st.session_state.flashcards:
        # Display flashcards
        for i, card in enumerate(st.session_state.flashcards):
            with st.expander(f"Card {i+1}: {card['question'][:50]}..."):
                st.write(f"**Question:** {card['question']}")
                st.write(f"**Answer:** {card['answer']}")
                st.write(f"**Difficulty:** {card['difficulty']}")
        
        # Export options
        st.subheader("📤 Export Options")
        
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            # CSV export
            csv_data = pd.DataFrame(st.session_state.flashcards).to_csv(index=False)
            st.download_button(
                label="📊 Download CSV",
                data=csv_data,
                file_name="flashcards.csv",
                mime="text/csv"
            )
            
            # Anki export
            anki_data = "\n".join([f"{card['question']},{card['answer']}" 
                                  for card in st.session_state.flashcards])
            st.download_button(
                label="🃏 Download Anki CSV",
                data=anki_data,
                file_name="flashcards_anki.csv",
                mime="text/csv"
            )
        
        with col_export2:
            # JSON export
            import json
            json_data = json.dumps({
                'flashcards': st.session_state.flashcards,
                'total_cards': len(st.session_state.flashcards)
            }, indent=2)
            st.download_button(
                label="📋 Download JSON",
                data=json_data,
                file_name="flashcards.json",
                mime="application/json"
            )
            
            # Quizlet export
            quizlet_data = "\n".join([f"{card['question']}\t{card['answer']}" 
                                     for card in st.session_state.flashcards])
            st.download_button(
                label="📚 Download Quizlet",
                data=quizlet_data,
                file_name="flashcards_quizlet.txt",
                mime="text/plain"
            )
    else:
        st.info("Generate flashcards to see them here!")

# Footer
st.markdown("---")
st.markdown("Built with Flan-T5 and Streamlit • [GitHub](https://github.com/yourusername/flashcard-generator)")
