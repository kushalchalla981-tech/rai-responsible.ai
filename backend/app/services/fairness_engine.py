import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Literal, List
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
import warnings

from app.models.schemas import AuditMode, MetricResponse

AuditModeType = Literal["direct", "proxy", "limited"]


class FairnessEngine:
    def __init__(self):
        self.min_samples = 100

    def run_audit(
        self,
        data: pd.DataFrame,
        protected_attrs: List[str],
        mode: AuditModeType,
        target_attr: str,
        confidence: float = 0.9,
    ) -> Dict[str, MetricResponse]:
        print(f"Starting audit with {len(data)} samples")
        print(f"Mode: {mode}, Target: {target_attr}, Protected: {protected_attrs}")

        if len(data) < self.min_samples:
            raise ValueError(f"Insufficient dataset size. Need at least {self.min_samples} samples, got {len(data)}.")

        if target_attr not in data.columns:
            raise ValueError(f"Target attribute '{target_attr}' not found in dataset columns: {list(data.columns)}")

        results = {}

        try:
            if mode == "direct":
                results = self._direct_audit(data, protected_attrs, target_attr)
            elif mode == "proxy":
                results = self._proxy_audit(data, protected_attrs, target_attr)
            elif mode == "limited":
                results = self._limited_audit(data, protected_attrs, target_attr)
        except Exception as e:
            print(f"Error during audit: {e}")
            import traceback
            traceback.print_exc()
            raise ValueError(f"Audit failed: {str(e)}")

        if not results:
            raise ValueError("No metrics could be calculated. Please check your configuration and ensure protected attributes have at least 2 groups.")

        print(f"Audit completed successfully with {len(results)} metrics")
        return results

    def _direct_audit(
        self, data: pd.DataFrame, protected_attrs: List[str], target_attr: str
    ) -> Dict[str, MetricResponse]:
        results = {}

        print(f"Running direct audit with protected_attrs: {protected_attrs}, target_attr: {target_attr}")

        # Validate target attribute exists
        if target_attr not in data.columns:
            raise ValueError(f"Target attribute '{target_attr}' not found in dataset columns: {list(data.columns)}")

        # Analyze target attribute type
        target_values = pd.to_numeric(data[target_attr], errors='coerce')
        target_is_numeric = not target_values.isna().all()
        target_unique_values = data[target_attr].dropna().unique()
        target_is_binary = target_is_numeric and len(target_unique_values) == 2 and set(target_unique_values).issubset({0, 1})

        print(f"Target analysis: is_numeric={target_is_numeric}, is_binary={target_is_binary}, unique_values={len(target_unique_values)}")

        for prot_attr in protected_attrs:
            if prot_attr not in data.columns:
                print(f"Protected attribute {prot_attr} not in data columns")
                continue

            print(f"Processing protected attribute: {prot_attr}")

            # Get unique groups for protected attribute
            groups = data[prot_attr].unique()
            print(f"Groups found: {groups}")

            # Skip if not enough groups
            if len(groups) < 2:
                print(f"Skipping {prot_attr}: only {len(groups)} group(s) found")
                continue

            # Limit number of groups to prevent performance issues
            if len(groups) > 20:
                print(f"Warning: {prot_attr} has {len(groups)} unique values, limiting to top 20")
                # Get top 20 most frequent groups
                top_groups = data[prot_attr].value_counts().head(20).index.tolist()
                data_filtered = data[data[prot_attr].isin(top_groups)]
                groups = top_groups
            else:
                data_filtered = data

            group_stats = []
            selection_rates = {}

            for group in groups:
                group_data = data_filtered[data_filtered[prot_attr] == group]
                print(f"Group {group}: {len(group_data)} samples")

                try:
                    if target_is_numeric:
                        # For numeric targets, calculate mean
                        group_target_values = pd.to_numeric(group_data[target_attr], errors='coerce')
                        
                        if group_target_values.isna().all():
                            print(f"Warning: Target attribute {target_attr} could not be converted to numeric for group {group}")
                            continue

                        rate = group_target_values.mean()
                        selection_rates[group] = rate
                        print(f"Selection rate for group {group}: {rate}")
                    else:
                        # For categorical targets, calculate positive rate (most frequent value)
                        group_target_values = group_data[target_attr].dropna()
                        
                        if len(group_target_values) == 0:
                            print(f"Warning: No valid target values for group {group}")
                            continue

                        # Get the most frequent value as "positive"
                        most_frequent = group_target_values.mode()[0] if len(group_target_values.mode()) > 0 else group_target_values.iloc[0]
                        rate = (group_target_values == most_frequent).mean()
                        selection_rates[group] = rate
                        print(f"Selection rate for group {group}: {rate} (positive class: {most_frequent})")
                except Exception as e:
                    print(f"Error calculating rate for group {group}: {e}")
                    continue

            rates = list(selection_rates.values())
            print(f"Selection rates: {rates}")

            if len(rates) >= 2:
                max_diff = max(rates) - min(rates)
                is_safe = max_diff <= 0.1

                for group, rate in selection_rates.items():
                    group_stats.append({"group": str(group), "rate": rate})

                results[f"demographic_parity_{prot_attr}"] = MetricResponse(
                    metric_name="Demographic Parity Difference",
                    score=max_diff,
                    threshold=0.1,
                    is_safe=is_safe,
                    subgroup_breakdown=group_stats,
                )
                print(f"Added demographic_parity_{prot_attr}: score={max_diff}, is_safe={is_safe}")

            # Calculate equal opportunity only if target is binary (0/1)
            try:
                if target_is_binary:
                    print(f"Calculating equal opportunity for binary target {target_attr}")
                    tprs = {}
                    for group in groups:
                        group_data = data_filtered[data_filtered[prot_attr] == group]
                        group_target_values = pd.to_numeric(group_data[target_attr], errors='coerce')

                        # Count positive cases (where target == 1)
                        positive_mask = group_target_values == 1
                        positive_count = positive_mask.sum()
                        total_count = len(group_target_values.dropna())

                        if positive_count > 0 and total_count > 0:
                            # True positive rate = positives / total
                            tprs[group] = positive_count / total_count
                        else:
                            tprs[group] = 0.0

                    tpr_values = list(tprs.values())
                    if len(tpr_values) >= 2:
                        tpr_diff = max(tpr_values) - min(tpr_values)
                        results[f"equal_opportunity_{prot_attr}"] = MetricResponse(
                            metric_name="Equal Opportunity",
                            score=tpr_diff,
                            threshold=0.1,
                            is_safe=tpr_diff <= 0.1,
                            subgroup_breakdown=[{"group": str(k), "tpr": v} for k, v in tprs.items()],
                        )
                        print(f"Added equal_opportunity_{prot_attr}: score={tpr_diff}, is_safe={tpr_diff <= 0.1}")
                    else:
                        print(f"Skipping equal opportunity: not enough groups with valid data")
                else:
                    print(f"Skipping equal opportunity: target {target_attr} is not binary (is_numeric={target_is_numeric}, unique_values={len(target_unique_values)})")
            except Exception as e:
                print(f"Error calculating equal opportunity for {prot_attr}: {e}")
                import traceback
                traceback.print_exc()

        print(f"Direct audit completed. Results: {list(results.keys())}")
        return results

    def _proxy_audit(
        self, data: pd.DataFrame, protected_attrs: List[str], target_attr: str
    ) -> Dict[str, MetricResponse]:
        results = {}

        if not protected_attrs:
            return results

        prot_attr = protected_attrs[0]
        if prot_attr not in data.columns:
            return results

        non_protected = [c for c in data.columns if c not in protected_attrs and c != target_attr]

        # Convert protected attribute to numeric for correlation calculation
        prot_data = data[prot_attr]
        if prot_data.dtype == object or str(prot_data.dtype) == 'str':
            try:
                prot_data = pd.Series(prot_data.astype('category').cat.codes, index=prot_data.index)
            except:
                return results

        correlations = {}
        for col in non_protected:
            feat_data = data[col]
            
            # Convert feature to numeric if it's categorical
            if feat_data.dtype == object or str(feat_data.dtype) == 'str':
                try:
                    feat_data = pd.Series(feat_data.astype('category').cat.codes, index=feat_data.index)
                except:
                    continue

            try:
                corr = feat_data.corr(prot_data)
                if not np.isnan(corr) and not np.isinf(corr):
                    correlations[col] = abs(corr)
            except:
                pass

        if correlations:
            max_proxy = max(correlations.items(), key=lambda x: x[1])
            is_safe = max_proxy[1] < 0.3
            proxy_risk = max_proxy[1]

            results["proxy_leakage"] = MetricResponse(
                metric_name="Proxy Correlation Risk",
                score=proxy_risk,
                threshold=0.3,
                is_safe=is_safe,
                subgroup_breakdown=[
                    {"feature": k, "correlation": v} for k, v in sorted(correlations.items(), key=lambda x: -x[1])[:5]
                ],
            )

        return results

    def _limited_audit(
        self, data: pd.DataFrame, protected_attrs: List[str], target_attr: str
    ) -> Dict[str, MetricResponse]:
        results = {}

        missing_info = {}
        for prot_attr in protected_attrs:
            if prot_attr in data.columns:
                missing_rate = data[prot_attr].isnull().sum() / len(data)
                missing_info[prot_attr] = missing_rate

        if missing_info:
            max_missing = max(missing_info.values())
            confidence = 1.0 - max_missing

            results["data_quality"] = MetricResponse(
                metric_name="Missing Data Confidence",
                score=confidence,
                threshold=0.9,
                is_safe=confidence >= 0.9,
                subgroup_breakdown=[{"attribute": k, "missing_rate": v} for k, v in missing_info.items()],
            )

        return results

    def detect_proxy_reconstruction(
        self, data: pd.DataFrame, protected_attrs: List[str]
    ) -> Dict[str, float]:
        proxies = {}

        for prot_attr in protected_attrs:
            if prot_attr not in data.columns:
                continue

            features = [c for c in data.columns if c not in protected_attrs]
            target = data[prot_attr]

            if target.dtype == object:
                try:
                    target = target.astype("category").cat.codes
                except:
                    continue

            for feat in features:
                if data[feat].dtype in [np.int64, np.float64]:
                    try:
                        model = LogisticRegression(max_iter=100)
                        X = data[[feat]].dropna()
                        y = target.loc[X.index]

                        if y.nunique() > 1 and len(X) > 50:
                            model.fit(X, y)
                            auc = roc_auc_score(y, model.predict_proba(X)[:, 1])
                            if auc > 0.5:
                                proxies[feat] = auc
                    except:
                        pass

        return proxies


engine = FairnessEngine()