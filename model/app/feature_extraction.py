"""
Enhanced Feature Extraction for 5G Traffic
"""
import numpy as np
from collections import defaultdict
import time

class FeatureExtractor:
    def __init__(self):
        self.flows = {}
        self.flow_timeout = 300  # 5 minutes
        self.last_cleanup = time.time()
        
    def extract_features_from_packet(self, packet):
        """Extract features from a single packet"""
        features = {}
        
        try:
            # Basic packet info
            features['timestamp'] = getattr(packet, 'sniff_time', time.time())
            features['packet_size'] = int(getattr(packet, 'length', 0))
            
            # IP layer
            if hasattr(packet, 'ip'):
                features['src_ip'] = packet.ip.src
                features['dst_ip'] = packet.ip.dst
                features['ip_version'] = 4
                
                # Protocol
                proto_num = int(packet.ip.proto)
                features['protocol'] = proto_num
                features['protocol_name'] = self._protocol_name(proto_num)
            
            # Transport layer
            if hasattr(packet, 'tcp'):
                features['src_port'] = int(packet.tcp.srcport)
                features['dst_port'] = int(packet.tcp.dstport)
                features['tcp_flags'] = int(getattr(packet.tcp, 'flags', 0))
                features['window_size'] = int(getattr(packet.tcp, 'window', 0))
                features['tcp_len'] = int(getattr(packet.tcp, 'len', 0))
                
            elif hasattr(packet, 'udp'):
                features['src_port'] = int(packet.udp.srcport)
                features['dst_port'] = int(packet.udp.dstport)
                features['udp_len'] = int(getattr(packet.udp, 'length', 0))
                
            elif hasattr(packet, 'icmp'):
                features['icmp_type'] = int(packet.icmp.type)
                features['icmp_code'] = int(packet.icmp.code)
        
        except AttributeError as e:
            # Packet missing expected layers
            pass
        
        return features
    
    def update_flow_features(self, packet_features):
        """Update flow-based features"""
        # Create flow key
        if 'src_ip' in packet_features and 'dst_ip' in packet_features:
            flow_key = (
                packet_features['src_ip'],
                packet_features['dst_ip'],
                packet_features.get('src_port', 0),
                packet_features.get('dst_port', 0),
                packet_features.get('protocol', 0)
            )
            
            # Initialize or update flow
            if flow_key not in self.flows:
                self.flows[flow_key] = {
                    'start_time': packet_features['timestamp'],
                    'packets': [],
                    'sizes': [],
                    'timestamps': [],
                    'last_activity': packet_features['timestamp']
                }
            
            flow = self.flows[flow_key]
            flow['packets'].append(packet_features)
            flow['sizes'].append(packet_features['packet_size'])
            flow['timestamps'].append(packet_features['timestamp'])
            flow['last_activity'] = packet_features['timestamp']
            
            # Clean old flows periodically
            if time.time() - self.last_cleanup > 60:
                self._cleanup_old_flows()
                self.last_cleanup = time.time()
            
            # Calculate flow statistics
            return self._calculate_flow_features(flow_key)
        
        return {}
    
    def _calculate_flow_features(self, flow_key):
        """Calculate comprehensive flow features"""
        flow = self.flows[flow_key]
        
        if len(flow['packets']) < 2:
            return {}
        
        sizes = np.array(flow['sizes'])
        timestamps = np.array(flow['timestamps'])
        
        # Time-based features
        duration = timestamps[-1] - timestamps[0]
        inter_arrival_times = np.diff(timestamps)
        
        # Statistical features
        features = {
            'flow_duration': float(duration),
            'total_packets': len(flow['packets']),
            'total_bytes': float(np.sum(sizes)),
            'packets_per_second': len(flow['packets']) / max(duration, 0.001),
            'bytes_per_second': np.sum(sizes) / max(duration, 0.001),
            'avg_packet_size': float(np.mean(sizes)),
            'std_packet_size': float(np.std(sizes)) if len(sizes) > 1 else 0.0,
            'min_packet_size': float(np.min(sizes)),
            'max_packet_size': float(np.max(sizes)),
            'avg_inter_arrival': float(np.mean(inter_arrival_times)) if len(inter_arrival_times) > 0 else 0.0,
            'std_inter_arrival': float(np.std(inter_arrival_times)) if len(inter_arrival_times) > 1 else 0.0,
            'size_entropy': self._calculate_entropy(sizes),
            'time_entropy': self._calculate_entropy(inter_arrival_times) if len(inter_arrival_times) > 0 else 0.0
        }
        
        # Protocol specific features
        first_packet = flow['packets'][0]
        if 'tcp_flags' in first_packet:
            features['syn_count'] = sum(1 for p in flow['packets'] if p.get('tcp_flags', 0) & 0x02)
            features['fin_count'] = sum(1 for p in flow['packets'] if p.get('tcp_flags', 0) & 0x01)
            features['rst_count'] = sum(1 for p in flow['packets'] if p.get('tcp_flags', 0) & 0x04)
        
        return features
    
    def _calculate_entropy(self, values):
        """Calculate entropy of a distribution"""
        if len(values) == 0:
            return 0.0
        
        # Discretize values
        hist, _ = np.histogram(values, bins=10)
        hist = hist[hist > 0]
        probabilities = hist / np.sum(hist)
        entropy = -np.sum(probabilities * np.log2(probabilities))
        
        return float(entropy)
    
    def _cleanup_old_flows(self):
        """Remove inactive flows"""
        current_time = time.time()
        to_remove = []
        
        for flow_key, flow in self.flows.items():
            if current_time - flow['last_activity'] > self.flow_timeout:
                to_remove.append(flow_key)
        
        for flow_key in to_remove:
            del self.flows[flow_key]
    
    def _protocol_name(self, proto_num):
        """Convert protocol number to name"""
        protocols = {
            1: 'ICMP',
            2: 'IGMP',
            6: 'TCP',
            17: 'UDP',
            47: 'GRE',
            50: 'ESP',
            51: 'AH',
            58: 'IPv6-ICMP',
            89: 'OSPF'
        }
        return protocols.get(proto_num, f'Proto-{proto_num}')