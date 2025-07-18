"""
Drug Interaction Prediction Web Server

A Flask-based web server that provides drug interaction prediction using a trained XGBoost model.
Accepts multiple drug data and returns interaction severity predictions.
"""

import os
import pickle
import logging
from typing import Dict, List, Any, Tuple
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime

# Import custom modules
from preprocessing import DrugDataPreprocessor
from prediction_service import DrugInteractionPredictor
from validation import InputValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables for model and services
model = None
preprocessor = None
predictor = None
validator = None

def load_model_and_services():
    """Load the trained model and initialize services"""
    global model, preprocessor, predictor, validator
    
    try:
        # Load the trained XGBoost model
        # Try different possible paths for the model file
        possible_paths = [
            'xgboost_model.pkl',  # When running from src directory
            'src/xgboost_model.pkl',  # When running from project root
            os.path.join(os.path.dirname(__file__), 'xgboost_model.pkl')  # Relative to this file
        ]

        model_path = None
        for path in possible_paths:
            if os.path.exists(path):
                model_path = path
                break

        if not model_path:
            raise FileNotFoundError(f"Model file not found in any of these locations: {possible_paths}")
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        logger.info(f"✅ Model loaded successfully from {model_path}")
        
        # Initialize services
        preprocessor = DrugDataPreprocessor()
        predictor = DrugInteractionPredictor(model, preprocessor)
        validator = InputValidator()
        
        logger.info("✅ All services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to load model and services: {str(e)}")
        raise

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Drug Interaction Prediction API',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': model is not None
    })

@app.route('/health', methods=['GET'])
def health():
    """Detailed health check endpoint for monitoring"""
    try:
        # Test model prediction capability
        test_successful = model is not None and preprocessor is not None

        return jsonify({
            'status': 'healthy' if test_successful else 'unhealthy',
            'service': 'Drug Interaction Prediction API',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'checks': {
                'model_loaded': model is not None,
                'preprocessor_ready': preprocessor is not None,
                'predictor_ready': predictor is not None,
                'validator_ready': validator is not None
            },
            'uptime': datetime.now().isoformat()
        }), 200 if test_successful else 503

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': 'Health check failed',
            'timestamp': datetime.now().isoformat()
        }), 503

@app.route('/predict-interactions', methods=['POST'])
def predict_interactions():
    """
    Main endpoint for drug interaction prediction
    
    Expected JSON format:
    {
        "drugs": [
            {
                "drug_name": "Codeine",
                "pharmacodynamic_class": "Opioid Analgesic",
                "logp": 1.45,
                "therapeutic_index": "Non-NTI",
                "transporter_interaction": "Substrate: P-gp",
                "plasma_protein_binding": 25.0,
                "metabolic_pathways": "Substrate: CYP2D6;CYP3A4"
            },
            {
                "drug_name": "Abiraterone",
                "pharmacodynamic_class": "Androgen Synthesis Inhibitor",
                "logp": 5.12,
                "therapeutic_index": "Non-NTI",
                "transporter_interaction": "Substrate: P-gp / Inhibitor: P-gp;BCRP",
                "plasma_protein_binding": 99.0,
                "metabolic_pathways": "Substrate: CYP3A4 / Inhibitor: CYP2D6"
            }
        ]
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No JSON data provided',
                'status': 'error'
            }), 400
        
        # Validate input data
        validation_result = validator.validate_input(data)
        if not validation_result['valid']:
            return jsonify({
                'error': 'Input validation failed',
                'details': validation_result['errors'],
                'status': 'error'
            }), 400
        
        # Extract drugs from input
        drugs = data.get('drugs', [])
        
        if len(drugs) < 2:
            return jsonify({
                'error': 'At least 2 drugs are required for interaction prediction',
                'status': 'error'
            }), 400
        
        # Predict interactions
        predictions = predictor.predict_interactions(drugs)
        
        # Format response
        response = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'input_drugs_count': len(drugs),
            'drug_pairs_analyzed': len(predictions),
            'predictions': predictions,
            'summary': {
                'high_risk_pairs': len([p for p in predictions if p.get('prediction', {}).get('severity') == 'Major']),
                'moderate_risk_pairs': len([p for p in predictions if p.get('prediction', {}).get('severity') == 'Moderate']),
                'low_risk_pairs': len([p for p in predictions if p.get('prediction', {}).get('severity') == 'Minor'])
            }
        }
        
        logger.info(f"✅ Processed interaction prediction for {len(drugs)} drugs")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Error in predict_interactions: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'status': 'error'
        }), 500

@app.route('/api/info', methods=['GET'])
def api_info():
    """Get API information and usage instructions"""
    return jsonify({
        'api_name': 'Drug Interaction Prediction API',
        'version': '1.0.0',
        'description': 'Predicts drug-drug interaction severity using machine learning',
        'endpoints': {
            '/': 'Health check',
            '/predict-interactions': 'Main prediction endpoint (POST)',
            '/api/info': 'API information'
        },
        'supported_severity_levels': ['Major', 'Moderate', 'Minor'],
        'required_drug_fields': [
            'drug_name',
            'pharmacodynamic_class',
            'logp',
            'therapeutic_index',
            'transporter_interaction',
            'plasma_protein_binding',
            'metabolic_pathways'
        ],
        'example_request': {
            'drugs': [
                {
                    'drug_name': 'Example Drug A',
                    'pharmacodynamic_class': 'Antibiotic',
                    'logp': 2.5,
                    'therapeutic_index': 'Non-NTI',
                    'transporter_interaction': 'Substrate: P-gp',
                    'plasma_protein_binding': 85.0,
                    'metabolic_pathways': 'Substrate: CYP3A4'
                }
            ]
        }
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'status': 'error',
        'available_endpoints': ['/', '/predict-interactions', '/api/info']
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'status': 'error'
    }), 500

# Load model and initialize services when module is imported
try:
    load_model_and_services()
except Exception as e:
    logger.error(f"❌ Failed to load model and services: {str(e)}")
    # Don't exit here, let the app start but mark as unhealthy

if __name__ == '__main__':
    try:
        # Get configuration from environment variables
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 5000))
        debug = os.getenv('DEBUG', 'False').lower() == 'true'

        logger.info(f"🚀 Starting Drug Interaction Prediction Server on {host}:{port}")

        # Start the Flask app
        app.run(host=host, port=port, debug=debug)

    except Exception as e:
        logger.error(f"❌ Failed to start server: {str(e)}")
        exit(1)
