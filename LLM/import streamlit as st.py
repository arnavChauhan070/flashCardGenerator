import streamlit as st
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Debug path setup
current_dir = Path(__file__).parent.parent

try:
    from LLM.flashCard_genrator import FlashcardGenerator
    from LLM.export import FlashcardExporter
    import pandas as pd
    import io
except Exception as e:
    st.error(f"Import error: {e}")

# Page config
st.set_page_config(
    page_title="Flashcard Generator",
    page_icon="🎯",
    layout="wide"
)

# Show startup message
st.info("App is initializing...")

# Initialize model with error handling
if 'generator' not in st.session_state:
    with st.spinner("Loading Flan-T5 model..."):
        try:
            st.session_state.generator = FlashcardGenerator()
            st.success("Model loaded successfully!")
        except Exception as e:
            st.error(f"Error loading model: {e}")