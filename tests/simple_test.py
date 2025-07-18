"""
Simple test script to verify the Drug Interaction API is working
"""

import requests
import json

def test_api():
    base_url = "http://localhost:5000"
    
    # Test health check
    print("Testing health check...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test prediction
    print("\nTesting prediction...")
    test_data = {
        "drugs": [
            {
                "drug_name": "Test Drug A",
                "pharmacodynamic_class": "Antibiotic",
                "logp": 2.5,
                "therapeutic_index": "Non-NTI",
                "transporter_interaction": "Substrate: P-gp",
                "plasma_protein_binding": 85.0,
                "metabolic_pathways": "Substrate: CYP3A4"
            },
            {
                "drug_name": "Test Drug B",
                "pharmacodynamic_class": "Antidepressant",
                "logp": 3.2,
                "therapeutic_index": "Non-NTI",
                "transporter_interaction": "No Transporter",
                "plasma_protein_binding": 92.0,
                "metabolic_pathways": "Substrate: CYP2D6"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{base_url}/predict-interactions",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Prediction successful")
            print(f"Status: {result.get('status')}")
            print(f"Drugs analyzed: {result.get('input_drugs_count')}")
            print(f"Pairs analyzed: {result.get('drug_pairs_analyzed')}")
            
            if result.get('predictions'):
                pred = result['predictions'][0]
                print(f"First prediction:")
                print(f"  Severity: {pred['prediction']['severity']}")
                print(f"  Confidence: {pred['prediction']['confidence']:.3f}")
                print(f"  Risk Level: {pred['prediction']['risk_level']}")
                print(f"  Recommendation: {pred['recommendation']}")
            
            return True
        else:
            print(f"❌ Prediction failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Simple Drug Interaction API Test")
    print("=" * 40)
    
    success = test_api()
    
    if success:
        print("\n🎉 All tests passed! API is working correctly.")
    else:
        print("\n⚠️ Tests failed. Please check the server.")
