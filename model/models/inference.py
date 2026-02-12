
import joblib
import numpy as np
import pandas as pd

class EliteDDoSDetector:
    """Production-ready DDoS detector using elite models"""
    
    def __init__(self, model_path='ensemble_voting_elite.pkl'):
        self.scaler = joblib.load('5g_ddos_scaler.pkl')
        self.feature_names = joblib.load('5g_feature_names.pkl')
        self.model = joblib.load(model_path)
        
    def predict(self, features):
        """Predict if traffic is DDoS"""
        # Scale features
        features_scaled = self.scaler.transform([features])
        
        # Get prediction and probability
        prediction = self.model.predict(features_scaled)[0]
        probability = self.model.predict_proba(features_scaled)[0][1]
        
        return {
            'is_ddos': bool(prediction),
            'confidence': float(probability),
            'risk_level': 'HIGH' if probability > 0.8 else 'MEDIUM' if probability > 0.6 else 'LOW'
        }

# Usage example:
# detector = EliteDDoSDetector()
# result = detector.predict(feature_array)
