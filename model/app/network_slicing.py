"""
Enhanced Network Slicing with ML Insights
Dynamically adjusts slicing based on traffic patterns and ML predictions
"""
import numpy as np
from datetime import datetime

class IntelligentSliceManager:
    def __init__(self):
        self.slice_definitions = {
            "eMBB": {
                "description": "Enhanced Mobile Broadband",
                "priority": 2,
                "bandwidth_weight": 0.50,
                "qos_requirements": {
                    "latency": 10,  # ms
                    "throughput": 1000,  # Mbps
                    "reliability": 0.999
                },
                "typical_traffic": ["video", "large_file_transfer", "streaming"]
            },
            "URLLC": {
                "description": "Ultra Reliable Low Latency Communications",
                "priority": 1,
                "bandwidth_weight": 0.30,
                "qos_requirements": {
                    "latency": 1,  # ms
                    "throughput": 100,  # Mbps
                    "reliability": 0.99999
                },
                "typical_traffic": ["iot_control", "autonomous_vehicles", "industrial_automation"]
            },
            "mMTC": {
                "description": "Massive Machine Type Communications",
                "priority": 3,
                "bandwidth_weight": 0.20,
                "qos_requirements": {
                    "latency": 100,  # ms
                    "throughput": 10,  # Mbps
                    "reliability": 0.99
                },
                "typical_traffic": ["sensor_data", "smart_metering", "wearables"]
            }
        }
        
        # Traffic pattern learning
        self.traffic_patterns = {
            'video_streaming': {'packet_size': 1200, 'pps': 30, 'protocol': 'TCP'},
            'iot_heartbeat': {'packet_size': 100, 'pps': 1, 'protocol': 'UDP'},
            'gaming': {'packet_size': 500, 'pps': 50, 'protocol': 'UDP'},
            'voip': {'packet_size': 200, 'pps': 50, 'protocol': 'UDP'},
            'file_transfer': {'packet_size': 1500, 'pps': 10, 'protocol': 'TCP'}
        }
        
        # ML-based slice adjustment history
        self.slice_adjustments = []
        self.slice_performance = {slice_name: {'hits': 0, 'correct': 0} for slice_name in self.slice_definitions}
    
    def classify_slice_with_ml(self, packet_features, ml_prediction=None):
        """
        Enhanced slice classification using ML insights
        Args:
            packet_features: Extracted features from packet
            ml_prediction: Optional ML prediction for the traffic
        Returns: Recommended slice
        """
        packet_size = packet_features.get('packet_size', 0)
        protocol = packet_features.get('protocol', 'UNKNOWN')
        pps = packet_features.get('packet_rate', 0)
        
        # If ML predicts DDoS, treat differently
        if ml_prediction and ml_prediction.get('prediction') == 'ddos':
            confidence = ml_prediction.get('confidence', 0)
            
            # High-confidence DDoS: Quarantine in special slice
            if confidence > 0.9:
                return {
                    "slice": "QUARANTINE",
                    "priority": 0,  # Highest priority for mitigation
                    "action": "BLOCK",
                    "reason": f"DDoS detected (confidence: {confidence:.2f})",
                    "qos_override": {
                        "bandwidth_limit": 0.01,  # 1% bandwidth
                        "latency_limit": 1000,  # High latency
                        "isolation_level": "HIGH"
                    }
                }
            # Medium-confidence: Throttle in URLLC with monitoring
            elif confidence > 0.7:
                return {
                    "slice": "URLLC",
                    "priority": 1,
                    "action": "THROTTLE",
                    "throttle_factor": 0.1,  # 10% of normal bandwidth
                    "reason": f"Suspicious traffic (confidence: {confidence:.2f})",
                    "monitoring": "ENHANCED"
                }
        
        # Normal traffic classification with ML assistance
        # Pattern recognition
        traffic_pattern = self._identify_traffic_pattern(packet_size, pps, protocol)
        
        # URLLC detection (critical real-time traffic)
        if (pps > 200 or 
            protocol == "ICMP" or 
            (packet_size < 300 and pps > 50) or
            traffic_pattern in ['iot_heartbeat', 'voip', 'gaming']):
            slice_name = "URLLC"
            reason = "Low-latency requirement detected"
        
        # mMTC detection (IoT/sensor traffic)
        elif (packet_size < 200 and pps < 20) or traffic_pattern == 'iot_heartbeat':
            slice_name = "mMTC"
            reason = "IoT/sensor traffic pattern"
        
        # eMBB detection (high bandwidth)
        else:
            slice_name = "eMBB"
            reason = "High bandwidth traffic"
        
        # Track performance
        self.slice_performance[slice_name]['hits'] += 1
        
        # If we have ML feedback, track correctness
        if ml_prediction and 'true_label' in ml_prediction:
            # In real system, we'd use feedback to improve
            pass
        
        return self._apply_slice_policy(slice_name, reason, packet_features)
    
    def _identify_traffic_pattern(self, packet_size, pps, protocol):
        """Identify traffic pattern based on characteristics"""
        best_match = None
        best_score = 0
        
        for pattern, characteristics in self.traffic_patterns.items():
            score = 0
            
            # Packet size match (within 30%)
            expected_size = characteristics['packet_size']
            size_diff = abs(packet_size - expected_size) / expected_size
            if size_diff < 0.3:
                score += 0.4
            
            # PPS match (within 50%)
            expected_pps = characteristics['pps']
            pps_diff = abs(pps - expected_pps) / max(expected_pps, 1)
            if pps_diff < 0.5:
                score += 0.4
            
            # Protocol match
            if protocol.upper() == characteristics['protocol']:
                score += 0.2
            
            if score > best_score:
                best_score = score
                best_match = pattern
        
        return best_match if best_score > 0.5 else 'unknown'
    
    def _apply_slice_policy(self, slice_name, reason, packet_features):
        """Apply QoS policy for the selected slice"""
        slice_info = self.slice_definitions.get(slice_name, self.slice_definitions["eMBB"])
        
        # Dynamic bandwidth adjustment based on congestion
        congestion_factor = self._calculate_congestion_factor(packet_features)
        adjusted_bandwidth = slice_info['bandwidth_weight'] * (1 - congestion_factor * 0.3)
        
        # Priority adjustment for critical traffic
        priority_boost = 0
        if packet_features.get('is_urgent', False):
            priority_boost = 1
        
        return {
            "slice": slice_name,
            "priority": slice_info['priority'] - priority_boost,  # Lower number = higher priority
            "bandwidth_weight": max(0.1, adjusted_bandwidth),
            "description": slice_info['description'],
            "reason": reason,
            "qos_requirements": slice_info['qos_requirements'],
            "congestion_factor": congestion_factor,
            "timestamp": datetime.now().isoformat(),
            "traffic_characteristics": {
                "packet_size": packet_features.get('packet_size', 0),
                "packet_rate": packet_features.get('packet_rate', 0),
                "protocol": packet_features.get('protocol', 'UNKNOWN')
            }
        }
    
    def _calculate_congestion_factor(self, packet_features):
        """Calculate network congestion factor (0-1)"""
        # Simplified congestion detection
        # In real system, would use buffer occupancy, queue lengths, etc.
        pps = packet_features.get('packet_rate', 0)
        
        if pps > 1000:
            return 0.8  # High congestion
        elif pps > 500:
            return 0.5  # Medium congestion
        elif pps > 100:
            return 0.2  # Low congestion
        else:
            return 0.0  # No congestion
    
    def learn_from_feedback(self, slice_assignment, ml_prediction, actual_outcome):
        """
        Learn from feedback to improve slice assignment
        Args:
            slice_assignment: Assigned slice
            ml_prediction: ML prediction that was used
            actual_outcome: What actually happened (e.g., "normal", "ddos", "performance_issue")
        """
        # Record adjustment for learning
        adjustment = {
            'timestamp': datetime.now().isoformat(),
            'slice': slice_assignment['slice'],
            'ml_confidence': ml_prediction.get('confidence', 0) if ml_prediction else 0,
            'ml_prediction': ml_prediction.get('prediction', 'unknown') if ml_prediction else 'unknown',
            'actual_outcome': actual_outcome,
            'correct': self._is_correct_assignment(slice_assignment, actual_outcome)
        }
        
        self.slice_adjustments.append(adjustment)
        
        # Update performance metrics
        if adjustment['correct']:
            self.slice_performance[slice_assignment['slice']]['correct'] += 1
    
    def _is_correct_assignment(self, slice_assignment, actual_outcome):
        """Determine if slice assignment was correct"""
        # Simple logic: if DDoS was detected and we didn't quarantine, it's wrong
        if actual_outcome == 'ddos' and slice_assignment['slice'] != 'QUARANTINE':
            return False
        # If normal traffic and we quarantined, it's wrong
        elif actual_outcome == 'normal' and slice_assignment['slice'] == 'QUARANTINE':
            return False
        
        return True
    
    def get_slice_performance(self):
        """Get performance metrics for slice assignments"""
        performance = {}
        
        for slice_name, stats in self.slice_performance.items():
            if stats['hits'] > 0:
                accuracy = stats['correct'] / stats['hits']
            else:
                accuracy = 0.0
            
            performance[slice_name] = {
                'hits': stats['hits'],
                'correct': stats['correct'],
                'accuracy': accuracy,
                'recent_adjustments': len([a for a in self.slice_adjustments[-100:] 
                                          if a['slice'] == slice_name])
            }
        
        return performance
    
    def optimize_slice_parameters(self):
        """Optimize slice parameters based on performance"""
        performance = self.get_slice_performance()
        
        optimizations = {}
        for slice_name, perf in performance.items():
            if perf['hits'] < 10:
                continue  # Not enough data
            
            if perf['accuracy'] < 0.7:
                # Need optimization
                optimizations[slice_name] = {
                    'current_accuracy': perf['accuracy'],
                    'suggestion': 'Increase monitoring or adjust thresholds',
                    'priority_boost': 0.1 if perf['accuracy'] < 0.5 else 0
                }
        
        return optimizations

# Legacy function for backward compatibility
def get_network_slice(packet_size, protocol, pps, ml_prediction=None):
    """
    Legacy function that creates an IntelligentSliceManager instance
    and classifies traffic
    """
    manager = IntelligentSliceManager()
    
    packet_features = {
        'packet_size': packet_size,
        'protocol': protocol,
        'packet_rate': pps
    }
    
    result = manager.classify_slice_with_ml(packet_features, ml_prediction)
    
    # Return in legacy format
    return {
        "slice": result["slice"],
        "priority": result["priority"],
        "bandwidth_weight": result.get("bandwidth_weight", 0.5),
        "description": result["description"],
        "timestamp": datetime.now().isoformat()
    }