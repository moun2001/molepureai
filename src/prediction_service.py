"""
Prediction Service Module for Drug Interaction Analysis

Handles the core prediction logic for drug-drug interactions using the trained XGBoost model.
Processes multiple drugs, generates all possible pairs, and returns interaction predictions.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from itertools import combinations
import logging
from preprocessing_config import SEVERITY_LEVELS

logger = logging.getLogger(__name__)

class DrugInteractionPredictor:
    """Handles drug interaction prediction using the trained model"""
    
    def __init__(self, model, preprocessor):
        """
        Initialize the predictor

        Args:
            model: Trained XGBoost model
            preprocessor: DrugDataPreprocessor instance
        """
        self.model = model
        self.preprocessor = preprocessor
        self.severity_levels = SEVERITY_LEVELS

        # Create mapping from model classes to severity labels
        # Model classes are typically [0, 1, 2] corresponding to severity levels
        self.class_to_severity = {}
        if hasattr(model, 'classes_'):
            for i, class_label in enumerate(model.classes_):
                if i < len(self.severity_levels):
                    self.class_to_severity[str(class_label)] = self.severity_levels[i]
                else:
                    self.class_to_severity[str(class_label)] = 'Unknown'

        logger.info("✅ DrugInteractionPredictor initialized")
        logger.info(f"Class to severity mapping: {self.class_to_severity}")
    
    def predict_interactions(self, drugs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Predict interactions for all possible drug pairs
        
        Args:
            drugs: List of drug dictionaries with characteristics
            
        Returns:
            List of prediction results for each drug pair
        """
        try:
            predictions = []
            
            # Generate all possible drug pairs
            drug_pairs = list(combinations(range(len(drugs)), 2))
            
            logger.info(f"🔍 Analyzing {len(drug_pairs)} drug pairs from {len(drugs)} drugs")
            
            for i, (idx_a, idx_b) in enumerate(drug_pairs):
                drug_a = drugs[idx_a]
                drug_b = drugs[idx_b]
                
                # Predict interaction for this pair
                prediction = self._predict_single_pair(drug_a, drug_b, idx_a, idx_b)
                predictions.append(prediction)
                
                logger.debug(f"Processed pair {i+1}/{len(drug_pairs)}: {drug_a['drug_name']} + {drug_b['drug_name']}")
            
            # Sort predictions by severity (Major > Moderate > Minor)
            predictions = self._sort_predictions_by_severity(predictions)
            
            logger.info(f"✅ Completed analysis of {len(predictions)} drug pairs")
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Error in predict_interactions: {str(e)}")
            raise
    
    def _predict_single_pair(self, drug_a: Dict[str, Any], drug_b: Dict[str, Any], 
                           idx_a: int, idx_b: int) -> Dict[str, Any]:
        """
        Predict interaction for a single drug pair
        
        Args:
            drug_a: First drug characteristics
            drug_b: Second drug characteristics
            idx_a: Index of first drug in original list
            idx_b: Index of second drug in original list
            
        Returns:
            Dictionary containing prediction results
        """
        try:
            # Preprocess the drug pair
            feature_vector = self.preprocessor.preprocess_drug_pair(drug_a, drug_b)
            
            # Get prediction probabilities
            probabilities = self.model.predict_proba(feature_vector)[0]
            
            # Get predicted class
            predicted_class_idx = np.argmax(probabilities)
            predicted_class_raw = str(self.model.classes_[predicted_class_idx])
            predicted_severity = self.class_to_severity.get(predicted_class_raw, 'Unknown')

            # Get confidence score
            confidence = float(probabilities[predicted_class_idx])

            # Create probability distribution (ensure all keys and values are JSON serializable)
            prob_distribution = {}
            for i, class_label in enumerate(self.model.classes_):
                severity_label = self.class_to_severity.get(str(class_label), 'Unknown')
                prob_distribution[severity_label] = float(probabilities[i])
            
            # Determine risk level
            risk_level = self._get_risk_level(predicted_severity)
            
            # Create prediction result (ensure all values are JSON serializable)
            prediction = {
                'drug_pair': {
                    'drug_a': {
                        'index': int(idx_a),
                        'name': str(drug_a['drug_name']),
                        'class': str(drug_a['pharmacodynamic_class'])
                    },
                    'drug_b': {
                        'index': int(idx_b),
                        'name': str(drug_b['drug_name']),
                        'class': str(drug_b['pharmacodynamic_class'])
                    }
                },
                'prediction': {
                    'severity': str(predicted_severity),
                    'confidence': float(confidence),
                    'risk_level': str(risk_level)
                },
                'probability_distribution': prob_distribution,
                'clinical_significance': self._get_clinical_significance(predicted_severity, confidence),
                'recommendation': self._get_recommendation(predicted_severity, confidence)
            }
            
            return prediction
            
        except Exception as e:
            logger.error(f"❌ Error predicting single pair: {str(e)}")
            # Return error prediction (ensure all values are JSON serializable)
            return {
                'drug_pair': {
                    'drug_a': {'index': int(idx_a), 'name': str(drug_a.get('drug_name', 'Unknown')), 'class': str(drug_a.get('pharmacodynamic_class', 'Unknown'))},
                    'drug_b': {'index': int(idx_b), 'name': str(drug_b.get('drug_name', 'Unknown')), 'class': str(drug_b.get('pharmacodynamic_class', 'Unknown'))}
                },
                'prediction': {
                    'severity': 'Unknown',
                    'confidence': 0.0,
                    'risk_level': 'Unknown'
                },
                'error': str(e)
            }
    
    def _get_risk_level(self, severity: str) -> str:
        """Convert severity to risk level"""
        risk_mapping = {
            'Major': 'High',
            'Moderate': 'Medium',
            'Minor': 'Low'
        }
        return risk_mapping.get(severity, 'Unknown')
    
    def _get_clinical_significance(self, severity: str, confidence: float) -> str:
        """Get clinical significance description"""
        if severity == 'Major':
            if confidence > 0.8:
                return "High clinical significance - Strong evidence of major interaction"
            else:
                return "High clinical significance - Potential major interaction"
        elif severity == 'Moderate':
            if confidence > 0.7:
                return "Moderate clinical significance - Monitor patient closely"
            else:
                return "Moderate clinical significance - Consider monitoring"
        elif severity == 'Minor':
            if confidence > 0.6:
                return "Low clinical significance - Minimal interaction expected"
            else:
                return "Low clinical significance - Uncertain interaction"
        else:
            return "Unknown clinical significance"
    
    def _get_recommendation(self, severity: str, confidence: float) -> str:
        """Get clinical recommendation"""
        if severity == 'Major':
            return "Consider alternative medications or adjust dosing. Consult healthcare provider."
        elif severity == 'Moderate':
            return "Monitor patient for adverse effects. Consider dose adjustment if needed."
        elif severity == 'Minor':
            return "Generally safe combination. Routine monitoring recommended."
        else:
            return "Consult healthcare provider for guidance."
    
    def _sort_predictions_by_severity(self, predictions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort predictions by severity level (Major > Moderate > Minor)"""
        severity_order = {'Major': 3, 'Moderate': 2, 'Minor': 1, 'Unknown': 0}
        
        return sorted(predictions, 
                     key=lambda x: (
                         severity_order.get(x['prediction']['severity'], 0),
                         x['prediction']['confidence']
                     ), 
                     reverse=True)
    
    def get_interaction_summary(self, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a summary of all interactions
        
        Args:
            predictions: List of prediction results
            
        Returns:
            Summary dictionary with statistics and insights
        """
        try:
            if not predictions:
                return {'total_pairs': 0, 'message': 'No predictions available'}
            
            # Count by severity
            severity_counts = {}
            high_confidence_pairs = []
            
            for pred in predictions:
                severity = pred['prediction']['severity']
                confidence = pred['prediction']['confidence']
                
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                if confidence > 0.7:  # High confidence threshold
                    high_confidence_pairs.append(pred)
            
            # Find highest risk pair
            highest_risk_pair = None
            if predictions:
                highest_risk_pair = predictions[0]  # Already sorted by severity and confidence
            
            summary = {
                'total_pairs_analyzed': len(predictions),
                'severity_distribution': severity_counts,
                'high_confidence_predictions': len(high_confidence_pairs),
                'highest_risk_interaction': {
                    'drugs': f"{highest_risk_pair['drug_pair']['drug_a']['name']} + {highest_risk_pair['drug_pair']['drug_b']['name']}",
                    'severity': highest_risk_pair['prediction']['severity'],
                    'confidence': highest_risk_pair['prediction']['confidence']
                } if highest_risk_pair else None,
                'overall_risk_assessment': self._get_overall_risk_assessment(severity_counts),
                'recommendations': self._get_overall_recommendations(severity_counts)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error generating interaction summary: {str(e)}")
            return {'error': str(e)}
    
    def _get_overall_risk_assessment(self, severity_counts: Dict[str, int]) -> str:
        """Get overall risk assessment based on severity distribution"""
        major_count = severity_counts.get('Major', 0)
        moderate_count = severity_counts.get('Moderate', 0)
        total = sum(severity_counts.values())
        
        if major_count > 0:
            return f"High overall risk - {major_count} major interaction(s) detected"
        elif moderate_count > total * 0.5:
            return f"Moderate overall risk - {moderate_count} moderate interaction(s) detected"
        else:
            return "Low overall risk - mostly minor interactions"
    
    def _get_overall_recommendations(self, severity_counts: Dict[str, int]) -> List[str]:
        """Get overall recommendations based on severity distribution"""
        recommendations = []
        
        major_count = severity_counts.get('Major', 0)
        moderate_count = severity_counts.get('Moderate', 0)
        
        if major_count > 0:
            recommendations.append("Immediate consultation with healthcare provider recommended")
            recommendations.append("Consider alternative medications for major interactions")
        
        if moderate_count > 0:
            recommendations.append("Enhanced monitoring for moderate interactions")
            recommendations.append("Regular follow-up appointments recommended")
        
        if not major_count and not moderate_count:
            recommendations.append("Routine monitoring sufficient for current drug combination")
        
        recommendations.append("Always inform healthcare providers of all medications being taken")
        
        return recommendations
