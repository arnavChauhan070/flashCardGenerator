import streamlit as st
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info("Starting Flashcard Generator app...")

# Debug path setup
current_dir = Path(__file__).parent.parent
logger.debug(f"Adding to path: {current_dir}")
sys.path.append(str(current_dir))

try:
    from LLM.flashCard_genrator import FlashcardGenerator
    from LLM.export import FlashcardExporter
    import pandas as pd
    import io
    logger.info("Successfully imported dependencies")
except Exception as e:
    logger.error(f"Failed to import dependencies: {e}")
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
            logger.info("Initializing FlashcardGenerator...")
            st.session_state.generator = FlashcardGenerator()
            logger.info("FlashcardGenerator initialized successfully")
            st.success("Model loaded successfully!")
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            st.error(f"Error loading model: {e}")