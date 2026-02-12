"""
Enhanced Mitigation Engine with 5G awareness
"""
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional
from sdn_controller import SDNController
from performance_cache import performance_monitor

class MitigationEngine:
    def __init__(self, sdn_controller: SDNController):
        self.sdn_controller = sdn_controller
        self.logger = logging.getLogger(__name__)
        self.blocked_ips: Dict[str, dict] = {}
        self.mitigation_history: List[dict] = []
        
        # Configuration
        self.config = {
            'default_switch_id': 1,
            'ddos_threshold': 0.7,
            'block_duration': 3600,
            'max_history': 1000,
            'check_interval': 60,
            'auto_unblock': True,
            'adaptive_threshold': True
        }
        
        # 5G slice aware mitigation
        self.slice_policies = {
            'eMBB': {'block_threshold': 0.7, 'throttle_threshold': 0.5, 'priority': 2},
            'URLLC': {'block_threshold': 0.9, 'throttle_threshold': 0.6, 'priority': 1},
            'mMTC': {'block_threshold': 0.6, 'throttle_threshold': 0.4, 'priority': 3},
            'V2X': {'block_threshold': 0.95, 'throttle_threshold': 0.7, 'priority': 1},
            'IndustrialIoT': {'block_threshold': 0.8, 'throttle_threshold': 0.5, 'priority': 2}
        }
        
        self._start_cleanup_thread()
        self.logger.info("✅ Mitigation Engine Initialized")

    def _start_cleanup_thread(self):
        import threading
        def cleanup_loop():
            while True:
                self._cleanup_expired_blocks()
                time.sleep(self.config['check_interval'])
        threading.Thread(target=cleanup_loop, daemon=True).start()

    def _cleanup_expired_blocks(self):
        now = time.time()
        expired = [ip for ip, d in self.blocked_ips.items() 
                  if now - d['timestamp'] > self.config['block_duration'] and self.config['auto_unblock']]
        
        for ip in expired:
            self.unblock_ip(ip)
            self.logger.info(f"⏰ Block expired for IP: {ip}")

        if len(self.mitigation_history) > self.config['max_history']:
            self.mitigation_history = self.mitigation_history[-self.config['max_history']:]

    def is_ip_blocked(self, ip: str) -> bool:
        if ip in self.blocked_ips:
            self.blocked_ips[ip]['last_seen'] = time.time()
            self.blocked_ips[ip]['packets_blocked'] += 1
            return True
        return False

    @performance_monitor
    def execute_mitigation(self, detection_result: dict, flow_info: dict, slice_type: str = "eMBB") -> dict:
        """Enhanced mitigation with 5G slice awareness"""
        src_ip = flow_info.get('src_ip', 'unknown')
        
        if src_ip in ('unknown', '0.0.0.0'):
            return {"status": "error", "message": "Invalid IP", "mitigation_applied": False}

        if self.is_ip_blocked(src_ip):
            return {
                "status": "already_blocked",
                "ip": src_ip,
                "since": datetime.fromtimestamp(self.blocked_ips[src_ip]['timestamp']).isoformat(),
                "packets_blocked": self.blocked_ips[src_ip]['packets_blocked'],
                "mitigation_applied": False
            }

        is_ddos = detection_result.get('prediction', '').lower() == 'ddos'
        confidence = float(detection_result.get('confidence', 0.0))
        
        # Get slice-specific thresholds
        slice_policy = self.slice_policies.get(slice_type, self.slice_policies['eMBB'])
        block_threshold = slice_policy['block_threshold']
        throttle_threshold = slice_policy['throttle_threshold']
        
        # Adaptive threshold adjustment
        if self.config['adaptive_threshold']:
            current_load = flow_info.get('network_load', 0.5)
            if current_load > 0.8:  # High network load
                block_threshold *= 0.9  # Lower threshold under stress
                throttle_threshold *= 0.8
        
        mitigation_action = None
        mitigation_applied = False
        
        if is_ddos and confidence >= block_threshold:
            # Full block
            if self.block_ip(src_ip, f'DDoS detected (confidence: {confidence:.2%})', confidence, slice_type):
                mitigation_action = 'BLOCKED'
                mitigation_applied = True
                
        elif is_ddos and confidence >= throttle_threshold:
            # Throttle instead of block
            if self.throttle_ip(src_ip, slice_type, 0.5):  # 50% throttling
                mitigation_action = 'THROTTLED'
                mitigation_applied = True
                
        elif confidence >= throttle_threshold * 0.8:
            # Monitor closely
            mitigation_action = 'MONITOR'
            mitigation_applied = False
            self.logger.info(f"👁️  Monitoring {src_ip} (confidence: {confidence:.2%})")
        
        # Record in history
        if mitigation_action:
            self.mitigation_history.append({
                'timestamp': time.time(),
                'ip': src_ip,
                'confidence': confidence,
                'action': mitigation_action,
                'slice': slice_type,
                'details': {
                    'threshold_used': block_threshold if mitigation_action == 'BLOCKED' else throttle_threshold,
                    'flow_info': {k: v for k, v in flow_info.items() if k != 'packet_data'}
                }
            })

        return {
            "status": mitigation_action.lower() if mitigation_action else "normal",
            "ip": src_ip,
            "confidence": confidence,
            "action": mitigation_action,
            "slice": slice_type,
            "threshold_used": block_threshold if mitigation_action == 'BLOCKED' else throttle_threshold,
            "mitigation_applied": mitigation_applied,
            "timestamp": datetime.now().isoformat()
        }

    def block_ip(self, ip: str, reason: str = 'DDoS Detection', confidence: float = 0.0, slice_type: str = "eMBB") -> bool:
        if not ip or ip in ("0.0.0.0", "unknown"):
            self.logger.warning(f"block_ip refused invalid IP: {ip}")
            return False

        self.logger.info(f"🚫 BLOCKING IP {ip} on slice {slice_type} (reason: {reason}, confidence: {confidence*100:.1f}%)")
        
        # SDN blocking
        success = self.sdn_controller.block_ip(ip)
        
        if success:
            self.blocked_ips[ip] = {
                "timestamp": time.time(),
                "confidence": confidence,
                "packets_blocked": 0,
                "reason": reason,
                "last_seen": time.time(),
                "slice_type": slice_type,
                "blocked_by": "engine"
            }
            self.logger.info(f"✅ Successfully blocked {ip} on {slice_type}")
        else:
            self.logger.warning(f"❌ Failed to block {ip}")

        return success

    def throttle_ip(self, ip: str, slice_type: str, throttle_ratio: float = 0.5) -> bool:
        """Throttle IP instead of full block"""
        self.logger.info(f"🐢 Throttling IP {ip} on {slice_type} to {throttle_ratio*100:.0f}%")
        
        # In production, implement actual QoS throttling
        # For now, simulate success
        success = True
        
        if success:
            self.blocked_ips[ip] = {
                "timestamp": time.time(),
                "action": "throttled",
                "throttle_ratio": throttle_ratio,
                "slice_type": slice_type,
                "last_seen": time.time()
            }
        
        return success

    def unblock_ip(self, ip: str) -> bool:
        if ip not in self.blocked_ips:
            return False
        
        action = self.blocked_ips[ip].get('action', 'blocked')
        
        if action == 'blocked':
            success = self.sdn_controller.unblock_ip(ip)
        else:
            success = True  # Throttling removed automatically
        
        if success:
            del self.blocked_ips[ip]
            self.logger.info(f"✅ Successfully unblocked {ip}")
        
        return success

    def get_blocked_ips(self) -> List[dict]:
        return [
            {
                "ip": ip,
                "timestamp": datetime.fromtimestamp(d["timestamp"]).isoformat(),
                "reason": d["reason"],
                "confidence": d["confidence"],
                "packets_blocked": d["packets_blocked"],
                "last_seen": datetime.fromtimestamp(d["last_seen"]).isoformat(),
                "slice_type": d.get("slice_type", "unknown"),
                "action": d.get("action", "blocked")
            }
            for ip, d in self.blocked_ips.items()
        ]

    def get_mitigation_history(self, limit: int = 50) -> List[dict]:
        return self.mitigation_history[-limit:]

    def get_slice_stats(self) -> Dict:
        """Get statistics per slice"""
        stats = {}
        for slice_name in self.slice_policies.keys():
            slice_blocks = [ip for ip, d in self.blocked_ips.items() if d.get('slice_type') == slice_name]
            stats[slice_name] = {
                'blocked_ips': len(slice_blocks),
                'currently_blocked': len([ip for ip in slice_blocks if self.blocked_ips[ip].get('action') == 'blocked']),
                'currently_throttled': len([ip for ip in slice_blocks if self.blocked_ips[ip].get('action') == 'throttled']),
                'policy': self.slice_policies[slice_name]
            }
        return stats