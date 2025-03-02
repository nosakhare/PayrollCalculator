import subprocess
import os
from flask import Flask, send_from_directory
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/ads.txt')
def ads_txt():
    return send_from_directory('.', 'ads.txt')

@app.route('/')
def index():
    return """
    <h1>Welcome!</h1>
    <p>Flask server is running. <a href='/streamlit'>Go to Streamlit App</a></p>
    """

@app.route('/streamlit')
def streamlit_route():
    return """
    <h2>Streamlit runs on port 8501 internally.</h2>
    <p>If this doesn't redirect automatically, open Replit's webview for port 8501.</p>
    <a href='http://127.0.0.1:8501' target='_blank'>Open Streamlit App</a>
    """

def run_streamlit():
    # Explicitly set Streamlit to use port 8501 and ensure it's accessible externally
    logger.info("Starting Streamlit server on port 8501...")
    try:
        subprocess.Popen([
            "streamlit", "run", "main.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--server.headless=true"
        ])
        logger.info("Streamlit server process initiated successfully")
    except Exception as e:
        logger.error(f"Failed to start Streamlit server: {str(e)}")
        raise

if __name__ == "__main__":
    run_streamlit()
    # Keep Flask on port 5000 as required by Replit
    app.run(host="0.0.0.0", port=5000)