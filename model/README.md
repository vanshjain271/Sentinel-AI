# SENTINEL AI - ML Models Documentation

## 📁 Project Structure

```
model/
├── app/                          # Flask Application
│   ├── app.py                    # Main Flask Application
│   ├── explainable_ai.py         # XAI for model predictions (SHAP, LIME)
│   ├── feature_extraction.py     # Packet feature extraction (17 features)
│   ├── fiveg_core_integration.py # 5G Core integration
│   ├── flow_capture.py           # Network flow capture (Scapy/pyshark)
│   ├── mitigation_engine.py      # Attack mitigation logic
│   ├── ml_detection.py           # ML detection engine (Ensemble models)
│   ├── nas_analyzer.py           # Neural Architecture Search
│   ├── network_slicing.py        # 5G network slicing (eMBB/URLLC/mMTC)
│   ├── online_learning.py        # Online model updates
│   ├── performance_cache.py      # Performance optimization
│   ├── sdn_controller.py         # SDN Ryu controller integration
│   ├── __init__.py
│   └── test/                     # Testing scripts
│       ├── compare_models.py     # Model comparison
│       ├── manual_block_test.py  # Manual block tests
│       ├── test_enhanced_model.py
│       ├── test_ryu_connection.py
│       ├── train_model.py        # Model training
│       └── training.py           # Training utilities
│
├── models/                       # Trained Models & Data
│   ├── 5g_ddos_dataset.csv       # Training dataset (5G DDoS traffic)
│   ├── 5g_ddos_scaler.pkl        # Feature scaler (StandardScaler)
│   ├── 5g_feature_names.pkl      # Feature names (17 features)
│   ├── autoencoder.keras         # Autoencoder for anomaly detection
│   ├── ensemble_voting.pkl       # Voting ensemble classifier
│   ├── inference.py              # Inference utilities
│   ├── lstm.keras                # LSTM for temporal patterns
│   ├── mininet.py                # Mininet network emulation
│   ├── model_metadata.json       # Model metadata
│   ├── model_performance_summary.csv
│   ├── random_forest.pkl         # Random Forest model
│   ├── rf_feature_importance.csv
│   ├── shap_force_plot.png       # SHAP force plot visualization
│   ├── shap_summary.png          # SHAP summary plot
│   ├── shap_values.csv           # SHAP values
│   ├── xgboost.json              # XGBoost model (JSON format)
│   └── xgboost.pkl               # XGBoost model (pickle format)
│
├── requirements.txt              # Python Dependencies
├── setup_windows.bat             # Windows setup script
├── run.sh                        # Linux/Mac startup script
├── TENSORFLOW_FIX_WINDOWS.md     # TensorFlow Windows DLL fix
└── README.md                     # This file
```

## 📁 Model Files

### Core Models
- `random_forest.pkl` - Primary Random Forest classifier
- `xgboost.pkl` / `xgboost.json` - XGBoost model for gradient boosting
- `autoencoder.keras` - Autoencoder for anomaly detection
- `lstm.keras` - LSTM for temporal pattern detection
- `ensemble_voting.pkl` - Voting ensemble classifier

## 🧠 Model Details

### Feature Set (17 features)
1. **Basic Features:**
   - Packet size
   - Protocol indicators (TCP/UDP/ICMP)
   - Port information
   - Header lengths

2. **Flow Features:**
   - Flow duration
   - Packet/byte counts
   - Packet/byte rates
   - Flow age

3. **Statistical Features:**
   - Packet size statistics (mean, std, min, max)
   - Inter-arrival time statistics (mean, std)

4. **Protocol Features:**
   - TCP flag counts (SYN, ACK, PSH, URG, FIN, RST)
   - Protocol entropy

### Ensemble Configuration
- **Weighted Average:** Combines predictions from all models
- **Dynamic Weights:** Updated based on recent performance
- **Fallback:** If primary model fails, uses backup models

## 🚀 Performance Targets
- Accuracy: >99%
- False Positive Rate: <1%
- Inference Time: <50ms
- Detection Rate: >99.5% for known attacks
- Zero-day detection: >80% via anomaly detection

## 🔄 Model Updates
1. **Online Learning:** Continuously updates with new data
2. **Drift Detection:** Alerts when model performance degrades
3. **Auto-retraining:** Triggers retraining when needed
4. **A/B Testing:** Tests new models before deployment

## 📊 Evaluation Metrics
- Accuracy, Precision, Recall, F1-Score
- ROC-AUC, PR-AUC
- Confusion Matrix
- Inference latency
- Memory usage

## 🛡️ Security Considerations
- Models are validated for adversarial robustness
- Input sanitization prevents model poisoning
- Secure model loading prevents tampering
- Regular integrity checks