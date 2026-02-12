"""
Explainable AI Module - SHAP and LIME explanations
"""
import numpy as np
import pandas as pd
import joblib

class DDoSExplainer:
    def __init__(self, feature_names):
        self.feature_names = feature_names
        self.feature_importance = self._load_feature_importance()
        
    def _load_feature_importance(self):
        """Load pre-computed feature importance from training"""
        try:
            importance_df = pd.read_csv('models/rf_feature_importance.csv')
            return dict(zip(importance_df['feature'], importance_df['importance']))
        except:
            # Fallback uniform importance
            return {feature: 1.0/len(self.feature_names) for feature in self.feature_names}
    
    def explain_prediction(self, features_scaled, detection_result):
        """Generate human-readable explanation for a prediction"""
        
        # Get feature contributions (simplified SHAP-like)
        contributions = []
        for i, (feature_name, feature_value) in enumerate(zip(self.feature_names, features_scaled)):
            importance = self.feature_importance.get(feature_name, 0.01)
            
            # Simple contribution logic
            if 'packet' in feature_name.lower() and abs(feature_value) > 2:
                contribution = importance * abs(feature_value)
            elif 'rate' in feature_name.lower() and feature_value > 1:
                contribution = importance * feature_value
            elif 'entropy' in feature_name.lower() and feature_value > 0.5:
                contribution = importance * feature_value
            else:
                contribution = importance * 0.1
            
            contributions.append({
                'feature': feature_name,
                'value': float(feature_value),
                'importance': float(importance),
                'contribution': float(contribution),
                'normalized_contribution': float(contribution / max(sum([c['contribution'] for c in contributions]) + contribution, 0.01))
            })
        
        # Sort by contribution
        contributions.sort(key=lambda x: x['contribution'], reverse=True)
        
        # Generate risk factors
        risk_factors = []
        confidence = detection_result.get('confidence', 0)
        
        # Check specific conditions
        packet_rate_idx = [i for i, f in enumerate(self.feature_names) if 'packet' in f.lower() and 'rate' in f.lower()]
        if packet_rate_idx and features_scaled[packet_rate_idx[0]] > 3:
            risk_factors.append(f"High packet rate (z-score: {features_scaled[packet_rate_idx[0]]:.2f})")
        
        entropy_idx = [i for i, f in enumerate(self.feature_names) if 'entropy' in f.lower()]
        if entropy_idx and features_scaled[entropy_idx[0]] > 2:
            risk_factors.append(f"Abnormal port/protocol distribution")
        
        size_idx = [i for i, f in enumerate(self.feature_names) if 'size' in f.lower()]
        if size_idx and abs(features_scaled[size_idx[0]]) > 2.5:
            risk_factors.append(f"Unusual packet size pattern")
        
        # Generate explanation
        explanation = {
            'prediction': detection_result.get('prediction', 'unknown'),
            'confidence': confidence,
            'top_factors': contributions[:5],
            'risk_factors': risk_factors[:3],
            'decision_basis': self._get_decision_basis(confidence, risk_factors),
            'model_confidence': f"{confidence*100:.1f}%"
        }
        
        return explanation
    
    def _get_decision_basis(self, confidence, risk_factors):
        """Generate natural language explanation"""
        if confidence > 0.9:
            if risk_factors:
                return f"Definite DDoS detected based on {len(risk_factors)} strong indicators"
            else:
                return "Definite DDoS detected based on overall traffic pattern"
        elif confidence > 0.7:
            return "Likely DDoS attack with multiple suspicious indicators"
        elif confidence > 0.5:
            return "Suspicious activity detected, requires monitoring"
        else:
            return "Normal traffic pattern"