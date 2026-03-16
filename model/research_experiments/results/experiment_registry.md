# Sentinel-AI Experiment Registry

This file records all experiments conducted to evaluate Sentinel-AI.

---

# Experiment 1
### Title
Sentinel Models on External Enterprise Dataset

### Dataset
UNSW-NB15

### Objective
Evaluate whether Sentinel-AI models trained on 5G network traffic generalize to enterprise network traffic.

### Models Used
- Random Forest
- XGBoost
- Ensemble Voting

### Method
External dataset features were aligned with Sentinel feature schema using feature mapping.

### Results
Accuracy ≈ 0.36  
Precision = 0  
Recall = 0  
F1 = 0  
ROC-AUC = 0.5  

### Interpretation
Sentinel models predicted all traffic as benign.

### Conclusion
Cross-domain generalization failure due to mismatch between:
- 5G traffic features
- enterprise network traffic features

---

# Experiment 2
### Title
Baseline Training on UNSW-NB15 Dataset

### Dataset
UNSW-NB15

### Objective
Verify whether the UNSW dataset is learnable by standard ML models.

### Models Used
- Random Forest
- XGBoost

### Method
Models were trained directly on UNSW feature space after preprocessing and categorical encoding.

### Results

Random Forest
Accuracy: 0.9427  
Precision: 0.9560  
Recall: 0.9542  
F1: 0.9551  
ROC-AUC: 0.9894  

XGBoost
Accuracy: 0.9383  
Precision: 0.9525  
Recall: 0.9508  
F1: 0.9516  
ROC-AUC: 0.9892  

### Interpretation
The UNSW dataset is easily learnable by standard ML models.

### Conclusion
The poor performance of Sentinel models in Experiment 1 was caused by feature domain mismatch rather than dataset difficulty.

---

## Experiment 3 — Sentinel on CIC-DDoS2019

Dataset: CIC-DDoS2019  
Samples: 800,000 flows (subset)

Models evaluated:
- Random Forest
- XGBoost
- Ensemble Voting

Results:

Accuracy: 0.3609  
Precision: 0.0000  
Recall: 0.0000  
F1-score: 0.0000  
ROC-AUC: 0.50

Confusion Matrix:

[[93000, 0],
 [164673, 0]]

Observation:

The model classified all traffic as benign and failed to detect any attack instances.

Conclusion:

Models trained on telecom traffic features fail to generalize to enterprise network traffic due to feature distribution mismatch.


---
## Experiment 4 — Universal Feature Model (UNSW → CIC)

Training Dataset: UNSW-NB15  
Testing Dataset: CIC-DDoS2019

Features:
protocol
flow_duration
packet_mean
packet_std
packet_rate

Model:
RandomForestClassifier

Results:

Accuracy: 0.672  
Precision: 0.989  
Recall: 0.673  
F1 Score: 0.801  
ROC-AUC: 0.65

Confusion Matrix:

[[9086, 5409],
 [256982, 528523]]

Observation:
Universal traffic features significantly improved cross-domain detection compared to Sentinel telecom-specific features.




# Experiment 5 — Reverse Cross-Dataset Evaluation

## Objective
Evaluate whether a model trained on CIC-DDoS2019 can detect attacks in the UNSW-NB15 dataset using universal traffic features.

## Setup

Train Dataset:
CIC-DDoS2019

Test Dataset:
UNSW-NB15

Model:
RandomForest

Features:
protocol
flow_duration
packet_mean
packet_std
packet_rate

## Results

Accuracy: 0.626
Precision: 0.641
Recall: 0.942
F1 Score: 0.763

## Key Insight

The model detects most attacks (94% recall) but produces false positives due to domain differences between datasets.

This demonstrates partial cross-domain generalization using universal traffic features.
---
# Planned Experiments

## Experiment 6
Improved Sentinel Architecture

Possible improvements:
- domain adaptation
- feature translation
- transfer learning
- improved threat risk scoring