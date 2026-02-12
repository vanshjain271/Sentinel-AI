"""
5G Core Integration - Interface with Open5GS/UERANSIM
"""
import requests
import socket
import json
import logging

class FiveGCoreIntegration:
    def __init__(self, open5gs_base="http://localhost:3000", enabled=True):
        self.base_url = open5gs_base
        self.enabled = enabled
        self.logger = logging.getLogger(__name__)
        
        # 5G Network Slice Configuration
        self.slices = {
            'eMBB': {'sst': 1, 'sd': '010203', 'priority': 2},
            'URLLC': {'sst': 2, 'sd': '112233', 'priority': 1},
            'mMTC': {'sst': 3, 'sd': '445566', 'priority': 3},
            'V2X': {'sst': 2, 'sd': '778899', 'priority': 1},
            'IndustrialIoT': {'sst': 3, 'sd': '990011', 'priority': 2}
        }
        
        if self.enabled:
            self._test_connection()
    
    def _test_connection(self):
        """Test connection to 5G core"""
        try:
            response = requests.get(f"{self.base_url}/api/status", timeout=2)
            if response.status_code == 200:
                self.logger.info("✅ Connected to 5G Core")
                return True
        except Exception as e:
            self.logger.warning(f"⚠️  5G Core not reachable: {e}")
            self.enabled = False
        return False
    
    def get_ue_slice_info(self, ue_ip):
        """Get UE's network slice information"""
        if not self.enabled:
            return self._get_mock_slice_info(ue_ip)
        
        try:
            response = requests.get(
                f"{self.base_url}/api/ue/{ue_ip}",
                timeout=2
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'slice': self._map_sst_to_slice(data.get('sst', 1)),
                    'supi': data.get('supi', 'unknown'),
                    'session_id': data.get('session_id'),
                    'qos_profile': data.get('qos', {}),
                    'source': '5g_core'
                }
        except Exception as e:
            self.logger.debug(f"5G Core query failed: {e}")
        
        # Fallback to mock
        return self._get_mock_slice_info(ue_ip)
    
    def enforce_slice_policy(self, slice_type, action):
        """Enforce security policy on specific slice"""
        if not self.enabled:
            self.logger.info(f"[MOCK] Would enforce {action} on slice {slice_type}")
            return True
        
        policy = {
            'slice': slice_type,
            'action': action,  # 'block', 'throttle', 'allow', 'isolate'
            'priority': self.slices.get(slice_type, {}).get('priority', 2),
            'qos_adjustment': 'minimum' if action == 'block' else 'reduced' if action == 'throttle' else 'normal'
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/policy/enforce",
                json=policy,
                timeout=3
            )
            if response.status_code == 200:
                self.logger.info(f"✅ Policy enforced: {action} on {slice_type}")
                return True
        except Exception as e:
            self.logger.error(f"Policy enforcement failed: {e}")
        
        return False
    
    def _get_mock_slice_info(self, ue_ip):
        """Generate mock slice info for testing"""
        # Simple hash-based slice assignment for consistency
        slice_idx = hash(ue_ip) % 3
        slices = ['eMBB', 'URLLC', 'mMTC']
        selected_slice = slices[slice_idx]
        
        return {
            'slice': selected_slice,
            'supi': f'imsi-00101{hash(ue_ip) % 1000000:06d}',
            'session_id': f'sess-{hash(ue_ip) % 10000:04d}',
            'qos_profile': {
                '5qi': self.slices[selected_slice]['sst'],
                'priority': self.slices[selected_slice]['priority'],
                'max_delay': 300 if selected_slice == 'eMBB' else 10 if selected_slice == 'URLLC' else 1000
            },
            'source': 'mock'
        }
    
    def _map_sst_to_slice(self, sst):
        mapping = {1: 'eMBB', 2: 'URLLC', 3: 'mMTC', 4: 'V2X', 5: 'IndustrialIoT'}
        return mapping.get(sst, 'eMBB')
    
    def get_slice_stats(self):
        """Get statistics for all slices"""
        stats = {}
        for slice_name, config in self.slices.items():
            stats[slice_name] = {
                'sst': config['sst'],
                'priority': config['priority'],
                'active_ues': 0,  # Would be real data in production
                'traffic_load': 'normal',
                'security_status': 'protected'
            }
        return stats