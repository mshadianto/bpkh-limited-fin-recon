"""ML-based anomaly detection for reconciliation data."""

import pandas as pd
import numpy as np
from typing import List, Dict, Any


class MLAnomalyDetector:
    """Anomaly detection using IsolationForest and Z-score."""

    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination

    def detect_zscore_anomalies(
        self,
        coa_recon: pd.DataFrame,
        threshold: float = 2.5
    ) -> List[Dict[str, Any]]:
        """Detect anomalies using Z-score on variance columns."""
        columns = ['Net_Variance', 'Debit_Variance', 'Credit_Variance']
        anomalies = []

        for col in columns:
            if col not in coa_recon.columns:
                continue
            values = coa_recon[col].dropna()
            if len(values) < 3:
                continue
            mean_val = values.mean()
            std_val = values.std()
            if std_val == 0:
                continue

            z_scores = (values - mean_val) / std_val
            outlier_mask = z_scores.abs() > threshold

            for idx in coa_recon.index[outlier_mask.reindex(coa_recon.index, fill_value=False)]:
                row = coa_recon.loc[idx]
                z = float(z_scores.get(idx, 0))
                anomalies.append({
                    "severity": "HIGH" if abs(z) > 3.5 else "MEDIUM",
                    "type": f"Z-Score Outlier ({col})",
                    "coa": int(row['COA']) if pd.notna(row.get('COA')) else "N/A",
                    "description": (
                        f"COA {int(row['COA']) if pd.notna(row.get('COA')) else 'N/A'}: "
                        f"{col} = SAR {row[col]:,.2f} (z-score: {z:.2f})"
                    ),
                    "amount": float(row[col]),
                    "z_score": z,
                    "method": "z_score"
                })
        return anomalies

    def detect_isolation_forest_anomalies(
        self,
        coa_recon: pd.DataFrame
    ) -> List[Dict[str, Any]]:
        """Detect anomalies using Isolation Forest on multi-dimensional features."""
        from sklearn.ensemble import IsolationForest
        from sklearn.preprocessing import StandardScaler

        feature_cols = [
            'Net_Variance', 'Debit_Variance', 'Credit_Variance',
            'Manual_TxnCount', 'Daftra_TxnCount', 'Abs_Variance'
        ]
        available = [c for c in feature_cols if c in coa_recon.columns]
        if len(available) < 2 or len(coa_recon) < 5:
            return []

        df_features = coa_recon[available].fillna(0).copy()

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df_features)

        model = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=100
        )
        predictions = model.fit_predict(X_scaled)
        scores = model.decision_function(X_scaled)

        anomalies = []
        for i, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:
                row = coa_recon.iloc[i]
                anomalies.append({
                    "severity": "HIGH" if score < -0.3 else "MEDIUM",
                    "type": "Isolation Forest Anomaly",
                    "coa": int(row['COA']) if pd.notna(row.get('COA')) else "N/A",
                    "description": (
                        f"COA {int(row['COA']) if pd.notna(row.get('COA')) else 'N/A'}: "
                        f"Multi-dimensional outlier (score: {score:.3f}). "
                        f"Net Var: SAR {row.get('Net_Variance', 0):,.2f}, "
                        f"Txn Manual/Daftra: {int(row.get('Manual_TxnCount', 0))}/{int(row.get('Daftra_TxnCount', 0))}"
                    ),
                    "amount": float(row.get('Net_Variance', 0)),
                    "anomaly_score": float(score),
                    "method": "isolation_forest"
                })

        anomalies.sort(key=lambda x: x.get('anomaly_score', 0))
        return anomalies

    def detect_all(self, coa_recon: pd.DataFrame) -> List[Dict[str, Any]]:
        """Run all ML anomaly detection methods and merge results."""
        z_anomalies = self.detect_zscore_anomalies(coa_recon)
        if_anomalies = self.detect_isolation_forest_anomalies(coa_recon)

        all_anomalies = z_anomalies + if_anomalies

        # Deduplicate: keep highest severity per (COA, method)
        seen = {}
        severity_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        for a in all_anomalies:
            key = (a['coa'], a['method'])
            if key not in seen or severity_rank.get(a['severity'], 3) < severity_rank.get(seen[key]['severity'], 3):
                seen[key] = a

        result = sorted(seen.values(), key=lambda x: severity_rank.get(x['severity'], 3))
        return result[:15]
