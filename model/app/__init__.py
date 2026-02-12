"""
SentinelAI - DDoS Detection System for 5G Networks
"""

__version__ = "3.0.0"
__author__ = "SentinelAI Team"
__description__ = "AI-Powered DDoS Detection & Mitigation for 5G/6G Networks"

# Core modules
from .ml_detection import MLDetectionEngine
from .mitigation_engine import MitigationEngine
from .network_slicing import get_network_slice
from .sdn_controller import SDNController
from .online_learning import OnlineLearningEngine
from .explainable_ai import DDoSExplainer
from .fiveg_core_integration import FiveGCoreIntegration

__all__ = [
    'MLDetectionEngine',
    'MitigationEngine',
    'get_network_slice',
    'SDNController',
    'OnlineLearningEngine',
    'DDoSExplainer',
    'FiveGCoreIntegration'
]