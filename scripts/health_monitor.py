#!/usr/bin/env python3
"""
Health Monitoring Script for Drug Interaction API

This script monitors the API health, performance, and system resources.
Can be run as a cron job or standalone monitoring service.
"""

import requests
import json
import time
import psutil
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, List
import argparse


class HealthMonitor:
    """Comprehensive health monitoring for the Drug Interaction API"""
    
    def __init__(self, api_url: str = "http://localhost:5000", 
                 log_file: str = "/var/log/drug-api/monitor.log"):
        self.api_url = api_url.rstrip('/')
        self.log_file = log_file
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def check_api_health(self) -> Dict[str, Any]:
        """Check API health endpoints"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'basic_health': False,
            'detailed_health': False,
            'response_times': {},
            'errors': []
        }
        
        try:
            # Basic health check
            start_time = time.time()
            response = requests.get(f"{self.api_url}/", timeout=10)
            health_status['response_times']['basic'] = time.time() - start_time
            
            if response.status_code == 200:
                health_status['basic_health'] = True
                basic_data = response.json()
                health_status['model_loaded'] = basic_data.get('model_loaded', False)
            else:
                health_status['errors'].append(f"Basic health check failed: {response.status_code}")
                
        except Exception as e:
            health_status['errors'].append(f"Basic health check error: {str(e)}")
        
        try:
            # Detailed health check
            start_time = time.time()
            response = requests.get(f"{self.api_url}/health", timeout=10)
            health_status['response_times']['detailed'] = time.time() - start_time
            
            if response.status_code == 200:
                health_status['detailed_health'] = True
                detailed_data = response.json()
                health_status['service_checks'] = detailed_data.get('checks', {})
            else:
                health_status['errors'].append(f"Detailed health check failed: {response.status_code}")
                
        except Exception as e:
            health_status['errors'].append(f"Detailed health check error: {str(e)}")
        
        return health_status
    
    def test_api_functionality(self) -> Dict[str, Any]:
        """Test API functionality with a sample prediction"""
        test_status = {
            'timestamp': datetime.now().isoformat(),
            'prediction_test': False,
            'response_time': 0,
            'errors': []
        }
        
        # Sample test data
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
            start_time = time.time()
            response = requests.post(
                f"{self.api_url}/predict-interactions",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            test_status['response_time'] = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success' and result.get('drug_pairs_analyzed') == 1:
                    test_status['prediction_test'] = True
                else:
                    test_status['errors'].append("Prediction test returned unexpected result")
            else:
                test_status['errors'].append(f"Prediction test failed: {response.status_code}")
                
        except Exception as e:
            test_status['errors'].append(f"Prediction test error: {str(e)}")
        
        return test_status
    
    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None,
                'available_memory_gb': psutil.virtual_memory().available / (1024**3),
                'disk_free_gb': psutil.disk_usage('/').free / (1024**3)
            }
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': f"Failed to get system resources: {str(e)}"
            }
    
    def check_api_performance(self) -> Dict[str, Any]:
        """Check API performance with multiple requests"""
        performance_status = {
            'timestamp': datetime.now().isoformat(),
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0,
            'min_response_time': float('inf'),
            'max_response_time': 0,
            'errors': []
        }
        
        # Test with 5 concurrent-ish requests
        response_times = []
        
        for i in range(5):
            try:
                start_time = time.time()
                response = requests.get(f"{self.api_url}/", timeout=10)
                response_time = time.time() - start_time
                
                performance_status['total_requests'] += 1
                
                if response.status_code == 200:
                    performance_status['successful_requests'] += 1
                    response_times.append(response_time)
                    performance_status['min_response_time'] = min(performance_status['min_response_time'], response_time)
                    performance_status['max_response_time'] = max(performance_status['max_response_time'], response_time)
                else:
                    performance_status['failed_requests'] += 1
                    performance_status['errors'].append(f"Request {i+1} failed: {response.status_code}")
                    
            except Exception as e:
                performance_status['failed_requests'] += 1
                performance_status['errors'].append(f"Request {i+1} error: {str(e)}")
            
            # Small delay between requests
            time.sleep(0.1)
        
        if response_times:
            performance_status['average_response_time'] = sum(response_times) / len(response_times)
        else:
            performance_status['min_response_time'] = 0
        
        return performance_status
    
    def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        self.logger.info("Starting health check...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'api_health': self.check_api_health(),
            'functionality_test': self.test_api_functionality(),
            'system_resources': self.check_system_resources(),
            'performance_test': self.check_api_performance()
        }
        
        # Overall health assessment
        overall_healthy = (
            report['api_health']['basic_health'] and
            report['api_health']['detailed_health'] and
            report['functionality_test']['prediction_test'] and
            report['performance_test']['successful_requests'] >= 4
        )
        
        report['overall_status'] = 'HEALTHY' if overall_healthy else 'UNHEALTHY'
        
        # Log summary
        if overall_healthy:
            self.logger.info("✅ Overall health check: HEALTHY")
        else:
            self.logger.warning("❌ Overall health check: UNHEALTHY")
            
        # Log specific issues
        for check_name, check_data in report.items():
            if isinstance(check_data, dict) and 'errors' in check_data:
                for error in check_data['errors']:
                    self.logger.error(f"{check_name}: {error}")
        
        return report
    
    def save_report(self, report: Dict[str, Any], output_file: str = None):
        """Save health report to file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"/var/log/drug-api/health_report_{timestamp}.json"
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Health report saved to: {output_file}")
        return output_file
    
    def check_alerts(self, report: Dict[str, Any]) -> List[str]:
        """Check for alert conditions"""
        alerts = []
        
        # API health alerts
        if not report['api_health']['basic_health']:
            alerts.append("CRITICAL: Basic API health check failed")
        
        if not report['api_health']['detailed_health']:
            alerts.append("CRITICAL: Detailed API health check failed")
        
        if not report['functionality_test']['prediction_test']:
            alerts.append("CRITICAL: API prediction functionality failed")
        
        # Performance alerts
        perf = report['performance_test']
        if perf['failed_requests'] > 1:
            alerts.append(f"WARNING: {perf['failed_requests']} out of {perf['total_requests']} requests failed")
        
        if perf['average_response_time'] > 5.0:
            alerts.append(f"WARNING: High average response time: {perf['average_response_time']:.2f}s")
        
        # System resource alerts
        sys_res = report['system_resources']
        if 'cpu_percent' in sys_res and sys_res['cpu_percent'] > 80:
            alerts.append(f"WARNING: High CPU usage: {sys_res['cpu_percent']:.1f}%")
        
        if 'memory_percent' in sys_res and sys_res['memory_percent'] > 80:
            alerts.append(f"WARNING: High memory usage: {sys_res['memory_percent']:.1f}%")
        
        if 'disk_percent' in sys_res and sys_res['disk_percent'] > 80:
            alerts.append(f"WARNING: High disk usage: {sys_res['disk_percent']:.1f}%")
        
        return alerts


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Drug Interaction API Health Monitor')
    parser.add_argument('--api-url', default='http://localhost:5000', 
                       help='API base URL (default: http://localhost:5000)')
    parser.add_argument('--log-file', default='/var/log/drug-api/monitor.log',
                       help='Log file path (default: /var/log/drug-api/monitor.log)')
    parser.add_argument('--output-file', help='Output file for health report (optional)')
    parser.add_argument('--alerts-only', action='store_true',
                       help='Only show alerts, suppress normal output')
    
    args = parser.parse_args()
    
    # Create monitor instance
    monitor = HealthMonitor(api_url=args.api_url, log_file=args.log_file)
    
    # Generate health report
    report = monitor.generate_health_report()
    
    # Save report
    report_file = monitor.save_report(report, args.output_file)
    
    # Check for alerts
    alerts = monitor.check_alerts(report)
    
    if alerts:
        print("\n🚨 ALERTS:")
        for alert in alerts:
            print(f"   {alert}")
    elif not args.alerts_only:
        print(f"\n✅ No alerts. Overall status: {report['overall_status']}")
        print(f"📄 Full report saved to: {report_file}")
    
    # Exit with error code if unhealthy
    if report['overall_status'] != 'HEALTHY':
        sys.exit(1)


if __name__ == "__main__":
    main()
