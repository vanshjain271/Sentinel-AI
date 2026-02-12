# 🌐 SENTINEL AI

**AI-Driven DDoS Detection & Mitigation for 5G Networks using Machine Learning + SDN + Real-Time Analytics**

---

## 📌 Project Overview

**Sentinel AI** is an enterprise-grade, AI-powered **5G DDoS Detection & Mitigation System** integrating:

- **Machine Learning (Python + Flask)** - Ensemble models with XAI explanations
- **Software-Defined Networking (SDN) via Ryu Controller** - Dynamic flow control
- **Mininet network emulation** - Network topology simulation
- **React real-time monitoring dashboard** - Live traffic visualization
- **Node.js backend orchestration** - API server with WebSocket support
- **Locust traffic & DDoS load testing** - Performance testing suite

The system delivers **real-time attack detection**, **5G network slicing support**, and **autonomous mitigation** using OpenFlow rules, with comprehensive testing and monitoring capabilities.

---

## ⭐ Key Capabilities

### 🔥 AI-Powered Detection
- **Ensemble ML Models**: RandomForest, XGBoost, LSTM, Autoencoder
- **Sub-50ms Inference**: Real-time packet classification
- **17 Feature Extraction**: Flow statistics, protocol analysis, temporal patterns
- **Explainable AI**: SHAP values, feature importance, decision reasoning
- **Online Learning**: Continuous model adaptation

### 📶 5G Network Slice Intelligence
- **eMBB Classification**: High-bandwidth traffic analysis
- **URLLC Detection**: Ultra-low latency attack identification
- **mMTC Monitoring**: Massive IoT device protection
- **Slice Isolation**: Network segmentation security

### 🧠 Self-Healing SDN Architecture
- **Automatic IP Blocking**: OpenFlow DROP rules via Ryu controller
- **Dynamic Flow Management**: Priority-based rule insertion
- **Auto-Recovery**: Intelligent unblocking after threat resolution
- **Fallback Mechanisms**: Rule-based detection when ML unavailable
- **Flow Cleanup**: Automatic expired rule removal

### 🔐 Advanced SDN Controller (Ryu)
- **REST API Integration**: `ryu.app.ofctl_rest` communication
- **OpenFlow 1.3 Support**: Modern protocol compatibility
- **Mininet Integration**: Network topology simulation
- **Real-time Rule Updates**: Dynamic flow table management
- **IP Quarantine System**: Configurable blocking timeouts

### 📊 Comprehensive Dashboard
- **Live Packet Monitoring**: Real-time traffic visualization
- **AI Explanation Panel**: Model prediction insights
- **Multi-Chart Analytics**: Normal/malicious/simulated traffic
- **5G Slice Performance**: Network segmentation metrics
- **Threat Management**: Blocked IP tracking and control

---

## 🏗 System Architecture

```
┌─────────────────┐      ┌───────────────────┐      ┌─────────────────┐
│   Traffic       │ ---> │  Packet Capture    │ ---> │  Feature         │
│ (Real/Simulated)│      │ (Scapy / Pyshark) │      │ Extraction       │
│   via Locust    │      │  + Mininet        │      │ (17 features)   │
└─────────────────┘      └───────────────────┘      └─────────────────┘
                              │
                              ▼
┌─────────────────┐      ┌───────────────────┐      ┌─────────────────┐
│ Network Slicing │ <--- │   ML Engine        │ ---> │  Backend API     │
│ eMBB/URLLC/mMTC │      │ Ensemble Models    │      │ Node.js + WS     │
│ Classification  │      │ + XAI Explanations│      │ (Port 3000)      │
└─────────────────┘      └───────────────────┘      └─────────────────┘
                              │
                              ▼
┌─────────────────┐      ┌───────────────────┐      ┌─────────────────┐
│ Ryu SDN         │ <--- │  Mitigation Logic │ ---> │  React Dashboard │
│ Controller      │      │ Auto-block IPs    │      │ Real-time UI     │
│ (Port 6633)     │      │ + Flow Rules      │      │ (Port 5173)      │
└─────────────────┘      └───────────────────┘      └─────────────────┘
```

