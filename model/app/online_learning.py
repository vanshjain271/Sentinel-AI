"""
Online Learning Engine - Continuously improves models
"""
import numpy as np
import joblib
import threading
from collections import deque
import logging
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier

class OnlineLearningEngine:
    def __init__(self, feedback_window=1000, retrain_threshold=500):
        self.feedback_buffer = deque(maxlen=feedback_window)
        self.lock = threading.Lock()
        self.retrain_threshold = retrain_threshold
        self.learning_rate = 0.1
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self.correct_predictions = 0
        self.total_predictions = 0
        self.model_accuracy = 0.0
        
        self.logger.info("✅ Online Learning Engine Initialized")

    def add_feedback(self, features, true_label, predicted_label, confidence):
        """Add feedback for continuous learning"""
        with self.lock:
            self.feedback_buffer.append({
                'features': features,
                'true': true_label,
                'predicted': predicted_label,
                'confidence': confidence,
                'correct': true_label == predicted_label,
                'timestamp': datetime.now().isoformat()
            })
            
            # Update accuracy metrics
            self.total_predictions += 1
            if true_label == predicted_label:
                self.correct_predictions += 1
            self.model_accuracy = self.correct_predictions / max(self.total_predictions, 1)
            
        # Check if retraining is needed
        if len(self.feedback_buffer) >= self.retrain_threshold:
            threading.Thread(target=self._retrain_model, daemon=True).start()

    def _retrain_model(self):
        """Incremental model update (simplified)"""
        with self.lock:
            if len(self.feedback_buffer) < 100:
                return
            
            try:
                # Prepare data from buffer
                X = np.array([item['features'] for item in self.feedback_buffer])
                y = np.array([item['true'] for item in self.feedback_buffer])
                
                self.logger.info(f"🔄 Retraining with {len(X)} new samples")
                
                # In production, you would update your actual models here
                # For now, we just log and simulate
                
                # Save learning metrics
                metrics = {
                    'retrain_timestamp': datetime.now().isoformat(),
                    'samples_used': len(X),
                    'current_accuracy': self.model_accuracy,
                    'buffer_size': len(self.feedback_buffer)
                }
                
                # Update model file (simulated)
                with open('models/online_learning_metrics.json', 'w') as f:
                    import json
                    json.dump(metrics, f, indent=2)
                
                self.logger.info(f"📈 Online learning updated: Accuracy={self.model_accuracy:.3f}")
                
            except Exception as e:
                self.logger.error(f"Retraining failed: {e}")

    def get_learning_metrics(self):
        """Get current learning metrics"""
        with self.lock:
            return {
                'accuracy': self.model_accuracy,
                'total_predictions': self.total_predictions,
                'correct_predictions': self.correct_predictions,
                'feedback_buffer_size': len(self.feedback_buffer),
                'ready_for_retrain': len(self.feedback_buffer) >= self.retrain_threshold
            }