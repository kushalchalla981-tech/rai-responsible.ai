import pandas as pd
import numpy as np
from typing import Dict, Any, Literal, List, Optional
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import warnings

MitigationType = Literal["reweighting", "threshold_optimization", "correlation_remover"]


class MitigationService:
    def __init__(self):
        self.min_samples = 100

    def apply_mitigation(
        self,
        data: pd.DataFrame,
        protected_attributes: List[str],
        target_attribute: str,
        mitigation_type: MitigationType,
        accuracy_cost: float = 0.05,
    ) -> Dict[str, Any]:
        if len(data) < self.min_samples:
            raise ValueError(f"Insufficient data for mitigation. Need {self.min_samples} samples.")

        if mitigation_type == "reweighting":
            return self._reweighting(data, protected_attributes, target_attribute)
        elif mitigation_type == "threshold_optimization":
            return self._threshold_optimization(data, protected_attributes, target_attribute, accuracy_cost)
        elif mitigation_type == "correlation_remover":
            return self._correlation_remover(data, protected_attributes, target_attribute)

        raise ValueError(f"Unknown mitigation type: {mitigation_type}")

    def _reweighting(
        self, data: pd.DataFrame, protected_attributes: List[str], target_attribute: str
    ) -> Dict[str, Any]:
        if not protected_attributes or protected_attributes[0] not in data.columns:
            raise ValueError("Protected attribute not found")

        prot_attr = protected_attributes[0]
        groups = data[prot_attr].unique()

        group_weights = {}
        total = len(data)

        for group in groups:
            group_count = (data[prot_attr] == group).sum()
            group_weights[group] = total / (len(groups) * group_count)

        weights = data[prot_attr].map(lambda x: group_weights.get(x, 1.0))

        original_mean = data[target_attribute].mean() if target_attribute in data.columns else 0
        weighted_mean = (data[target_attribute] * weights).mean()

        return {
            "mitigation_type": "reweighting",
            "method": "Reweighting",
            "description": "Adjusted sample weights to balance group representation",
            "group_weights": {str(k): v for k, v in group_weights.items()},
            "original_target_mean": original_mean,
            "adjusted_target_mean": weighted_mean,
            "estimated_accuracy_impact": abs(weighted_mean - original_mean),
        }

    def _threshold_optimization(
        self,
        data: pd.DataFrame,
        protected_attributes: List[str],
        target_attribute: str,
        accuracy_cost: float,
    ) -> Dict[str, Any]:
        if target_attribute not in data.columns:
            raise ValueError("Target attribute not found")

        features = [c for c in data.columns if c not in protected_attributes + [target_attribute]]
        features = [f for f in features if data[f].dtype in [np.int64, np.float64]]

        if not features:
            raise ValueError("No numeric features available")

        numeric_data = data[features].fillna(0)
        scaler = StandardScaler()
        X = scaler.fit_transform(numeric_data)
        y = data[target_attribute]

        try:
            model = LogisticRegression(max_iter=100)
            model.fit(X, y)
            predictions = model.predict_proba(X)[:, 1]
        except:
            return {"error": "Could not fit model for threshold optimization"}

        thresholds = np.arange(0.3, 0.7, 0.05)
        best_threshold = 0.5
        best_fairness = 0
        best_accuracy = 0

        for thresh in thresholds:
            preds = (predictions >= thresh).astype(int)

            fairness_scores = []
            for prot_attr in protected_attributes:
                if prot_attr in data.columns:
                    groups = data[prot_attr].unique()
                    rates = []
                    for group in groups:
                        mask = data[prot_attr] == group
                        if mask.sum() > 0:
                            rate = preds[mask].mean()
                            rates.append(rate)

                    if len(rates) >= 2:
                        diff = abs(max(rates) - min(rates))
                        fairness_scores.append(diff)

            if fairness_scores:
                fairness = 1.0 - min(fairness_scores)
                accuracy = (preds == y).mean()

                if fairness > best_fairness and accuracy >= (y.mean() - accuracy_cost):
                    best_fairness = fairness
                    best_accuracy = accuracy
                    best_threshold = thresh

        return {
            "mitigation_type": "threshold_optimization",
            "method": "Threshold Optimization",
            "description": f"Adjusted decision threshold to {best_threshold:.2f} for fairer outcomes",
            "optimal_threshold": best_threshold,
            "estimated_accuracy": best_accuracy,
            "estimated_fairness": best_fairness,
            "accuracy_cost": 1.0 - best_accuracy,
        }

    def _correlation_remover(
        self, data: pd.DataFrame, protected_attributes: List[str], target_attribute: str
    ) -> Dict[str, Any]:
        if not protected_attributes:
            return {"error": "No protected attributes specified"}

        prot_attr = protected_attributes[0]
        if prot_attr not in data.columns:
            raise ValueError(f"Protected attribute {prot_attr} not found")

        features = [c for c in data.columns if c not in protected_attributes + [target_attribute]]
        features = [f for f in features if data[f].dtype in [np.int64, np.float64]]

        if not features:
            raise ValueError("No numeric features available")

        numeric_data = data[features].fillna(0)
        prot_codes = pd.Categorical(data[prot_attr]).codes

        correlations_before = {}
        for feat in features:
            corr = np.corrcoef(numeric_data[feat], prot_codes)[0, 1]
            if not np.isnan(corr):
                correlations_before[feat] = abs(corr)

        X = numeric_data.values
        model = LogisticRegression(max_iter=100)
        model.fit(X, prot_codes)

        residuals = np.zeros_like(X)
        for i in range(X.shape[1]):
            model_feat = LogisticRegression(max_iter=100)
            model_feat.fit(X[:, i].reshape(-1, 1), prot_codes)
            predicted = model_feat.predict_proba(X[:, i].reshape(-1, 1))[:, 1]
            residuals[:, i] = X[:, i] - predicted * X[:, i].std() - X[:, i].mean()

        correlations_after = {}
        for i, feat in enumerate(features):
            corr = np.corrcoef(residuals[:, i], prot_codes)[0, 1]
            if not np.isnan(corr):
                correlations_after[feat] = abs(corr)

        return {
            "mitigation_type": "correlation_remover",
            "method": "Correlation Remover",
            "description": "Removed correlation between features and protected attributes",
            "correlations_before": correlations_before,
            "correlations_after": correlations_after,
            "avg_correlation_reduction": np.mean(list(correlations_before.values())) - np.mean(list(correlations_after.values())),
        }

    def get_tradeoff_curve(
        self,
        data: pd.DataFrame,
        protected_attributes: List[str],
        target_attribute: str,
    ) -> List[Dict[str, float]]:
        if target_attribute not in data.columns:
            return []

        features = [c for c in data.columns if c not in protected_attributes + [target_attribute]]
        features = [f for f in features if data[f].dtype in [np.int64, np.float64]]

        if not features:
            return []

        numeric_data = data[features].fillna(0)
        scaler = StandardScaler()
        X = scaler.fit_transform(numeric_data)
        y = data[target_attribute]

        try:
            model = LogisticRegression(max_iter=100)
            model.fit(X, y)
            predictions = model.predict_proba(X)[:, 1]
        except:
            return []

        curve = []
        thresholds = np.arange(0.1, 0.9, 0.1)

        for thresh in thresholds:
            preds = (predictions >= thresh).astype(int)
            accuracy = (preds == y).mean()

            fairness_scores = []
            for prot_attr in protected_attributes:
                if prot_attr in data.columns:
                    groups = data[prot_attr].unique()
                    rates = []
                    for group in groups:
                        mask = data[prot_attr] == group
                        if mask.sum() > 0:
                            rate = preds[mask].mean()
                            rates.append(rate)

                    if len(rates) >= 2:
                        diff = abs(max(rates) - min(rates))
                        fairness_scores.append(1.0 - diff)

            fairness = np.mean(fairness_scores) if fairness_scores else 1.0

            curve.append({"threshold": thresh, "accuracy": accuracy, "fairness": fairness})

        return curve


mitigation_service = MitigationService()