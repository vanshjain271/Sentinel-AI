"""
enhanced_model_test.py
Tests your ENHANCED MODEL with live DDoS simulation
"""

import os
import time
import socket
import random
import threading
import numpy as np
import joblib
import pickle
from pathlib import Path

# ================================
# 1. CONFIG
# ================================
LAPTOP_IP = "192.168.0.100"  # ← YOUR LAPTOP IP
RYU_URL   = "http://192.168.56.101:8080"
MODEL_DIR = Path("../models")

MODEL_PATH     = MODEL_DIR / "randomforest_enhanced.pkl"
SCALER_PATH    = MODEL_DIR / "scaler_enhanced.pkl"
FEATURES_PATH  = MODEL_DIR / "feature_columns.pkl"

# Load model, scaler
print("Loading enhanced model...")
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
with open(FEATURES_PATH, "rb") as f:
    FEATURES = pickle.load(f)

print(f"Model: LOADED | Features: {model.n_features_in_} | Expected: {len(FEATURES)}")

# ================================
# 2. LIVE FLOW CACHE
# ================================
flow_cache = {}

def update_flow(src_ip, pkt_size, proto, sport=0, dport=0):
    now = time.time()
    if src_ip not in flow_cache:
        flow_cache[src_ip] = {
            "start": now,
            "packets": 0,
            "bytes": 0,
            "sizes": [],
            "iats": [],
            "src_ports": set(),
            "dst_ports": set(),
            "protos": set(),
            "last_ts": now
        }
    
    f = flow_cache[src_ip]
    f["packets"] += 1
    f["bytes"]   += pkt_size
    f["sizes"].append(pkt_size)
    if f["packets"] > 1:
        f["iats"].append(now - f["last_ts"])
    f["last_ts"] = now
    f["src_ports"].add(sport)
    f["dst_ports"].add(dport)
    f["protos"].add(proto)

    # Keep 1-second window
    if now - f["start"] > 1.0:
        f["start"] = now
        f["sizes"] = f["sizes"][-100:]
        f["iats"]  = f["iats"][-100:]

def extract_features(src_ip):
    if src_ip not in flow_cache:  # ← FIXED: was 'srcs_ip'
        return None
    f = flow_cache[src_ip]
    now = time.time()
    duration = max(now - f["start"], 1e-6)

    sizes = np.array(f["sizes"]) if f["sizes"] else np.array([0])
    iats  = np.array(f["iats"])  if f["iats"]  else np.array([0])

    return [
        duration,
        f["packets"],
        f["bytes"],
        f["packets"] / duration,
        f["bytes"]   / duration,
        sizes.mean(),
        sizes.std()  if len(sizes) > 1 else 0,
        sizes.min(),
        sizes.max(),
        iats.mean()  if len(iats) > 1 else 0,
        iats.std()   if len(iats) > 1 else 0,
        len(f["src_ports"]),
        len(f["dst_ports"]),
        len(f["protos"]),
        1 if "TCP" in f["protos"] else 0,
        1 if "UDP" in f["protos"] else 0,
        1 if "ICMP" in f["protos"] else 0,
    ]

# ================================
# 3. PREDICTION
# ================================
def predict_ddos(src_ip):
    feats = extract_features(src_ip)
    if not feats or len(feats) != 17:
        return False, 0.0
    X = scaler.transform([feats])
    prob = model.predict_proba(X)[0, 1]
    pred = model.predict(X)[0]
    return pred == 1, prob

# ================================
# 4. BLOCK VIA RYU
# ================================
import requests

def block_ip_ryu(ip):
    url = f"{RYU_URL}/stats/flowentry/add"
    rule = {
        "dpid": "0000000000000001",
        "priority": 60000,
        "match": {"ipv4_src": ip},
        "actions": []
    }
    try:
        r = requests.post(url, json=rule, timeout=3)
        if r.ok:
            print(f"SDN BLOCKED {ip}")
            return True
    except Exception as e:
        print(f"Ryu block failed: {e}")
    return False

# ================================
# 5. SIMULATE DDoS
# ================================
def simulate_ddos():
    print("\nStarting DDoS simulation (200 pps UDP flood)...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    target = (LAPTOP_IP, 5001)
    
    for i in range(1000):
        data = random._urandom(1024)
        sock.sendto(data, target)
        update_flow("1.2.3.4", len(data), "UDP", sport=1234, dport=5001)
        time.sleep(0.005)  # 200 pps
        
        if i % 50 == 0:
            is_attack, prob = predict_ddos("1.2.3.4")
            print(f"[{i}] PPS: ~200 | ML Prob: {prob:.3f} | Attack: {is_attack}")
            if is_attack and prob > 0.7:
                block_ip_ryu("1.2.3.4")
                print("DDoS DETECTED & BLOCKED!")
                break
    sock.close()

# ================================
# 6. RUN TEST
# ================================
if __name__ == "__main__":
    print("ENHANCED MODEL LIVE TEST")
    print(f"Target: {LAPTOP_IP}:5001")
    print(f"Ryu: {RYU_URL}")
    print("-" * 50)
    
    thread = threading.Thread(target=simulate_ddos, daemon=True)
    thread.start()
    
    thread.join(timeout=10)
    print("\nTest Complete! Check SENTINEL dashboard.")
    print("Unblock via: curl -X POST http://localhost:5001/unblock -d \"{\\\"ip\\\": \\\"1.2.3.4\\\"}\"")