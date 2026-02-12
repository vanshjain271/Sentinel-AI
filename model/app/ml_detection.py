"""
ML Detection Engine - Uses your trained models
"""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import logging
from datetime import datetime
from pathlib import Path
import xgboost as xgb
import tensorflow as tf

class MLDetectionEngine:
    def __init__(self, model_base_path="models/"):
        self.model_base_path = Path(__file__).parent.parent / model_base_path
        self.scaler = None
        self.feature_names = None
        self.ensemble_model = None
        self.xgb_model = None
        self.rf_model = None
        self.lstm_model = None
        self.autoencoder = None
        self.logger = logging.getLogger(__name__)
        self.load_models()

    def load_models(self):
        """Load all models from Colab training"""
        try:
            # Load scaler and feature names
            self.scaler = joblib.load(self.model_base_path / "5g_ddos_scaler.pkl")
            self.feature_names = joblib.load(self.model_base_path / "5g_feature_names.pkl")
            
            # Load ensemble model (primary)
            self.ensemble_model = joblib.load(self.model_base_path / "ensemble_voting.pkl")
            
            # Load individual models
            self.rf_model = joblib.load(self.model_base_path / "random_forest.pkl")
            self.xgb_model = xgb.XGBClassifier()
            self.xgb_model.load_model(self.model_base_path / "xgboost.json")
            
            # Load neural models
            self.lstm_model = tf.keras.models.load_model(self.model_base_path / "lstm.keras")
            self.autoencoder = tf.keras.models.load_model(self.model_base_path / "autoencoder.keras")
            
            self.logger.info(f"✅ Models loaded: {len(self.feature_names)} features")
            self.logger.info(f"   → Ensemble Model: {self.ensemble_model.__class__.__name__}")
            self.logger.info(f"   → Random Forest: {self.rf_model.n_estimators} trees")
            self.logger.info(f"   → XGBoost: Ready")
            self.logger.info(f"   → LSTM: Ready")
            self.logger.info(f"   → Autoencoder: Ready")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load models: {e}")
            self.initialize_fallback()

    def initialize_fallback(self):
        """Fallback if models fail"""
        self.logger.warning("Using fallback models")
        self.feature_names = ['packet_size', 'packets_per_second', 'avg_packet_size', 'protocol']
        self.scaler = StandardScaler()
        
        # Simple fallback model
        X = np.random.randn(100, len(self.feature_names))
        y = (np.random.rand(100) > 0.7).astype(int)
        X_scaled = self.scaler.fit_transform(X)
        
        self.ensemble_model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.ensemble_model.fit(X_scaled, y)

    def prepare_features(self, features_array):
        """Prepare features for prediction"""
        # Ensure correct feature count
        if len(features_array) != len(self.feature_names):
            self.logger.warning(f"Feature mismatch: got {len(features_array)}, expected {len(self.feature_names)}")
            # Pad or truncate
            if len(features_array) < len(self.feature_names):
                features_array = np.pad(features_array, (0, len(self.feature_names) - len(features_array)))
            else:
                features_array = features_array[:len(self.feature_names)]
        
        return features_array.reshape(1, -1)

    def detect_ddos(self, features_scaled):
        """Main detection using ensemble model"""
        try:
            # Get ensemble prediction
            prediction = self.ensemble_model.predict(features_scaled)[0]
            proba = self.ensemble_model.predict_proba(features_scaled)[0]
            confidence = float(max(proba))
            
            # Get individual model predictions for consensus
            rf_pred = self.rf_model.predict(features_scaled)[0]
            xgb_pred = self.xgb_model.predict(features_scaled)[0]
            
            # Consensus logic
            predictions = [prediction, rf_pred, xgb_pred]
            consensus = 1 if sum(predictions) >= 2 else 0
            
            # Autoencoder anomaly score
            if hasattr(self, 'autoencoder') and self.autoencoder:
                reconstruction = self.autoencoder.predict(features_scaled)
                mse = np.mean(np.power(features_scaled - reconstruction, 2))
                anomaly_score = float(mse)
            else:
                anomaly_score = 0.0
            
            # Final decision with anomaly consideration
            if anomaly_score > 0.5:  # High reconstruction error
                final_prediction = 1  # Likely anomaly/DDoS
                confidence = max(confidence, 0.7)
            else:
                final_prediction = consensus
            
            threat_level = "CRITICAL" if confidence > 0.9 else "HIGH" if confidence > 0.7 else "MEDIUM" if confidence > 0.5 else "LOW"
            
            return {
                "prediction": "ddos" if final_prediction == 1 else "normal",
                "confidence": round(confidence, 4),
                "threat_level": threat_level,
                "consensus": f"{sum(predictions)}/3 models agree",
                "anomaly_score": round(anomaly_score, 4),
                "model_used": "ensemble",
                "timestamp": datetime.now().isoformat(),
                "features_count": len(self.feature_names)
            }
            
        except Exception as e:
            self.logger.error(f"Detection error: {e}")
            return {
                "prediction": "unknown",
                "confidence": 0.0,
                "threat_level": "UNKNOWN",
                "error": str(e)
            }

    def get_model_info(self):
        """Get information about loaded models"""
        return {
            "ensemble_model": self.ensemble_model.__class__.__name__ if self.ensemble_model else None,
            "feature_count": len(self.feature_names) if self.feature_names else 0,
            "models_loaded": {
                "ensemble": self.ensemble_model is not None,
                "random_forest": self.rf_model is not None,
                "xgboost": self.xgb_model is not None,
                "lstm": self.lstm_model is not None,
                "autoencoder": self.autoencoder is not None
            }
        }