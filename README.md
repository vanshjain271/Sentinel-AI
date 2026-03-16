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
🧪 Cross-Domain Research Experiments

To evaluate the robustness of Sentinel-AI beyond telecom networks, a dedicated research pipeline was developed to study cross-domain generalization of intrusion detection models.

The key research question investigated:

Can AI models trained on one network environment detect DDoS attacks in a different network environment?

Different network infrastructures (telecom, enterprise, cloud) expose different traffic features. Sentinel-AI experiments evaluate whether models trained on one domain remain effective in another.

Two public cybersecurity datasets were used for evaluation.

Dataset	Description
UNSW-NB15	Enterprise intrusion detection dataset
CIC-DDoS2019	Modern large-scale DDoS attack dataset

Experiments were conducted using both domain-specific features and domain-agnostic universal traffic features.

📊 Experiment Results Summary

| Experiment       | Train Dataset      | Test Dataset | Accuracy | Key                                      |
| ---------------- | ------------------ | ------------ | -------- | ------------------------------------------------- |
| **Experiment 1** | Telecom 5G Dataset | UNSW-NB15    | 0.36     | Telecom-trained models fail on enterprise traffic |
| **Experiment 2** | UNSW-NB15          | UNSW-NB15    | 0.94     | Dataset is learnable with standard ML models      |
| **Experiment 3** | Telecom 5G Dataset | CIC-DDoS2019 | 0.36     | Telecom models fail on modern DDoS traffic        |
| **Experiment 4** | UNSW-NB15          | CIC-DDoS2019 | 0.98     | Universal features enable cross-domain detection  |
| **Experiment 5** | CIC-DDoS2019       | UNSW-NB15    | 0.63     | High attack recall across datasets                |

🔬 Key Research Findings

The experiments reveal several important insights:

1️⃣ Domain-Specific Models Do Not Generalize

Models trained on telecom-specific features (such as 5qi, gNB_id, and pdu_session_id) fail when applied to enterprise network datasets.

This demonstrates that feature domain mismatch significantly reduces IDS effectiveness.

2️⃣ Universal Traffic Features Improve Cross-Domain Detection

To overcome feature mismatch, a universal feature abstraction layer was introduced using domain-agnostic traffic statistics:

protocol
flow_duration
packet_mean
packet_std
packet_rate

These features exist in most network environments and allow models to detect anomalous traffic patterns independent of infrastructure.

3️⃣ Bidirectional Cross-Dataset Generalization

Experiments 4 and 5 demonstrate that models trained using universal traffic features can detect attacks across different datasets in both directions:

UNSW → CIC detection
CIC → UNSW detection

This indicates that universal traffic statistics capture fundamental characteristics of DDoS behavior.

🧠 Research Pipeline

A separate experimental framework was implemented inside:

model/research_experiments/

This pipeline supports:

Dataset loading

Feature abstraction

Cross-dataset model evaluation

Automated experiment logging

Metrics and confusion matrix generation

Each experiment is versioned using Git tags for full reproducibility.

Experiment	Git Tag
Experiment 1	experiment-1-telecom-unsw
Experiment 2	experiment-2-unsw-baseline
Experiment 3	experiment-3-cic-ddos
Experiment 4	experiment-4-universal-features
Experiment 5	experiment-5-reverse-cross-dataset
📈 Example Experiment Metrics (Experiment 5)

Reverse cross-dataset evaluation (CIC → UNSW):

Metric	Value
Accuracy	0.63
Precision	0.64
Recall	0.94
F1 Score	0.76

The model detects 94% of attacks, demonstrating strong recall across different network environments.
---
🧪 Sentinel-AI Research Experiment Pipeline
To systematically evaluate model generalization across different network environments, Sentinel-AI includes a dedicated experimental framework.

The research pipeline isolates dataset processing, feature abstraction, training, and evaluation into reproducible modules.
Dataset Loader
      ↓
Feature Mapping / Universal Feature Layer
      ↓
Model Training (RandomForest / XGBoost)
      ↓
Cross-Dataset Evaluation
      ↓
Metrics Generation
      ↓
Confusion Matrix
      ↓
Experiment Registry Logging
      ↓
Result Storage

This pipeline enables controlled experimentation for evaluating cross-domain intrusion detection performance

Research Pipeline Components
| Module             | Purpose                                             |
| ------------------ | --------------------------------------------------- |
| datasets           | Dataset loading and preprocessing                   |
| preprocessing      | Feature mapping and normalization                   |
| training_baselines | Baseline model training                             |
| models             | Universal feature models                            |
| evaluation         | Metrics computation and confusion matrix generation |
| results            | Stored experiment outputs                           |

Stored Experiment Outputs

Each experiment automatically stores:

Performance metrics (JSON)

Confusion matrices (CSV)

Experiment summary tables

Registry entries documenting experiment parameters

This ensures full reproducibility of results


## 🗂 Repository Structure

```
Sentinel-AI/
│
├── frontend/            # React Dashboard (Port 5173)
│
├── backend/             # Node.js API Server (Port 3000)
│
├── model/               # ML Engine + Flask API (Port 5001)
│   │
│   ├── app/             # Flask ML service
│   │   ├── app.py
│   │   ├── feature_extraction.py
│   │   ├── ml_detection.py
│   │   ├── mitigation_engine.py
│   │   ├── explainable_ai.py
│   │   ├── network_slicing.py
│   │   ├── online_learning.py
│   │   └── sdn_controller.py
│   │
│   ├── models/          # Trained models
│   │   ├── random_forest.pkl
│   │   ├── xgboost.pkl
│   │   ├── lstm.keras
│   │   ├── autoencoder.keras
│   │   ├── ensemble_voting.pkl
│   │   └── model_metadata.json
│   │
│   ├── research_experiments/   # Cross-domain IDS research framework
│   │   │
│   │   ├── datasets/           # Dataset loading utilities
│   │   ├── preprocessing/      # Feature abstraction layer
│   │   ├── models/             # Experimental models
│   │   ├── training_baselines/ # Baseline training scripts
│   │   ├── evaluation/         # Metrics + confusion matrix generation
│   │   │
│   │   ├── run_experiment.py
│   │   ├── run_experiment_4_universal.py
│   │   ├── run_experiment_5_reverse.py
│   │   │
│   │   ├── results/
│   │   │   ├── metrics/
│   │   │   ├── confusion_matrices/
│   │   │   ├── tables/
│   │   │   └── experiment_registry.md
│   │   │
│   │   └── README.md
│
├── DDOS/                # Locust attack simulation scripts
│
├── README.md
├── LICENSE
└── .gitignore
```
📚 Research Contributions

Sentinel-AI contributes to cybersecurity research in several areas:

1️⃣ Cross-Domain Intrusion Detection Evaluation

Demonstrates that intrusion detection models trained on telecom-specific datasets fail to generalize across enterprise and cloud traffic environments.

2️⃣ Universal Traffic Feature Abstraction

Introduces a domain-agnostic feature layer enabling cross-dataset intrusion detection.

3️⃣ AI + SDN Autonomous Defense

Combines machine learning detection with software-defined networking mitigation for real-time automated defense.

4️⃣ Reproducible Experimental Framework

Provides a modular pipeline for evaluating IDS models across heterogeneous datasets.

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

🧑‍💻 Author

Vansh Jain
Cybersecurity & AI Researcher

Creator and lead developer of Sentinel-AI, an AI-driven DDoS detection and mitigation architecture integrating machine learning, SDN automation, and real-time network analytics.

All intellectual property and implementation of Sentinel-AI are developed and maintained by Vansh Jain.