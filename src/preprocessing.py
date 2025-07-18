"""
Data Preprocessing Module for Drug Interaction Prediction

Handles transformation of drug data into the format expected by the trained model.
Uses the preprocessing configuration generated during model training.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import logging
from preprocessing_config import (
    CATEGORICAL_MAPPINGS, 
    FEATURE_COLUMNS, 
    NUMERICAL_STATS,
    PERCENTAGE_COLUMNS,
    ENGINEERED_FEATURES
)

logger = logging.getLogger(__name__)

class DrugDataPreprocessor:
    """Handles preprocessing of drug data for model prediction"""
    
    def __init__(self):
        """Initialize the preprocessor with configuration"""
        self.categorical_mappings = CATEGORICAL_MAPPINGS
        self.feature_columns = FEATURE_COLUMNS
        self.numerical_stats = NUMERICAL_STATS
        self.percentage_columns = PERCENTAGE_COLUMNS
        self.engineered_features = ENGINEERED_FEATURES
        
        logger.info("✅ DrugDataPreprocessor initialized")
    
    def preprocess_drug_pair(self, drug_a: Dict[str, Any], drug_b: Dict[str, Any]) -> np.ndarray:
        """
        Preprocess a pair of drugs for model prediction
        
        Args:
            drug_a: Dictionary containing drug A characteristics
            drug_b: Dictionary containing drug B characteristics
            
        Returns:
            numpy array with preprocessed features in the correct order
        """
        try:
            # Create a dictionary to store all features
            features = {}
            
            # Extract basic numerical features
            features['LogP_A'] = float(drug_a['logp'])
            features['LogP_B'] = float(drug_b['logp'])
            features['Plasma_Protein_Binding_A'] = float(drug_a['plasma_protein_binding'])
            features['Plasma_Protein_Binding_B'] = float(drug_b['plasma_protein_binding'])
            
            # Engineer additional features
            features['LogP_diff'] = features['LogP_A'] - features['LogP_B']
            features['LogP_ratio'] = features['LogP_A'] / features['LogP_B'] if features['LogP_B'] != 0 else 0
            features['Protein_Binding_diff'] = features['Plasma_Protein_Binding_A'] - features['Plasma_Protein_Binding_B']
            features['Protein_Binding_avg'] = (features['Plasma_Protein_Binding_A'] + features['Plasma_Protein_Binding_B']) / 2
            
            # Process categorical features
            self._add_categorical_features(features, drug_a, drug_b)
            
            # Convert to feature vector in the correct order
            feature_vector = self._create_feature_vector(features)
            
            return feature_vector
            
        except Exception as e:
            logger.error(f"❌ Error preprocessing drug pair: {str(e)}")
            raise
    
    def _add_categorical_features(self, features: Dict[str, float], drug_a: Dict[str, Any], drug_b: Dict[str, Any]):
        """Add one-hot encoded categorical features"""
        
        # Map drug data to categorical fields
        categorical_data = {
            'Pharmacodynamic_Class_A': drug_a.get('pharmacodynamic_class', ''),
            'Pharmacodynamic_Class_B': drug_b.get('pharmacodynamic_class', ''),
            'Therapeutic_Index_A': drug_a.get('therapeutic_index', ''),
            'Therapeutic_Index_B': drug_b.get('therapeutic_index', ''),
            'Transporter_Interaction_A': drug_a.get('transporter_interaction', ''),
            'Transporter_Interaction_B': drug_b.get('transporter_interaction', ''),
            'Metabolic_Pathways_A': drug_a.get('metabolic_pathways', ''),
            'Metabolic_Pathways_B': drug_b.get('metabolic_pathways', '')
        }
        
        # Process each categorical field
        for field_name, value in categorical_data.items():
            if field_name in self.categorical_mappings:
                categories = self.categorical_mappings[field_name]
                
                # One-hot encode
                for category in categories:
                    feature_name = f"{field_name}_{category}"
                    if category == 'Other':
                        # 'Other' is 1 if the value is not in the known categories
                        features[feature_name] = 1.0 if value not in categories[:-1] else 0.0
                    else:
                        # Regular category matching
                        features[feature_name] = 1.0 if value == category else 0.0
    
    def _create_feature_vector(self, features: Dict[str, float]) -> np.ndarray:
        """Create feature vector in the exact order expected by the model"""
        
        feature_vector = []
        
        for feature_name in self.feature_columns:
            if feature_name in features:
                feature_vector.append(features[feature_name])
            else:
                # If feature is missing, use 0 (should not happen with proper preprocessing)
                logger.warning(f"⚠️ Missing feature: {feature_name}, using 0")
                feature_vector.append(0.0)
        
        return np.array(feature_vector).reshape(1, -1)
    
    def validate_drug_data(self, drug: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate that drug data contains all required fields and values are in valid ranges
        
        Args:
            drug: Dictionary containing drug characteristics
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Required fields
        required_fields = [
            'drug_name', 'pharmacodynamic_class', 'logp', 'therapeutic_index',
            'transporter_interaction', 'plasma_protein_binding', 'metabolic_pathways'
        ]
        
        # Check for missing fields
        for field in required_fields:
            if field not in drug or drug[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Validate numerical ranges
        if 'logp' in drug:
            try:
                logp = float(drug['logp'])
                stats = self.numerical_stats.get('LogP_A', {})
                if 'min' in stats and 'max' in stats:
                    if logp < stats['min'] - 2 or logp > stats['max'] + 2:  # Allow some tolerance
                        errors.append(f"LogP value {logp} is outside expected range [{stats['min']}, {stats['max']}]")
            except (ValueError, TypeError):
                errors.append("LogP must be a valid number")
        
        if 'plasma_protein_binding' in drug:
            try:
                ppb = float(drug['plasma_protein_binding'])
                if ppb < 0 or ppb > 100:
                    errors.append("Plasma protein binding must be between 0 and 100")
            except (ValueError, TypeError):
                errors.append("Plasma protein binding must be a valid number")
        
        # Validate categorical values (warn but don't fail for unknown categories)
        categorical_fields = {
            'pharmacodynamic_class': 'Pharmacodynamic_Class_A',
            'therapeutic_index': 'Therapeutic_Index_A',
            'transporter_interaction': 'Transporter_Interaction_A',
            'metabolic_pathways': 'Metabolic_Pathways_A'
        }
        
        for field, mapping_key in categorical_fields.items():
            if field in drug and drug[field]:
                known_values = self.categorical_mappings.get(mapping_key, [])
                if known_values and drug[field] not in known_values:
                    # This is just a warning - unknown categories will be mapped to 'Other'
                    logger.warning(f"⚠️ Unknown {field}: '{drug[field]}' will be mapped to 'Other'")
        
        return len(errors) == 0, errors
    
    def get_feature_info(self) -> Dict[str, Any]:
        """Get information about the features used by the model"""
        return {
            'total_features': len(self.feature_columns),
            'numerical_features': ['LogP_A', 'LogP_B', 'Plasma_Protein_Binding_A', 'Plasma_Protein_Binding_B'] + self.engineered_features,
            'categorical_features': list(self.categorical_mappings.keys()),
            'engineered_features': self.engineered_features,
            'feature_order': self.feature_columns
        }
