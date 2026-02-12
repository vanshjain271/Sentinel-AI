"""
5G NAS (Non-Access Stratum) Control Plane Analyzer
"""
import struct
import logging

class NASAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 5G NAS message types
        self.nas_message_types = {
            0x41: 'Registration Request',
            0x42: 'Registration Accept',
            0x44: 'Registration Complete',
            0x45: 'Deregistration Request',
            0x46: 'Deregistration Accept',
            0x61: 'Service Request',
            0x62: 'Service Accept',
            0x63: 'Service Reject',
            0x64: 'Service Complete',
            0x6d: 'Configuration Update Command',
            0x70: 'Authentication Request',
            0x71: 'Authentication Response',
            0x72: 'Authentication Reject',
            0x73: 'Authentication Failure',
            0x74: 'Authentication Result',
            0x75: 'Identity Request',
            0x76: 'Identity Response',
            0x7e: 'Authentication Failure'
        }
        
        # Attack signatures
        self.attack_patterns = {
            'registration_storm': {'message': 0x41, 'threshold': 100, 'window': 1},
            'auth_failure_attack': {'message': 0x73, 'threshold': 10, 'window': 1},
            'service_request_flood': {'message': 0x61, 'threshold': 50, 'window': 1}
        }
        
        # Tracking
        self.message_counts = {}
        self.anomalies_detected = []
    
    def analyze_nas_packet(self, packet_data):
        """Analyze 5G NAS messages for security threats"""
        if len(packet_data) < 3:
            return None
        
        message_type = packet_data[0]
        security_header_type = (packet_data[1] & 0x0F)
        
        analysis = {
            'message_type': self.nas_message_types.get(message_type, f'Unknown (0x{message_type:02x})'),
            'security_protected': security_header_type != 0,
            'anomalies': [],
            'threat_level': 'low',
            'recommended_action': 'none'
        }
        
        # Update counts
        key = f"{message_type:02x}"
        self.message_counts[key] = self.message_counts.get(key, 0) + 1
        
        # Check for attack patterns
        for attack_name, pattern in self.attack_patterns.items():
            if message_type == pattern['message']:
                count = self._get_recent_count(key, pattern['window'])
                if count > pattern['threshold']:
                    analysis['anomalies'].append(f"Potential {attack_name.replace('_', ' ')}")
                    analysis['threat_level'] = 'high'
                    analysis['recommended_action'] = 'alert_and_throttle'
        
        # Specific anomaly checks
        if message_type == 0x73:  # Authentication Failure
            cause_code = packet_data[2] if len(packet_data) > 2 else 0
            if cause_code in [21, 22, 23]:  # Specific failure causes
                analysis['anomalies'].append(f"Authentication failure with cause {cause_code}")
                analysis['threat_level'] = 'medium'
        
        elif message_type == 0x41:  # Registration Request
            # Check for suspicious registration attempts
            if len(packet_data) > 10:
                # Check for abnormal parameters
                analysis['threat_level'] = 'low'  # Default
        
        # Update overall threat level
        if analysis['anomalies']:
            if analysis['threat_level'] == 'low':
                analysis['threat_level'] = 'medium'
        
        return analysis
    
    def _get_recent_count(self, message_key, window_seconds):
        """Get count of messages in recent window"""
        # Simplified - in production would use time-based tracking
        return self.message_counts.get(message_key, 0)
    
    def get_security_report(self):
        """Get overall security report"""
        total_messages = sum(self.message_counts.values())
        anomaly_count = len(self.anomalies_detected)
        
        return {
            'total_nas_messages': total_messages,
            'unique_message_types': len(self.message_counts),
            'anomalies_detected': anomaly_count,
            'top_message_types': dict(sorted(self.message_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
            'security_status': 'secure' if anomaly_count == 0 else 'monitoring' if anomaly_count < 3 else 'threatened'
        }
    
    def reset_counters(self):
        """Reset tracking counters"""
        self.message_counts = {}
        self.anomalies_detected = []
