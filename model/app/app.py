"""
SentinelAI - Enhanced with 5G and Advanced AI
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
import threading
import time
import socket
import numpy as np
from datetime import datetime
from collections import defaultdict, deque
import joblib
import os

# ---------- Modules ----------
from network_slicing import get_network_slice
from ml_detection import MLDetectionEngine
from online_learning import OnlineLearningEngine
from explainable_ai import DDoSExplainer
from fiveg_core_integration import FiveGCoreIntegration
from nas_analyzer import NASAnalyzer

# ---------- 3rd party ----------
from scapy.all import sniff, IP, TCP, UDP, ICMP

# ==========================================================
app = Flask(__name__)
CORS(app, origins=["*"])

# === LOGGING ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger("SENTINEL")

# === AUTO-DETECT LAPTOP IP ===
def get_laptop_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 1))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

LAPTOP_IP = get_laptop_ip()
log.info(f"🎯 SYSTEM STARTED → LAPTOP IP: {LAPTOP_IP}")

# ==========================================================
# CONFIGURATION
# ==========================================================
RYU_URL = "http://192.168.56.101:8080"
NODE_URL = "http://localhost:3000/api/emit-blocked-ip"
NODE_LIVEPACKET = "http://localhost:3000/api/live-packet"

# Get the absolute path to the directory where app.py lives (model/app/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Move up one level to 'model/' then down into 'models/'
MODEL_BASE_PATH = os.path.join(BASE_DIR, "..", "models")

SCALER_PATH = os.path.join(MODEL_BASE_PATH, "5g_ddos_scaler.pkl")
FEATURE_NAMES_PATH = os.path.join(MODEL_BASE_PATH, "5g_feature_names.pkl")
ENSEMBLE_MODEL_PATH = os.path.join(MODEL_BASE_PATH, "ensemble_voting.pkl")

# === LOAD MODELS ===
ml_engine = None
online_learner = None
explainer = None
fiveg_core = None
nas_analyzer = None

try:
    # Load feature names
    if not os.path.exists(FEATURE_NAMES_PATH):
        raise FileNotFoundError(f"Missing file: {FEATURE_NAMES_PATH}")
        
    with open(FEATURE_NAMES_PATH, 'rb') as f:
        feature_names = joblib.load(f)
    
    # Load scaler
    if not os.path.exists(SCALER_PATH):
        raise FileNotFoundError(f"Missing file: {SCALER_PATH}")
        
    scaler = joblib.load(SCALER_PATH)
    
    # Initialize engines
    ml_engine = MLDetectionEngine()
    online_learner = OnlineLearningEngine()
    explainer = DDoSExplainer(feature_names)
    fiveg_core = FiveGCoreIntegration()
    nas_analyzer = NASAnalyzer()
    
    log.info("✅ MODELS LOADED SUCCESSFULLY")
    log.info(f"   → Features: {len(feature_names)}")
    log.info(f"   → Scaler: {scaler.__class__.__name__}")
    
except Exception as e:
    log.error(f"❌ FAILED TO LOAD MODELS: {e}")
    raise

# === STATE ===
BLOCKED_IPS = set()
running = False
packet_queue = deque(maxlen=1000)
flow_tracker = defaultdict(lambda: {'packets': [], 'start_time': None})

# === PROTOCOL MAPPING ===
PROTOCOL_MAP = {
    1: "ICMP",
    6: "TCP",
    17: "UDP",
    58: "IPv6-ICMP",
    89: "OSPF",
    50: "ESP",
    51: "AH",
}

# ==========================================================
# FEATURE EXTRACTOR
# ==========================================================
def extract_features(packet, src_ip, dst_ip, protocol_name, pps):
    """Extract advanced features for ML models"""
    features = {}
    
    # Basic features
    features['packet_size'] = len(packet)
    features['packets_per_second'] = pps
    features['avg_packet_size'] = len(packet)
    features['protocol'] = 6 if protocol_name == 'TCP' else 17 if protocol_name == 'UDP' else 1
    features['src_port_entropy'] = 0.5  # Simplified
    features['dst_port_entropy'] = 0.3
    
    # Statistical features (would be enhanced in real deployment)
    features['packet_size_variance'] = 100.0
    features['jitter'] = 0.01
    features['bytes_per_second'] = len(packet) * pps
    features['concurrent_connections'] = 5
    features['failed_connections'] = 0
    features['retransmission_rate'] = 0.01
    
    # 5G Features
    slice_info = get_network_slice(len(packet), protocol_name, pps)
    features['slice_type_encoded'] = {'eMBB': 0, 'URLLC': 1, 'mMTC': 2}.get(slice_info['slice'], 0)
    features['5qi'] = slice_info.get('5qi', 6)
    features['priority_level'] = slice_info.get('priority', 10)
    
    # Derived features
    features['traffic_intensity'] = features['bytes_per_second'] / 1000000  # Mbps
    features['packet_size_ratio'] = 1.0
    
    return features, slice_info

# ==========================================================
# DETECTION PIPELINE
# ==========================================================
def detection_pipeline(features_dict, src_ip, is_simulated=False):
    """Complete detection pipeline"""
    
    # Convert features to array in correct order
    features_array = np.array([features_dict.get(name, 0) for name in feature_names])
    
    # Scale features
    features_scaled = scaler.transform(features_array.reshape(1, -1))
    
    # Get ML prediction
    ml_result = ml_engine.detect_ddos(features_scaled)
    
    # Get AI explanation
    explanation = explainer.explain_prediction(features_scaled[0], ml_result)
    
    # Online learning (if not simulated)
    if not is_simulated and online_learner:
        # In production, you'd have ground truth from verification
        online_learner.add_feedback(
            features=features_scaled[0],
            true_label=ml_result.get('prediction') == 'ddos',
            predicted_label=ml_result.get('prediction') == 'ddos',
            confidence=ml_result.get('confidence', 0.5)
        )
    
    # 5G Core integration
    fiveg_info = {}
    if fiveg_core:
        fiveg_info = fiveg_core.get_ue_slice_info(src_ip)
        if ml_result.get('prediction') == 'ddos':
            fiveg_core.enforce_slice_policy(
                fiveg_info.get('slice', 'eMBB'),
                'block' if ml_result.get('confidence', 0) > 0.8 else 'throttle'
            )
    
    return {
        **ml_result,
        'explanation': explanation,
        '5g_info': fiveg_info,
        'features_used': len(feature_names),
        'model_version': '3.0.0'
    }

# ==========================================================
# RYU CONTROLLER: BLOCK / UNBLOCK
# ==========================================================
def block_ip(ip: str, reason: str = "DDoS detected") -> bool:
    """Install DROP flow in Ryu"""
    if ip in BLOCKED_IPS:
        return True

    url = f"{RYU_URL}/stats/flowentry/add"
    rule = {
        "dpid": 1,
        "priority": 60000,
        "match": {
            "eth_type": 0x0800,
            "ipv4_src": ip
        },
        "actions": []
    }

    try:
        r = requests.post(url, json=rule, timeout=3)
        if r.ok:
            BLOCKED_IPS.add(ip)
            log.warning(f"🚫 BLOCKED {ip} → {reason}")
            return True
        else:
            log.error(f"RYU failed: {r.status_code} {r.text}")
    except Exception as e:
        log.error(f"RYU unreachable: {e}")
    return False

def unblock_ip(ip: str) -> bool:
    """Remove DROP flow from Ryu"""
    if ip not in BLOCKED_IPS:
        return True

    url = f"{RYU_URL}/stats/flowentry/delete"
    rule = {
        "dpid": 1,
        "match": {
            "eth_type": 0x0800,
            "ipv4_src": ip
        }
    }

    try:
        r = requests.post(url, json=rule, timeout=3)
        if r.ok:
            BLOCKED_IPS.discard(ip)
            log.info(f"✅ UNBLOCKED {ip}")
            return True
    except Exception as e:
        log.error(f"Failed to unblock {ip}: {e}")
    return False

# ==========================================================
# RATE TRACKER
# ==========================================================
class RateTracker:
    def __init__(self, window=1.0):
        self.window = window
        self.timestamps = defaultdict(deque)

    def add(self, src_ip: str, ts: float):
        q = self.timestamps[src_ip]
        q.append(ts)
        while q and ts - q[0] > self.window:
            q.popleft()

    def pps(self, src_ip: str) -> float:
        q = self.timestamps[src_ip]
        return len(q) / self.window if q else 0.0

rate_tracker = RateTracker(window=1.0)

# ==========================================================
# SCAPY CAPTURE LOOP
# ==========================================================
def capture_loop():
    global running
    log.info(f"🚀 CAPTURE STARTED on Wi-Fi → Target: {LAPTOP_IP}")

    def packet_handler(pkt):
        if not running:
            return
        if not pkt.haslayer(IP):
            return

        ip_layer = pkt[IP]
        src_ip = ip_layer.src
        dst_ip = ip_layer.dst
        size = len(pkt)
        proto = ip_layer.proto
        
        # Get protocol name
        protocol_name = PROTOCOL_MAP.get(proto, f"Proto-{proto}")
        
        # Update rate tracker
        now = time.time()
        rate_tracker.add(src_ip, now)
        pps = rate_tracker.pps(src_ip)
        
        # Extract features
        features, slice_info = extract_features(pkt, src_ip, dst_ip, protocol_name, pps)
        
        # Send to frontend
        try:
            requests.post(NODE_LIVEPACKET, json={
                "srcIP": src_ip,
                "dstIP": dst_ip,
                "protocol": protocol_name,
                "packetSize": size,
                "timestamp": int(now * 1000),
                "network_slice": slice_info['slice'],
                "slice_priority": slice_info['priority'],
                "features": {k: float(v) for k, v in features.items()},
                "isReal": True
            }, timeout=0.1)
        except:
            pass
        
        # Detection
        if pps > 50:  # Only analyze suspicious traffic
            detection_result = detection_pipeline(features, src_ip, is_simulated=False)
            
            if detection_result.get('prediction') == 'ddos' and detection_result.get('confidence', 0) > 0.7:
                if block_ip(src_ip, f"DDoS (Confidence: {detection_result['confidence']:.2%})"):
                    # Send blocked IP to frontend
                    try:
                        requests.post(NODE_URL, json={
                            "ip": src_ip,
                            "reason": f"DDoS Detection (Confidence: {detection_result['confidence']:.2%})",
                            "confidence": detection_result['confidence'],
                            "threatLevel": "high",
                            "timestamp": datetime.now().isoformat(),
                            "isSimulated": False,
                            "network_slice": slice_info['slice'],
                            "explanation": detection_result.get('explanation', {}),
                            "model_used": detection_result.get('model_version', ' ')
                        }, timeout=1)
                    except:
                        pass
                    
                    log.warning(f"🚨 DDoS DETECTED: {src_ip} → Confidence: {detection_result['confidence']:.2%}")

    try:
        sniff(
            iface="en0",
            prn=packet_handler,
            store=False,
            stop_filter=lambda x: not running
        )
    except Exception as e:
        log.error(f"Capture crashed: {e}")
    finally:
        running = False
        log.info("Capture thread exited")

# ==========================================================
# API ROUTES
# ==========================================================

@app.post("/simulate-packet")
def simulate_packet():
    """simulation endpoint"""
    try:
        data = request.get_json(force=True) or {}
        
        # Extract data
        src_ip = data.get("srcIP") or request.headers.get("X-Forwarded-For") or "192.168.1.100"
        dst_ip = data.get("dstIP") or LAPTOP_IP
        packet_size = int(data.get("packetSize", 1024))
        protocol = data.get("protocol", "TCP")
        
        # Simulated is always treated as attack for demo
        is_simulated = True
        now = time.time()
        pps = 1000  # Simulated high rate
        
        # Get network slice
        slice_info = get_network_slice(packet_size, protocol, pps)
        
        # Extract features
        features_dict = {
            'packet_size': packet_size,
            'packets_per_second': pps,
            'avg_packet_size': packet_size,
            'protocol': 6 if protocol == 'TCP' else 17,
            'slice_type_encoded': {'eMBB': 0, 'URLLC': 1, 'mMTC': 2}.get(slice_info['slice'], 0),
            '5qi': slice_info.get('5qi', 6),
            'traffic_intensity': (packet_size * pps) / 1000000
        }
        
        # Run detection
        detection_result = detection_pipeline(features_dict, src_ip, is_simulated=True)
        
        # Always block in simulation for demo
        blocked = block_ip(src_ip, "Simulated DDoS Attack")
        
        # Send to frontend
        try:
            requests.post(NODE_LIVEPACKET, json={
                "srcIP": src_ip,
                "dstIP": dst_ip,
                "protocol": protocol,
                "packetSize": packet_size,
                "timestamp": int(now * 1000),
                "isMalicious": True,
                "confidence": detection_result.get('confidence', 0.99),
                "packet_data": {"simulated": True},
                "network_slice": slice_info['slice'],
                "explanation": detection_result.get('explanation', {}),
                "model_used": "simulation"
            }, timeout=0.1)
        except:
            pass
        
        return jsonify({
            "status": "simulated",
            "prediction": "ddos",
            "confidence": detection_result.get('confidence', 0.99),
            "blocked": blocked,
            "explanation": detection_result.get('explanation', {}),
            "slice": slice_info['slice']
        })
        
    except Exception as e:
        log.error(f"Simulation error: {e}")
        return jsonify({"error": str(e)}), 500

@app.post("/start-capture")
def start_capture_endpoint():
    global running
    if running:
        return jsonify({"status": "already_running"})
    running = True
    threading.Thread(target=capture_loop, daemon=True).start()
    log.info("🎬 CAPTURE STARTED VIA API")
    return jsonify({"status": "capturing", "ip": LAPTOP_IP})

@app.post("/stop-capture")
def stop_capture_endpoint():
    global running
    running = False
    log.info("🛑 CAPTURE STOPPED VIA API")
    return jsonify({"status": "stopped"})

@app.get("/health")
def health():
    try:
        ryu_ok = requests.get(f"{RYU_URL}/stats/switches", timeout=2).ok
    except:
        ryu_ok = False
    
    return jsonify({
        "status": "LIVE",
        "version": "3.0.0",
        "laptop_ip": LAPTOP_IP,
        "ryu_reachable": ryu_ok,
        "ml_engine_ready": ml_engine is not None,
        "models_loaded": True,
        "features_count": len(feature_names) if 'feature_names' in locals() else 0,
        "blocked_ips": len(BLOCKED_IPS),
        "capturing": running
    })

@app.post("/unblock")
def unblock_endpoint():
    data = request.get_json(force=True) or {}
    ip = data.get("ip")
    success = False
    if ip:
        success = unblock_ip(ip)
    return jsonify({"success": success})

@app.post("/predict")
def predict_endpoint():
    """Direct prediction API for testing"""
    try:
        data = request.get_json()
        features = data.get("features", [])
        
        if not features:
            return jsonify({"error": "No features provided"}), 400
        
        # Scale features
        features_scaled = scaler.transform([features])
        
        # Get prediction
        result = ml_engine.detect_ddos(features_scaled)
        explanation = explainer.explain_prediction(features_scaled[0], result)
        
        return jsonify({
            **result,
            "explanation": explanation,
            "features_count": len(features)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    log.info("="*60)
    log.info("🚀 SENTINELAI 3.0.0 STARTING")
    log.info("="*60)
    log.info(f"📡 Laptop IP: {LAPTOP_IP}")
    log.info(f"🤖 ML Engine: {'READY' if ml_engine else 'FAILED'}")
    log.info(f"🧠 Online Learning: {'ACTIVE' if online_learner else 'INACTIVE'}")
    log.info(f"🔍 Explainable AI: {'READY' if explainer else 'FAILED'}")
    log.info(f"📶 5G Integration: {'READY' if fiveg_core else 'INACTIVE'}")
    log.info(f"🛡️  Models Loaded: {len(feature_names) if 'feature_names' in locals() else 0} features")
    log.info("="*60)
    
    app.run(host="0.0.0.0", port=5001, debug=False, threaded=True)