---

## 🗂 Repository Structure

```
Sentinel-AI/
│
├── frontend/            # React Dashboard (Port 5173)
│   ├── src/
│   │   ├── components/  # React Components (Header, Stats, Charts, etc.)
│   │   ├── services/    # API Service Layer
│   │   ├── types/       # TypeScript Type Definitions
│   │   ├── App.tsx      # Main Application
│   │   └── main.tsx     # Entry Point
│   └── public/          # Static Assets
│
├── backend/             # Node.js API Server (Port 3000)
│   ├── controllers/     # Route Controllers
│   ├── middleware/      # Custom Middleware
│   ├── routes/          # Express Routes
│   ├── services/        # Business Logic Services
│   ├── tests/           # Unit, Integration, Performance Tests
│   └── utils/           # Utility Functions
│
├── model/               # ML Engine + Flask API (Port 5001)
│   ├── app/             # Flask Application
│   │   ├── app.py                   # Main Flask Application
│   │   ├── explainable_ai.py         # XAI for model predictions
│   │   ├── feature_extraction.py     # Packet feature extraction
│   │   ├── fiveg_core_integration.py # 5G Core integration
│   │   ├── flow_capture.py           # Network flow capture
│   │   ├── mitigation_engine.py      # Attack mitigation logic
│   │   ├── ml_detection.py           # ML detection engine
│   │   ├── nas_analyzer.py           # Neural Architecture Search
│   │   ├── network_slicing.py        # 5G network slicing
│   │   ├── online_learning.py        # Online model updates
│   │   ├── performance_cache.py      # Performance optimization
│   │   ├── sdn_controller.py         # SDN Ryu controller
│   │   └── test/                     # Model training & testing
│   │       ├── compare_models.py     # Model comparison
│   │       ├── manual_block_test.py  # Manual block tests
│   │       ├── test_enhanced_model.py
│   │       ├── test_ryu_connection.py
│   │       ├── train_model.py        # Model training
│   │       └── training.py           # Training utilities
│   ├── models/          # Trained Models (.keras, .pkl, .json)
│   │   ├── 5g_ddos_dataset.csv       # Training dataset
│   │   ├── 5g_ddos_scaler.pkl        # Feature scaler
│   │   ├── 5g_feature_names.pkl      # Feature names
│   │   ├── autoencoder.keras         # Autoencoder model
│   │   ├── ensemble_voting.pkl       # Voting ensemble
│   │   ├── inference.py              # Inference utilities
│   │   ├── lstm.keras                # LSTM model
│   │   ├── mininet.py                # Mininet topology
│   │   ├── model_metadata.json       # Model metadata
│   │   ├── model_performance_summary.csv
│   │   ├── random_forest.pkl         # Random Forest model
│   │   ├── rf_feature_importance.csv
│   │   ├── shap_values.csv           # SHAP values
│   │   ├── xgboost.json              # XGBoost model
│   │   └── xgboost.pkl               # XGBoost model
│   ├── requirements.txt   # Python Dependencies
│   ├── setup_windows.bat  # Windows setup script
│   └── TENSORFLOW_FIX_WINDOWS.md    # TensorFlow Windows fix
│
├── DDOS/                # Load Testing Scripts (Locust)
│   └── locustfile.py    # DDoS Simulation Tests
│
├── .gitignore
├── README.md
└── LICENSE
```

---

## ⚙️ Installation Guide

### 1️⃣ Install WSL & Ubuntu
```bash
wsl --install
wsl --install -d Ubuntu-20.04
```

### 2️⃣ Install Mininet
```bash
sudo apt update
sudo apt upgrade
sudo apt install mininet -y
sudo mn --test pingall
```

### 3️⃣ Install Python, Pip, Ryu
```bash
sudo apt install -y python3-pip
pip3 install --upgrade pip setuptools wheel
pip3 install eventlet==0.33.3
pip3 install ryu
```

### 4️⃣ Create Ryu Virtual Environment
```bash
python3.8 -m venv ryu-venv
source ryu-venv/bin/activate
ryu-manager --version
```

