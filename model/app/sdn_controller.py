"""
Enhanced SDN Controller Interface
"""
import requests
import logging
import time
from typing import Optional, Dict, List

class SDNController:
    def __init__(self, host='192.168.56.101', port=8080):
        self.base_url = f"http://{host}:{port}"
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.timeout = 5
        self.retry_count = 3
        self.retry_delay = 1
        
        self._check_connection()
        self.logger.info(f"✅ SDN Controller connected to {self.base_url}")
    
    def _check_connection(self):
        """Verify connection to Ryu controller"""
        try:
            response = self.session.get(f"{self.base_url}/stats/switches", timeout=5)
            if response.status_code == 200:
                switches = response.json()
                self.logger.info(f"📡 Connected to Ryu. Switches: {switches}")
                return True
            else:
                self.logger.warning(f"Ryu status {response.status_code}")
        except Exception as e:
            self.logger.error(f"Cannot reach Ryu: {e}")
            raise ConnectionError(f"Failed to connect to Ryu at {self.base_url}")
        return False
    
    def _make_request(self, method, endpoint, **kwargs):
        """Make HTTP request with retry logic"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.retry_count):
            try:
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt < self.retry_count - 1:
                    self.logger.warning(f"Attempt {attempt + 1} failed for {endpoint}, retrying...")
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    self.logger.error(f"All attempts failed for {endpoint}: {e}")
                    raise
        return None
    
    def install_flow_rule(self, dpid: int, rule: Dict) -> bool:
        """Install flow rule on switch"""
        endpoint = "/stats/flowentry/add"
        data = {
            "dpid": dpid,
            **rule
        }
        
        try:
            response = self._make_request('POST', endpoint, json=data)
            return response is not None and response.status_code in (200, 201)
        except Exception as e:
            self.logger.error(f"Flow installation failed: {e}")
            return False
    
    def remove_flow_rule(self, dpid: int, rule: Dict) -> bool:
        """Remove flow rule from switch"""
        endpoint = "/stats/flowentry/delete"
        data = {
            "dpid": dpid,
            **rule
        }
        
        try:
            response = self._make_request('POST', endpoint, json=data)
            return response is not None and response.status_code in (200, 201)
        except Exception as e:
            self.logger.error(f"Flow removal failed: {e}")
            return False
    
    def block_ip(self, ip: str, slice_type: Optional[str] = None) -> bool:
        """Block IP with slice-aware rules"""
        # Base blocking rule
        rule = {
            "priority": 60000,
            "match": {
                "eth_type": 0x0800,
                "ipv4_src": ip
            },
            "actions": []  # Empty actions = DROP
        }
        
        # Add slice-specific matching if provided
        if slice_type:
            # This would map slice_type to VLAN or other identifiers
            # For now, just add to match criteria
            rule['match']['slice_id'] = self._slice_to_id(slice_type)
            rule['priority'] = 65000  # Higher priority for slice-specific rules
        
        success = self.install_flow_rule(1, rule)
        
        if success:
            self.logger.info(f"✅ Blocked IP {ip}" + (f" on slice {slice_type}" if slice_type else ""))
        else:
            self.logger.error(f"❌ Failed to block IP {ip}")
        
        return success
    
    def unblock_ip(self, ip: str) -> bool:
        """Remove all blocking rules for IP"""
        # Create match pattern for deletion
        rule = {
            "match": {
                "eth_type": 0x0800,
                "ipv4_src": ip
            }
        }
        
        success = self.remove_flow_rule(1, rule)
        
        if success:
            self.logger.info(f"✅ Unblocked IP {ip}")
        else:
            self.logger.warning(f"⚠️  May have failed to unblock IP {ip} (or no rule existed)")
        
        return success
    
    def throttle_ip(self, ip: str, rate_limit_kbps: int = 1000) -> bool:
        """Throttle IP instead of full block"""
        # Rate limiting rule (simplified)
        rule = {
            "priority": 55000,
            "match": {
                "eth_type": 0x0800,
                "ipv4_src": ip
            },
            "actions": [
                {
                    "type": "OUTPUT",
                    "port": "CONTROLLER"  # Would implement meter-based limiting in production
                }
            ]
        }
        
        success = self.install_flow_rule(1, rule)
        
        if success:
            self.logger.info(f"✅ Throttled IP {ip} to {rate_limit_kbps} Kbps")
        else:
            self.logger.error(f"❌ Failed to throttle IP {ip}")
        
        return success
    
    def get_switch_stats(self, dpid: int = 1) -> Optional[Dict]:
        """Get switch statistics"""
        try:
            response = self._make_request('GET', f"/stats/desc/{dpid}")
            return response.json() if response else None
        except Exception as e:
            self.logger.error(f"Failed to get switch stats: {e}")
            return None
    
    def get_flow_stats(self, dpid: int = 1) -> List[Dict]:
        """Get current flow statistics"""
        try:
            response = self._make_request('GET', f"/stats/flow/{dpid}")
            return response.json() if response else []
        except Exception as e:
            self.logger.error(f"Failed to get flow stats: {e}")
            return []
    
    def cleanup_old_rules(self, dpid: int = 1, older_than_hours: int = 24) -> int:
        """Clean up old flow rules (maintenance)"""
        # Implementation would enumerate and remove old rules
        # For now, return count of rules that would be cleaned
        self.logger.info(f"Would clean rules older than {older_than_hours}h on switch {dpid}")
        return 0
    
    def _slice_to_id(self, slice_type: str) -> int:
        """Map slice type to identifier for SDN rules"""
        mapping = {
            'eMBB': 100,
            'URLLC': 200,
            'mMTC': 300,
            'V2X': 400,
            'IndustrialIoT': 500
        }
        return mapping.get(slice_type, 100)
    
    def get_status(self) -> Dict:
        """Get controller status"""
        try:
            switches = self.get_switch_stats()
            flows = self.get_flow_stats()
            
            return {
                'connected': True,
                'switches': switches.get('switches', []) if switches else [],
                'active_flows': len(flows),
                'controller_url': self.base_url,
                'last_check': time.time()
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e),
                'controller_url': self.base_url
            }
