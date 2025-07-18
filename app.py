"""
Drug Interaction Prediction API - Production Entry Point

This is the main entry point for the production deployment.
It imports the Flask app from the src directory.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import app

if __name__ == '__main__':
    app.run()
