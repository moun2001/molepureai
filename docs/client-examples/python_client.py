"""
Python Client SDK for Drug Interaction Prediction API

This module provides a convenient Python interface for the Drug Interaction API.
"""

import requests
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time


@dataclass
class Drug:
    """Drug data structure"""
    drug_name: str
    pharmacodynamic_class: str
    logp: float
    therapeutic_index: str
    transporter_interaction: str
    plasma_protein_binding: float
    metabolic_pathways: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request"""
        return {
            'drug_name': self.drug_name,
            'pharmacodynamic_class': self.pharmacodynamic_class,
            'logp': self.logp,
            'therapeutic_index': self.therapeutic_index,
            'transporter_interaction': self.transporter_interaction,
            'plasma_protein_binding': self.plasma_protein_binding,
            'metabolic_pathways': self.metabolic_pathways
        }


@dataclass
class InteractionPrediction:
    """Interaction prediction result"""
    drug_a_name: str
    drug_b_name: str
    severity: str
    confidence: float
    risk_level: str
    clinical_significance: str
    recommendation: str
    probability_distribution: Dict[str, float]


class DrugInteractionAPIError(Exception):
    """Custom exception for API errors"""
    pass


class DrugInteractionClient:
    """Client for Drug Interaction Prediction API"""
    
    def __init__(self, base_url: str = "http://localhost:5000", timeout: int = 120):
        """
        Initialize the client
        
        Args:
            base_url: Base URL of the API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'DrugInteractionClient/1.0.0'
        })
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform basic health check
        
        Returns:
            Health status information
        """
        try:
            response = self.session.get(f"{self.base_url}/", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise DrugInteractionAPIError(f"Health check failed: {str(e)}")
    
    def detailed_health_check(self) -> Dict[str, Any]:
        """
        Perform detailed health check
        
        Returns:
            Detailed health status information
        """
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise DrugInteractionAPIError(f"Detailed health check failed: {str(e)}")
    
    def predict_interactions(self, drugs: List[Drug]) -> List[InteractionPrediction]:
        """
        Predict drug interactions
        
        Args:
            drugs: List of Drug objects to analyze
            
        Returns:
            List of InteractionPrediction objects
        """
        if len(drugs) < 2:
            raise ValueError("At least 2 drugs are required for interaction prediction")
        
        if len(drugs) > 10:
            raise ValueError("Maximum 10 drugs allowed per request")
        
        # Convert drugs to API format
        request_data = {
            'drugs': [drug.to_dict() for drug in drugs]
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/predict-interactions",
                json=request_data,
                timeout=self.timeout
            )
            
            if response.status_code == 400:
                error_data = response.json()
                raise DrugInteractionAPIError(f"Validation error: {error_data.get('error', 'Unknown validation error')}")
            
            response.raise_for_status()
            result = response.json()
            
            # Convert to InteractionPrediction objects
            predictions = []
            for pred in result['predictions']:
                predictions.append(InteractionPrediction(
                    drug_a_name=pred['drug_pair']['drug_a']['name'],
                    drug_b_name=pred['drug_pair']['drug_b']['name'],
                    severity=pred['prediction']['severity'],
                    confidence=pred['prediction']['confidence'],
                    risk_level=pred['prediction']['risk_level'],
                    clinical_significance=pred['clinical_significance'],
                    recommendation=pred['recommendation'],
                    probability_distribution=pred['probability_distribution']
                ))
            
            return predictions
            
        except requests.exceptions.RequestException as e:
            raise DrugInteractionAPIError(f"Prediction request failed: {str(e)}")
    
    def get_api_info(self) -> Dict[str, Any]:
        """
        Get API information
        
        Returns:
            API information and usage guidelines
        """
        try:
            response = self.session.get(f"{self.base_url}/api/info", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise DrugInteractionAPIError(f"API info request failed: {str(e)}")


class DrugInteractionBatchClient(DrugInteractionClient):
    """Extended client with batch processing capabilities"""
    
    def __init__(self, base_url: str = "http://localhost:5000", timeout: int = 120, 
                 rate_limit_delay: float = 0.1):
        """
        Initialize batch client
        
        Args:
            base_url: Base URL of the API
            timeout: Request timeout in seconds
            rate_limit_delay: Delay between requests to avoid rate limiting
        """
        super().__init__(base_url, timeout)
        self.rate_limit_delay = rate_limit_delay
    
    def predict_interactions_batch(self, drug_batches: List[List[Drug]]) -> List[List[InteractionPrediction]]:
        """
        Process multiple batches of drugs
        
        Args:
            drug_batches: List of drug lists to process
            
        Returns:
            List of prediction results for each batch
        """
        results = []
        
        for i, drugs in enumerate(drug_batches):
            try:
                predictions = self.predict_interactions(drugs)
                results.append(predictions)
                
                # Rate limiting delay
                if i < len(drug_batches) - 1:
                    time.sleep(self.rate_limit_delay)
                    
            except DrugInteractionAPIError as e:
                print(f"Batch {i+1} failed: {str(e)}")
                results.append([])
        
        return results


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = DrugInteractionClient("http://localhost:5000")
    
    # Check API health
    try:
        health = client.health_check()
        print(f"API Status: {health['status']}")
    except DrugInteractionAPIError as e:
        print(f"Health check failed: {e}")
        exit(1)
    
    # Create drug objects
    warfarin = Drug(
        drug_name="Warfarin",
        pharmacodynamic_class="Anticoagulant",
        logp=2.7,
        therapeutic_index="NTI",
        transporter_interaction="Substrate: P-gp",
        plasma_protein_binding=99.0,
        metabolic_pathways="Substrate: CYP2C9;CYP3A4"
    )
    
    amiodarone = Drug(
        drug_name="Amiodarone",
        pharmacodynamic_class="Antiarrhythmic",
        logp=7.6,
        therapeutic_index="NTI",
        transporter_interaction="Substrate: P-gp / Inhibitor: P-gp",
        plasma_protein_binding=96.0,
        metabolic_pathways="Substrate: CYP3A4 / Inhibitor: CYP2D6"
    )
    
    # Predict interactions
    try:
        predictions = client.predict_interactions([warfarin, amiodarone])
        
        print(f"\nInteraction Analysis Results:")
        print("=" * 50)
        
        for pred in predictions:
            print(f"\n{pred.drug_a_name} + {pred.drug_b_name}")
            print(f"  Severity: {pred.severity}")
            print(f"  Confidence: {pred.confidence:.1%}")
            print(f"  Risk Level: {pred.risk_level}")
            print(f"  Recommendation: {pred.recommendation}")
            
    except DrugInteractionAPIError as e:
        print(f"Prediction failed: {e}")