---

## 🖥️ Running the Entire System

### **Terminal 1 — Ryu SDN Controller**
```bash
source ryu-venv/bin/activate
ryu-manager ryu.app.simple_switch_13 ryu.app.ofctl_rest
```

### **Terminal 2 — Mininet Topology**
```bash
sudo mn --topo single,3 --mac --switch ovsk --controller=remote,ip=127.0.0.1,port=6633
```

### **Terminal 3 — Backend**
```bash
cd backend
npm install
npm start
```

### **Terminal 4 — Frontend**
```bash
cd frontend
npm install
npm run dev
```

### **Terminal 5 — ML Model (Flask)**
```bash
cd model
pip install -r requirements.txt
cd app
python app.py
```

---

## 🚦 Load Testing with Locust

### Install Locust:
```bash
pip install locust
```

### Run Locust:
```bash
locust -f locustfile.py
```

### Access Load Test UI:
```
http://localhost:8089
```

---

## 🧠 Machine Learning Models Included

| Model               | Purpose                     |
| ------------------- | --------------------------- |
| Random Forest       | Primary classifier          |
| XGBoost             | Gradient boosted accuracy   |
| LightGBM            | Fast, memory-efficient      |
| LSTM                | Temporal behavior detection |
| SVM                 | Boundary-based detection    |
| Logistic Regression | Baseline                    |
| KNN                 | Similarity detection        |

---

## 🔐 SDN Flow Control (Ryu)

The SDN controller manages network traffic through dynamic flow rules:

- **DROP rules** for blocking malicious IPs via OpenFlow
- **FORWARD rules** for allowing legitimate traffic
- **Flow table management** with priority-based rule insertion
- **Automatic cleanup** of expired flow rules
- **IP quarantine system** with configurable timeout

**Integration Points:**
- Ryu Controller REST API (`ryu.app.ofctl_rest`)
- OpenFlow 1.3 protocol support
- Mininet topology integration
- Real-time flow rule updates from ML engine

---

## 🔄 Self-Healing Pipeline

```
Packet Received → Feature Extraction (17 features)
     ↓
ML Ensemble Prediction (RandomForest + XGBoost + LSTM)
     ↓
Confidence Threshold Check (>80% = Attack)
     ↓
DDoS Detected → SDN Controller API Call
     ↓
OpenFlow DROP Rule Applied (IP Blocked)
     ↓
Traffic Monitoring for Recovery Patterns
     ↓
Auto-Unblock IP (Flow Rule Removed)
     ↓
System Returns to Normal State
     ↓
Online Learning Updates Model Weights
```

---

## 📊 Dashboard Features

**Real-Time Monitoring:**
- Live packet capture and analysis
- Real-time traffic charts (normal/malicious/simulated)
- Packet-per-second metrics and statistics
- Network slice performance monitoring

**AI-Powered Insights:**
- ML model confidence scores
- Explainable AI (XAI) predictions with SHAP values
- Feature importance visualization
- Detection reason explanations

**Network Security:**
- Blocked IP management with auto-unblock
- Threat level classification (high/medium/low)
- IP quarantine status tracking
- Mitigation action history

**5G Network Slicing:**
- eMBB, URLLC, mMTC slice classification
- Slice-specific traffic analysis
- Network performance metrics
- Slice isolation monitoring

**System Health:**
- Backend/ML service connectivity status
- Model performance metrics
- System resource monitoring
- Alert and notification system

---

## 🛠 Future Enhancements

- Docker & Kubernetes deployment
- Federated learning for edge devices
- 5G NR physical-layer packet support
- GPU-accelerated inference

---

## 📜 License

This project is for academic and research use.
Refer to the LICENSE file for details.

---

## 🎯 Conclusion

**Sentinel AI** provides a complete, autonomous, real-time DDoS defense system for modern 5G networks, utilizing:

- AI
- SDN
- Network slicing
- Real-time analytics
- Self-healing mechanisms

Perfect for research, enterprise labs, and advanced cybersecurity projects.
