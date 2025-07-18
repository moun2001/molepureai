"""
Demonstration of the Drug Interaction Prediction API

This script shows how to use the API with real drug examples
"""

import requests
import json

def demo_drug_interactions():
    base_url = "http://localhost:5000"
    
    print("🏥 Drug Interaction Prediction API Demo")
    print("=" * 50)
    
    # Example with multiple drugs that might have interactions
    demo_drugs = {
        "drugs": [
            {
                "drug_name": "Warfarin",
                "pharmacodynamic_class": "Anticoagulant",
                "logp": 2.7,
                "therapeutic_index": "NTI",
                "transporter_interaction": "Substrate: P-gp",
                "plasma_protein_binding": 99.0,
                "metabolic_pathways": "Substrate: CYP2C9;CYP3A4"
            },
            {
                "drug_name": "Amiodarone",
                "pharmacodynamic_class": "Antiarrhythmic",
                "logp": 7.6,
                "therapeutic_index": "NTI",
                "transporter_interaction": "Substrate: P-gp / Inhibitor: P-gp",
                "plasma_protein_binding": 96.0,
                "metabolic_pathways": "Substrate: CYP3A4 / Inhibitor: CYP2D6"
            },
            {
                "drug_name": "Simvastatin",
                "pharmacodynamic_class": "Statin",
                "logp": 4.7,
                "therapeutic_index": "Non-NTI",
                "transporter_interaction": "Substrate: OATP1B1",
                "plasma_protein_binding": 95.0,
                "metabolic_pathways": "Substrate: CYP3A4"
            }
        ]
    }
    
    print(f"📋 Analyzing interactions between {len(demo_drugs['drugs'])} drugs:")
    for i, drug in enumerate(demo_drugs['drugs'], 1):
        print(f"  {i}. {drug['drug_name']} ({drug['pharmacodynamic_class']})")
    
    print("\n🔍 Sending request to API...")
    
    try:
        response = requests.post(
            f"{base_url}/predict-interactions",
            json=demo_drugs,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Analysis completed successfully!")
            print(f"\n📊 Summary:")
            print(f"   • Total drug pairs analyzed: {result['drug_pairs_analyzed']}")
            
            summary = result.get('summary', {})
            print(f"   • High risk pairs: {summary.get('high_risk_pairs', 0)}")
            print(f"   • Moderate risk pairs: {summary.get('moderate_risk_pairs', 0)}")
            print(f"   • Low risk pairs: {summary.get('low_risk_pairs', 0)}")
            
            print(f"\n🔬 Detailed Results:")
            print("-" * 50)
            
            for i, prediction in enumerate(result['predictions'], 1):
                drug_a = prediction['drug_pair']['drug_a']
                drug_b = prediction['drug_pair']['drug_b']
                pred_info = prediction['prediction']
                
                print(f"\n{i}. {drug_a['name']} + {drug_b['name']}")
                print(f"   Severity: {pred_info['severity']}")
                print(f"   Confidence: {pred_info['confidence']:.1%}")
                print(f"   Risk Level: {pred_info['risk_level']}")
                print(f"   Clinical Significance: {prediction['clinical_significance']}")
                print(f"   Recommendation: {prediction['recommendation']}")
                
                # Show probability distribution
                prob_dist = prediction.get('probability_distribution', {})
                print(f"   Probability Distribution:")
                for severity, prob in prob_dist.items():
                    print(f"     • {severity}: {prob:.1%}")
            
            return True
            
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_api_info():
    """Display API information"""
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(f"{base_url}/api/info")
        if response.status_code == 200:
            info = response.json()
            print("\n📚 API Information:")
            print(f"   • Name: {info.get('api_name')}")
            print(f"   • Version: {info.get('version')}")
            print(f"   • Description: {info.get('description')}")
            print(f"   • Supported Severity Levels: {', '.join(info.get('supported_severity_levels', []))}")
            
    except Exception as e:
        print(f"Could not retrieve API info: {e}")

if __name__ == "__main__":
    # Show API information
    show_api_info()
    
    # Run the demo
    success = demo_drug_interactions()
    
    if success:
        print(f"\n🎉 Demo completed successfully!")
        print(f"\n💡 Next Steps:")
        print(f"   • The API is ready for production use")
        print(f"   • Deploy using Docker or cloud platforms")
        print(f"   • Integrate with your healthcare applications")
        print(f"   • Use the /predict-interactions endpoint for real-time predictions")
    else:
        print(f"\n⚠️ Demo failed. Please check the server is running.")
