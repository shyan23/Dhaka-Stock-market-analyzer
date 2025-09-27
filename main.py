import streamlit as st
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.app import StockMarketApp
from config import Config

def main():
    st.set_page_config(
        page_title="Stock Market Analyzer - Multi-User",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize the app
    app = StockMarketApp()
    app.run()

if __name__ == "__main__":
    main()


