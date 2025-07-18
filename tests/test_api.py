"""
Test script for Drug Interaction Prediction API

Tests the web server functionality with sample data and validates responses.
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:5000"
TIMEOUT = 30

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Model loaded: {data.get('model_loaded')}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

def test_api_info():
    """Test the API info endpoint"""
    print("\n🔍 Testing API info endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/info", timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API info retrieved successfully")
            print(f"   API Name: {data.get('api_name')}")
            print(f"   Version: {data.get('version')}")
            return True
        else:
            print(f"❌ API info failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API info failed: {str(e)}")
        return False

def test_prediction_valid_data():
    """Test prediction with valid drug data"""
    print("\n🔍 Testing prediction with valid data...")
    
    test_data = {
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
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict-interactions",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Prediction successful")
            print(f"   Status: {data.get('status')}")
            print(f"   Drugs analyzed: {data.get('input_drugs_count')}")
            print(f"   Pairs analyzed: {data.get('drug_pairs_analyzed')}")
            
            if data.get('predictions'):
                pred = data['predictions'][0]
                print(f"   First prediction:")
                print(f"     Severity: {pred['prediction']['severity']}")
                print(f"     Confidence: {pred['prediction']['confidence']:.3f}")
                print(f"     Risk Level: {pred['prediction']['risk_level']}")
            
            return True
        else:
            print(f"❌ Prediction failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Prediction failed: {str(e)}")
        return False

def test_prediction_multiple_drugs():
    """Test prediction with multiple drugs"""
    print("\n🔍 Testing prediction with multiple drugs...")
    
    test_data = {
        "drugs": [
            {
                "drug_name": "Drug A",
                "pharmacodynamic_class": "Antibiotic",
                "logp": 2.5,
                "therapeutic_index": "Non-NTI",
                "transporter_interaction": "Substrate: P-gp",
                "plasma_protein_binding": 85.0,
                "metabolic_pathways": "Substrate: CYP3A4"
            },
            {
                "drug_name": "Drug B",
                "pharmacodynamic_class": "Antidepressant",
                "logp": 3.2,
                "therapeutic_index": "Non-NTI",
                "transporter_interaction": "No Transporter",
                "plasma_protein_binding": 92.0,
                "metabolic_pathways": "Substrate: CYP2D6"
            },
            {
                "drug_name": "Drug C",
                "pharmacodynamic_class": "Corticosteroid",
                "logp": 1.8,
                "therapeutic_index": "Non-NTI",
                "transporter_interaction": "Substrate: P-gp",
                "plasma_protein_binding": 78.0,
                "metabolic_pathways": "Substrate: CYP3A4"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict-interactions",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Multiple drug prediction successful")
            print(f"   Drugs analyzed: {data.get('input_drugs_count')}")
            print(f"   Pairs analyzed: {data.get('drug_pairs_analyzed')}")
            
            summary = data.get('summary', {})
            print(f"   High risk pairs: {summary.get('high_risk_pairs', 0)}")
            print(f"   Moderate risk pairs: {summary.get('moderate_risk_pairs', 0)}")
            print(f"   Low risk pairs: {summary.get('low_risk_pairs', 0)}")
            
            return True
        else:
            print(f"❌ Multiple drug prediction failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Multiple drug prediction failed: {str(e)}")
        return False

def test_prediction_invalid_data():
    """Test prediction with invalid data to check error handling"""
    print("\n🔍 Testing prediction with invalid data...")
    
    # Test with missing required field
    invalid_data = {
        "drugs": [
            {
                "drug_name": "Test Drug",
                "pharmacodynamic_class": "Antibiotic",
                # Missing logp field
                "therapeutic_index": "Non-NTI",
                "transporter_interaction": "Substrate: P-gp",
                "plasma_protein_binding": 85.0,
                "metabolic_pathways": "Substrate: CYP3A4"
            },
            {
                "drug_name": "Test Drug 2",
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
            f"{BASE_URL}/predict-interactions",
            json=invalid_data,
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        
        if response.status_code == 400:
            data = response.json()
            print(f"✅ Invalid data properly rejected")
            print(f"   Status: {data.get('status')}")
            print(f"   Error: {data.get('error')}")
            return True
        else:
            print(f"❌ Invalid data not properly handled (status: {response.status_code})")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Invalid data test failed: {str(e)}")
        return False

def test_prediction_insufficient_drugs():
    """Test prediction with insufficient drugs"""
    print("\n🔍 Testing prediction with insufficient drugs...")
    
    insufficient_data = {
        "drugs": [
            {
                "drug_name": "Single Drug",
                "pharmacodynamic_class": "Antibiotic",
                "logp": 2.5,
                "therapeutic_index": "Non-NTI",
                "transporter_interaction": "Substrate: P-gp",
                "plasma_protein_binding": 85.0,
                "metabolic_pathways": "Substrate: CYP3A4"
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/predict-interactions",
            json=insufficient_data,
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        
        if response.status_code == 400:
            data = response.json()
            print(f"✅ Insufficient drugs properly rejected")
            print(f"   Error: {data.get('error')}")
            return True
        else:
            print(f"❌ Insufficient drugs not properly handled (status: {response.status_code})")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Insufficient drugs test failed: {str(e)}")
        return False

def test_404_endpoint():
    """Test 404 handling"""
    print("\n🔍 Testing 404 endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/nonexistent", timeout=TIMEOUT)
        
        if response.status_code == 404:
            print(f"✅ 404 properly handled")
            return True
        else:
            print(f"❌ 404 not properly handled (status: {response.status_code})")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 404 test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("🚀 Starting Drug Interaction API Tests")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health_check),
        ("API Info", test_api_info),
        ("Valid Prediction", test_prediction_valid_data),
        ("Multiple Drugs", test_prediction_multiple_drugs),
        ("Invalid Data", test_prediction_invalid_data),
        ("Insufficient Drugs", test_prediction_insufficient_drugs),
        ("404 Handling", test_404_endpoint)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the server and try again.")
        return False

if __name__ == "__main__":
    print("Drug Interaction Prediction API Test Suite")
    print("Make sure the server is running on http://localhost:5000")
    print()
    
    # Wait a moment for user to start server if needed
    input("Press Enter to start tests (or Ctrl+C to cancel)...")
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
