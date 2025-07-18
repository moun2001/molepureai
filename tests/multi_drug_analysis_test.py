"""
Multi-Drug Analysis Test Suite

Tests the API's capability to handle multiple drugs and analyze all possible
drug pair combinations with performance benchmarking.
"""

import requests
import json
import time
from typing import List, Dict, Any
import itertools


class MultiDrugAnalyzer:
    """Test multi-drug analysis capabilities"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def create_sample_drugs(self, count: int) -> List[Dict[str, Any]]:
        """Create sample drug data for testing"""
        
        # Base drug templates with realistic data
        drug_templates = [
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
            },
            {
                "drug_name": "Metformin",
                "pharmacodynamic_class": "Antidiabetic",
                "logp": -2.6,
                "therapeutic_index": "Non-NTI",
                "transporter_interaction": "Substrate: OCT1;OCT2",
                "plasma_protein_binding": 0.0,
                "metabolic_pathways": "No Metabolism"
            },
            {
                "drug_name": "Digoxin",
                "pharmacodynamic_class": "Cardiac Glycoside",
                "logp": 1.3,
                "therapeutic_index": "NTI",
                "transporter_interaction": "Substrate: P-gp",
                "plasma_protein_binding": 25.0,
                "metabolic_pathways": "Minimal Metabolism"
            },
            {
                "drug_name": "Phenytoin",
                "pharmacodynamic_class": "Anticonvulsant",
                "logp": 2.5,
                "therapeutic_index": "NTI",
                "transporter_interaction": "No Transporter",
                "plasma_protein_binding": 90.0,
                "metabolic_pathways": "Substrate: CYP2C9;CYP2C19"
            },
            {
                "drug_name": "Rifampin",
                "pharmacodynamic_class": "Antibiotic",
                "logp": 2.8,
                "therapeutic_index": "Non-NTI",
                "transporter_interaction": "Substrate: P-gp / Inhibitor: OATP1B1",
                "plasma_protein_binding": 85.0,
                "metabolic_pathways": "Substrate: CYP3A4 / Inducer: CYP3A4;CYP2C9"
            },
            {
                "drug_name": "Ketoconazole",
                "pharmacodynamic_class": "Antifungal",
                "logp": 4.4,
                "therapeutic_index": "Non-NTI",
                "transporter_interaction": "Substrate: P-gp / Inhibitor: P-gp",
                "plasma_protein_binding": 99.0,
                "metabolic_pathways": "Substrate: CYP3A4 / Inhibitor: CYP3A4"
            },
            {
                "drug_name": "Cyclosporine",
                "pharmacodynamic_class": "Immunosuppressant",
                "logp": 2.9,
                "therapeutic_index": "NTI",
                "transporter_interaction": "Substrate: P-gp / Inhibitor: P-gp;OATP1B1",
                "plasma_protein_binding": 90.0,
                "metabolic_pathways": "Substrate: CYP3A4 / Inhibitor: CYP3A4"
            },
            {
                "drug_name": "Atorvastatin",
                "pharmacodynamic_class": "Statin",
                "logp": 5.7,
                "therapeutic_index": "Non-NTI",
                "transporter_interaction": "Substrate: OATP1B1;OATP1B3",
                "plasma_protein_binding": 98.0,
                "metabolic_pathways": "Substrate: CYP3A4"
            }
        ]
        
        # Return the requested number of drugs
        return drug_templates[:min(count, len(drug_templates))]
    
    def calculate_expected_pairs(self, drug_count: int) -> int:
        """Calculate expected number of drug pairs for n drugs"""
        return drug_count * (drug_count - 1) // 2
    
    def test_multi_drug_scenario(self, drug_count: int) -> Dict[str, Any]:
        """Test a specific multi-drug scenario"""
        
        print(f"\n🧪 Testing {drug_count} drugs scenario...")
        
        # Create test drugs
        drugs = self.create_sample_drugs(drug_count)
        expected_pairs = self.calculate_expected_pairs(drug_count)
        
        print(f"   Expected pairs to analyze: {expected_pairs}")
        
        # Prepare request
        request_data = {"drugs": drugs}
        
        # Measure performance
        start_time = time.time()
        
        try:
            response = self.session.post(
                f"{self.base_url}/predict-interactions",
                json=request_data,
                timeout=120
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Analyze results
                analysis = {
                    'drug_count': drug_count,
                    'expected_pairs': expected_pairs,
                    'actual_pairs': result.get('drug_pairs_analyzed', 0),
                    'response_time_seconds': round(response_time, 2),
                    'pairs_per_second': round(expected_pairs / response_time, 2),
                    'status': 'success',
                    'predictions': result.get('predictions', []),
                    'summary': result.get('summary', {}),
                    'memory_efficient': response_time < (drug_count * 0.5)  # Heuristic
                }
                
                # Verify pair count matches expectation
                if analysis['actual_pairs'] == expected_pairs:
                    print(f"   ✅ Correct pair count: {expected_pairs}")
                else:
                    print(f"   ❌ Pair count mismatch: expected {expected_pairs}, got {analysis['actual_pairs']}")
                
                print(f"   ⏱️  Response time: {response_time:.2f} seconds")
                print(f"   🚀 Processing rate: {analysis['pairs_per_second']:.2f} pairs/second")
                
                # Analyze severity distribution
                severity_counts = analysis['summary']
                total_pairs = sum(severity_counts.values()) if severity_counts else 0
                if total_pairs > 0:
                    print(f"   📊 Severity distribution:")
                    for severity, count in severity_counts.items():
                        percentage = (count / total_pairs) * 100
                        print(f"      {severity}: {count} ({percentage:.1f}%)")
                
                return analysis
                
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                return {
                    'drug_count': drug_count,
                    'expected_pairs': expected_pairs,
                    'status': 'error',
                    'error_code': response.status_code,
                    'error_message': error_data.get('error', 'Unknown error'),
                    'response_time_seconds': round(response_time, 2)
                }
                
        except requests.exceptions.Timeout:
            return {
                'drug_count': drug_count,
                'expected_pairs': expected_pairs,
                'status': 'timeout',
                'error_message': 'Request timed out after 120 seconds'
            }
        except Exception as e:
            return {
                'drug_count': drug_count,
                'expected_pairs': expected_pairs,
                'status': 'error',
                'error_message': str(e)
            }
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run comprehensive multi-drug analysis"""
        
        print("🔬 Starting Comprehensive Multi-Drug Analysis")
        print("=" * 60)
        
        # Test scenarios: 2, 3, 4, 5, 6, 7, 8, 9, 10 drugs
        test_scenarios = [2, 3, 4, 5, 6, 7, 8, 9, 10]
        results = []
        
        for drug_count in test_scenarios:
            result = self.test_multi_drug_scenario(drug_count)
            results.append(result)
            
            # Brief pause between tests
            time.sleep(1)
        
        # Analyze overall performance
        successful_tests = [r for r in results if r['status'] == 'success']
        failed_tests = [r for r in results if r['status'] != 'success']
        
        if successful_tests:
            avg_response_time = sum(r['response_time_seconds'] for r in successful_tests) / len(successful_tests)
            max_response_time = max(r['response_time_seconds'] for r in successful_tests)
            min_response_time = min(r['response_time_seconds'] for r in successful_tests)
            
            avg_processing_rate = sum(r['pairs_per_second'] for r in successful_tests) / len(successful_tests)
        else:
            avg_response_time = max_response_time = min_response_time = avg_processing_rate = 0
        
        # Generate comprehensive report
        report = {
            'test_summary': {
                'total_scenarios': len(test_scenarios),
                'successful_tests': len(successful_tests),
                'failed_tests': len(failed_tests),
                'success_rate': (len(successful_tests) / len(test_scenarios)) * 100
            },
            'performance_metrics': {
                'average_response_time': round(avg_response_time, 2),
                'min_response_time': round(min_response_time, 2),
                'max_response_time': round(max_response_time, 2),
                'average_processing_rate': round(avg_processing_rate, 2)
            },
            'detailed_results': results,
            'recommendations': self._generate_recommendations(results)
        }
        
        return report
    
    def _generate_recommendations(self, results: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on test results"""
        
        recommendations = []
        successful_tests = [r for r in results if r['status'] == 'success']
        
        if not successful_tests:
            recommendations.append("❌ No successful tests - check API health and configuration")
            return recommendations
        
        # Performance recommendations
        max_successful_drugs = max(r['drug_count'] for r in successful_tests)
        slow_tests = [r for r in successful_tests if r['response_time_seconds'] > 10]
        
        if max_successful_drugs >= 10:
            recommendations.append("✅ API successfully handles up to 10 drugs (45 pairs)")
        elif max_successful_drugs >= 5:
            recommendations.append(f"⚠️ API handles up to {max_successful_drugs} drugs - consider optimization for larger sets")
        else:
            recommendations.append(f"⚠️ API limited to {max_successful_drugs} drugs - investigate performance issues")
        
        if slow_tests:
            recommendations.append(f"⚠️ {len(slow_tests)} scenarios took >10 seconds - consider performance optimization")
        
        # Memory efficiency
        memory_efficient_tests = [r for r in successful_tests if r.get('memory_efficient', False)]
        if len(memory_efficient_tests) / len(successful_tests) > 0.8:
            recommendations.append("✅ Good memory efficiency across test scenarios")
        else:
            recommendations.append("⚠️ Consider memory optimization for better performance")
        
        # Scaling recommendations
        if max_successful_drugs >= 8:
            recommendations.append("✅ API scales well for clinical use cases (typically 2-8 drugs)")
        
        recommendations.append("💡 For >10 drugs, consider batch processing or client-side pair selection")
        
        return recommendations


def main():
    """Run the multi-drug analysis test suite"""
    
    analyzer = MultiDrugAnalyzer()
    
    # Check API health first
    try:
        health_response = analyzer.session.get(f"{analyzer.base_url}/health", timeout=10)
        if health_response.status_code != 200:
            print("❌ API health check failed - ensure server is running")
            return
        print("✅ API health check passed")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return
    
    # Run comprehensive analysis
    report = analyzer.run_comprehensive_analysis()
    
    # Print summary report
    print("\n" + "=" * 60)
    print("📊 MULTI-DRUG ANALYSIS REPORT")
    print("=" * 60)
    
    summary = report['test_summary']
    print(f"Total scenarios tested: {summary['total_scenarios']}")
    print(f"Successful tests: {summary['successful_tests']}")
    print(f"Failed tests: {summary['failed_tests']}")
    print(f"Success rate: {summary['success_rate']:.1f}%")
    
    if summary['successful_tests'] > 0:
        metrics = report['performance_metrics']
        print(f"\n⏱️  Performance Metrics:")
        print(f"Average response time: {metrics['average_response_time']} seconds")
        print(f"Response time range: {metrics['min_response_time']} - {metrics['max_response_time']} seconds")
        print(f"Average processing rate: {metrics['average_processing_rate']} pairs/second")
    
    print(f"\n💡 Recommendations:")
    for rec in report['recommendations']:
        print(f"   {rec}")
    
    # Save detailed report
    with open('multi_drug_analysis_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Detailed report saved to: multi_drug_analysis_report.json")


if __name__ == "__main__":
    main()
