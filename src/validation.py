"""
Input Validation Module for Drug Interaction Prediction API

Provides comprehensive validation for drug data input, ensuring data quality
and proper error handling for the prediction service.
"""

import re
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class InputValidator:
    """Handles validation of input data for drug interaction prediction"""
    
    def __init__(self):
        """Initialize the validator with validation rules"""
        
        # Required fields for each drug
        self.required_fields = [
            'drug_name',
            'pharmacodynamic_class',
            'logp',
            'therapeutic_index',
            'transporter_interaction',
            'plasma_protein_binding',
            'metabolic_pathways'
        ]
        
        # Valid ranges for numerical fields
        self.numerical_ranges = {
            'logp': {'min': -10.0, 'max': 15.0, 'type': float},
            'plasma_protein_binding': {'min': 0.0, 'max': 100.0, 'type': float}
        }
        
        # Valid values for categorical fields (common ones)
        self.valid_therapeutic_indices = ['NTI', 'Non-NTI']
        
        # Common pharmacodynamic classes (for validation warnings)
        self.common_drug_classes = [
            'Antibiotic', 'Antidepressant', 'Antidiabetic', 'Antifungal',
            'Antihistamine', 'Antimalarial', 'Antipsychotic', 'Corticosteroid',
            'Diuretic', 'Tyrosine Kinase Inhibitor', 'Immunosuppressant',
            'Beta-2 Agonist', 'Antineoplastic', 'Opioid Analgesic',
            'Androgen Synthesis Inhibitor', 'Antiandrogen', 'Antiprotozoal'
        ]
        
        logger.info("✅ InputValidator initialized")
    
    def validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the complete input data structure
        
        Args:
            data: Input data dictionary
            
        Returns:
            Dictionary with validation results
        """
        try:
            errors = []
            warnings = []
            
            # Check if data is a dictionary
            if not isinstance(data, dict):
                return {
                    'valid': False,
                    'errors': ['Input must be a JSON object'],
                    'warnings': []
                }
            
            # Check for 'drugs' key
            if 'drugs' not in data:
                errors.append("Missing 'drugs' key in input data")
                return {
                    'valid': False,
                    'errors': errors,
                    'warnings': warnings
                }
            
            drugs = data['drugs']
            
            # Check if drugs is a list
            if not isinstance(drugs, list):
                errors.append("'drugs' must be a list")
                return {
                    'valid': False,
                    'errors': errors,
                    'warnings': warnings
                }
            
            # Check minimum number of drugs
            if len(drugs) < 2:
                errors.append("At least 2 drugs are required for interaction analysis")
            
            # Check maximum number of drugs (to prevent excessive computation)
            if len(drugs) > 10:
                warnings.append(f"Large number of drugs ({len(drugs)}) may result in slow processing")
            
            # Validate each drug
            for i, drug in enumerate(drugs):
                drug_errors, drug_warnings = self._validate_single_drug(drug, i)
                errors.extend(drug_errors)
                warnings.extend(drug_warnings)
            
            # Check for duplicate drug names
            drug_names = [drug.get('drug_name', '').lower() for drug in drugs if 'drug_name' in drug]
            if len(drug_names) != len(set(drug_names)):
                warnings.append("Duplicate drug names detected - this may affect interaction analysis")
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings,
                'drugs_count': len(drugs),
                'pairs_to_analyze': len(drugs) * (len(drugs) - 1) // 2
            }
            
        except Exception as e:
            logger.error(f"❌ Error in validate_input: {str(e)}")
            return {
                'valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'warnings': []
            }
    
    def _validate_single_drug(self, drug: Dict[str, Any], index: int) -> Tuple[List[str], List[str]]:
        """
        Validate a single drug entry
        
        Args:
            drug: Drug data dictionary
            index: Index of the drug in the list
            
        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []
        drug_prefix = f"Drug {index + 1}"
        
        # Check if drug is a dictionary
        if not isinstance(drug, dict):
            errors.append(f"{drug_prefix}: Must be an object")
            return errors, warnings
        
        # Check required fields
        for field in self.required_fields:
            if field not in drug:
                errors.append(f"{drug_prefix}: Missing required field '{field}'")
            elif drug[field] is None or drug[field] == '':
                errors.append(f"{drug_prefix}: Field '{field}' cannot be empty")
        
        # Validate specific fields
        if 'drug_name' in drug:
            name_errors, name_warnings = self._validate_drug_name(drug['drug_name'], drug_prefix)
            errors.extend(name_errors)
            warnings.extend(name_warnings)
        
        if 'logp' in drug:
            logp_errors = self._validate_numerical_field(drug['logp'], 'logp', drug_prefix)
            errors.extend(logp_errors)
        
        if 'plasma_protein_binding' in drug:
            ppb_errors = self._validate_numerical_field(drug['plasma_protein_binding'], 'plasma_protein_binding', drug_prefix)
            errors.extend(ppb_errors)
        
        if 'therapeutic_index' in drug:
            ti_warnings = self._validate_therapeutic_index(drug['therapeutic_index'], drug_prefix)
            warnings.extend(ti_warnings)
        
        if 'pharmacodynamic_class' in drug:
            class_warnings = self._validate_pharmacodynamic_class(drug['pharmacodynamic_class'], drug_prefix)
            warnings.extend(class_warnings)
        
        # Validate text fields are not too long
        text_fields = ['drug_name', 'pharmacodynamic_class', 'transporter_interaction', 'metabolic_pathways']
        for field in text_fields:
            if field in drug and isinstance(drug[field], str) and len(drug[field]) > 200:
                warnings.append(f"{drug_prefix}: Field '{field}' is unusually long ({len(drug[field])} characters)")
        
        return errors, warnings
    
    def _validate_drug_name(self, name: Any, drug_prefix: str) -> Tuple[List[str], List[str]]:
        """Validate drug name"""
        errors = []
        warnings = []
        
        if not isinstance(name, str):
            errors.append(f"{drug_prefix}: Drug name must be a string")
            return errors, warnings
        
        name = name.strip()
        if len(name) < 2:
            errors.append(f"{drug_prefix}: Drug name too short")
        elif len(name) > 100:
            warnings.append(f"{drug_prefix}: Drug name is unusually long")
        
        # Check for suspicious characters
        if re.search(r'[<>{}[\]\\]', name):
            warnings.append(f"{drug_prefix}: Drug name contains unusual characters")
        
        return errors, warnings
    
    def _validate_numerical_field(self, value: Any, field_name: str, drug_prefix: str) -> List[str]:
        """Validate numerical fields"""
        errors = []
        
        # Check if value can be converted to number
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            errors.append(f"{drug_prefix}: Field '{field_name}' must be a valid number")
            return errors
        
        # Check range if defined
        if field_name in self.numerical_ranges:
            range_info = self.numerical_ranges[field_name]
            if num_value < range_info['min'] or num_value > range_info['max']:
                errors.append(f"{drug_prefix}: Field '{field_name}' value {num_value} is outside valid range [{range_info['min']}, {range_info['max']}]")
        
        # Check for extreme values
        if abs(num_value) > 1000:
            errors.append(f"{drug_prefix}: Field '{field_name}' has an extreme value ({num_value})")
        
        return errors
    
    def _validate_therapeutic_index(self, value: Any, drug_prefix: str) -> List[str]:
        """Validate therapeutic index"""
        warnings = []
        
        if not isinstance(value, str):
            return warnings
        
        if value not in self.valid_therapeutic_indices:
            warnings.append(f"{drug_prefix}: Therapeutic index '{value}' is not a standard value (expected: {', '.join(self.valid_therapeutic_indices)})")
        
        return warnings
    
    def _validate_pharmacodynamic_class(self, value: Any, drug_prefix: str) -> List[str]:
        """Validate pharmacodynamic class"""
        warnings = []
        
        if not isinstance(value, str):
            return warnings
        
        if value not in self.common_drug_classes:
            warnings.append(f"{drug_prefix}: Pharmacodynamic class '{value}' is not commonly recognized - will be mapped to 'Other'")
        
        return warnings
    
    def get_validation_schema(self) -> Dict[str, Any]:
        """
        Get the validation schema for API documentation
        
        Returns:
            Dictionary describing the expected input format
        """
        return {
            'type': 'object',
            'required': ['drugs'],
            'properties': {
                'drugs': {
                    'type': 'array',
                    'minItems': 2,
                    'maxItems': 10,
                    'items': {
                        'type': 'object',
                        'required': self.required_fields,
                        'properties': {
                            'drug_name': {
                                'type': 'string',
                                'minLength': 2,
                                'maxLength': 100,
                                'description': 'Name of the drug'
                            },
                            'pharmacodynamic_class': {
                                'type': 'string',
                                'description': 'Pharmacodynamic class of the drug',
                                'examples': self.common_drug_classes[:5]
                            },
                            'logp': {
                                'type': 'number',
                                'minimum': self.numerical_ranges['logp']['min'],
                                'maximum': self.numerical_ranges['logp']['max'],
                                'description': 'Lipophilicity (LogP) value'
                            },
                            'therapeutic_index': {
                                'type': 'string',
                                'enum': self.valid_therapeutic_indices,
                                'description': 'Therapeutic index classification'
                            },
                            'transporter_interaction': {
                                'type': 'string',
                                'description': 'Transporter interaction information'
                            },
                            'plasma_protein_binding': {
                                'type': 'number',
                                'minimum': self.numerical_ranges['plasma_protein_binding']['min'],
                                'maximum': self.numerical_ranges['plasma_protein_binding']['max'],
                                'description': 'Plasma protein binding percentage'
                            },
                            'metabolic_pathways': {
                                'type': 'string',
                                'description': 'Metabolic pathway information'
                            }
                        }
                    }
                }
            }
        }
