"""
Anomaly detection for identifying outliers and unusual patterns in FMCG data.
"""
from typing import Dict, List, Tuple, Optional
from statistics import mean, stdev, StatisticsError
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class AnomalyAlert:
    """Represents a detected anomaly."""
    metric_name: str
    entity: str  # Product, region, store, etc.
    expected_value: float
    actual_value: float
    z_score: float  # Standard deviations from mean
    anomaly_type: str  # "spike", "drop", "outlier"
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    message: str
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    def to_dict(self):
        return {
            "metric_name": self.metric_name,
            "entity": self.entity,
            "expected_value": self.expected_value,
            "actual_value": self.actual_value,
            "z_score": self.z_score,
            "anomaly_type": self.anomaly_type,
            "severity": self.severity,
            "message": self.message,
            "timestamp": self.timestamp.isoformat()
        }


class AnomalyDetector:
    """Detect statistical anomalies in data."""

    def __init__(self, z_score_threshold: float = 2.5):
        """
        Initialize anomaly detector.

        Args:
            z_score_threshold: Z-score threshold for anomaly (default 2.5 = 99th percentile)
        """
        self.z_score_threshold = z_score_threshold
        self.spike_threshold = 1.5  # 50% increase = spike
        self.drop_threshold = 0.5  # 50% decrease = drop

    def detect_anomalies(
        self,
        data: List[Dict],
        metric_field: str,
        groupby_field: str = None,
        time_series_data: Optional[List[Dict]] = None
    ) -> List[AnomalyAlert]:
        """
        Detect anomalies in numeric data.

        Args:
            data: List of data points
            metric_field: Field name to analyze for anomalies
            groupby_field: Optional field to group by for context
            time_series_data: Optional time series data for trend analysis

        Returns:
            List of detected anomalies
        """
        if not data or metric_field not in data[0]:
            return []

        anomalies = []

        # Extract numeric values
        try:
            values = [float(row.get(metric_field, 0)) for row in data]
            values = [v for v in values if v is not None]  # Remove None values
        except (ValueError, TypeError):
            logger.warning(f"Could not extract numeric values from {metric_field}")
            return []

        if len(values) < 3:
            return []  # Need at least 3 points for stats

        # Calculate statistics
        try:
            data_mean = mean(values)
            data_stdev = stdev(values) if len(values) > 1 else 0
        except StatisticsError:
            return []

        # Z-score based anomaly detection
        if data_stdev > 0:
            for i, row in enumerate(data):
                value = float(row.get(metric_field, 0))
                z_score = abs((value - data_mean) / data_stdev)

                if z_score > self.z_score_threshold:
                    entity = row.get(groupby_field, f"Item {i}") if groupby_field else f"Item {i}"

                    # Determine anomaly type
                    if value > data_mean:
                        anomaly_type = "spike"
                        severity = "HIGH" if z_score > 3.5 else "MEDIUM"
                    else:
                        anomaly_type = "drop"
                        severity = "HIGH" if z_score > 3.5 else "MEDIUM"

                    anomalies.append(
                        AnomalyAlert(
                            metric_name=metric_field,
                            entity=entity,
                            expected_value=data_mean,
                            actual_value=value,
                            z_score=z_score,
                            anomaly_type=anomaly_type,
                            severity=severity,
                            message=f"{entity}: {metric_field} anomaly detected ({anomaly_type}). Expected ~{data_mean:.1f}, got {value:.1f}"
                        )
                    )

        return sorted(anomalies, key=lambda x: x.z_score, reverse=True)

    def detect_trends(
        self,
        time_series: List[Dict],
        metric_field: str,
        entity_field: str,
        time_field: str = "timestamp"
    ) -> Dict[str, Dict]:
        """
        Detect trends in time series data.

        Args:
            time_series: Time series data points
            metric_field: Metric to analyze
            entity_field: Field identifying entities (product, region, etc.)
            time_field: Timestamp field name

        Returns:
            Dictionary of trend information by entity
        """
        trends = {}

        if not time_series:
            return trends

        # Group by entity
        grouped = {}
        for row in time_series:
            entity = row.get(entity_field, "Unknown")
            if entity not in grouped:
                grouped[entity] = []
            grouped[entity].append(row)

        # Analyze each entity
        for entity, entity_data in grouped.items():
            if len(entity_data) < 2:
                continue

            # Extract metric values
            try:
                values = [float(row.get(metric_field, 0)) for row in entity_data]
                values = [v for v in values if v is not None]
            except (ValueError, TypeError):
                continue

            if len(values) < 2:
                continue

            # Simple trend: compare first half vs second half
            mid = len(values) // 2
            first_half_avg = mean(values[:mid]) if mid > 0 else values[0]
            second_half_avg = mean(values[mid:]) if mid < len(values) else values[-1]

            change_pct = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg != 0 else 0

            trend = "UP" if change_pct > 5 else "DOWN" if change_pct < -5 else "STABLE"
            severity = "HIGH" if abs(change_pct) > 30 else "MEDIUM" if abs(change_pct) > 15 else "LOW"

            trends[entity] = {
                "trend": trend,
                "change_pct": change_pct,
                "severity": severity,
                "current_avg": second_half_avg,
                "previous_avg": first_half_avg,
                "data_points": len(values)
            }

        return trends

    def detect_correlations(
        self,
        data: List[Dict],
        metric1_field: str,
        metric2_field: str
    ) -> Dict:
        """
        Detect correlation between two metrics.

        Args:
            data: Data points
            metric1_field: First metric field
            metric2_field: Second metric field

        Returns:
            Correlation analysis
        """
        try:
            # Extract both metrics
            pairs = []
            for row in data:
                try:
                    m1 = float(row.get(metric1_field, 0))
                    m2 = float(row.get(metric2_field, 0))
                    pairs.append((m1, m2))
                except (ValueError, TypeError):
                    continue

            if len(pairs) < 3:
                return {"error": "Insufficient data points"}

            # Calculate correlation coefficient
            m1_values = [p[0] for p in pairs]
            m2_values = [p[1] for p in pairs]

            m1_mean = mean(m1_values)
            m2_mean = mean(m2_values)
            m1_stdev = stdev(m1_values) if len(m1_values) > 1 else 0
            m2_stdev = stdev(m2_values) if len(m2_values) > 1 else 0

            if m1_stdev == 0 or m2_stdev == 0:
                correlation = 0
            else:
                covariance = sum((m1_values[i] - m1_mean) * (m2_values[i] - m2_mean) for i in range(len(pairs))) / len(pairs)
                correlation = covariance / (m1_stdev * m2_stdev)

            # Interpret correlation
            if abs(correlation) > 0.7:
                strength = "Strong"
                direction = "positive" if correlation > 0 else "negative"
            elif abs(correlation) > 0.4:
                strength = "Moderate"
                direction = "positive" if correlation > 0 else "negative"
            else:
                strength = "Weak"
                direction = "positive" if correlation > 0 else "negative"

            return {
                "correlation_coefficient": round(correlation, 3),
                "strength": strength,
                "direction": direction,
                "interpretation": f"{strength} {direction} correlation between {metric1_field} and {metric2_field}",
                "significance": "Likely significant" if abs(correlation) > 0.6 else "May be due to chance"
            }

        except Exception as e:
            logger.error(f"Correlation analysis error: {str(e)}")
            return {"error": str(e)}

    def detect_segments(
        self,
        data: List[Dict],
        metric_field: str,
        threshold_percentile: float = 0.75
    ) -> Dict:
        """
        Segment data into high/medium/low performers.

        Args:
            data: Data points
            metric_field: Metric to segment by
            threshold_percentile: Percentile for segmentation (default 75th)

        Returns:
            Segmentation analysis
        """
        try:
            values = [float(row.get(metric_field, 0)) for row in data]
            values = [v for v in values if v is not None]

            if len(values) < 3:
                return {"error": "Insufficient data"}

            values.sort()

            # Calculate percentiles
            high_threshold = values[int(len(values) * threshold_percentile)]
            low_threshold = values[int(len(values) * (1 - threshold_percentile))]

            segments = {"high": [], "medium": [], "low": []}

            for row in data:
                value = float(row.get(metric_field, 0))
                if value >= high_threshold:
                    segments["high"].append(row)
                elif value <= low_threshold:
                    segments["low"].append(row)
                else:
                    segments["medium"].append(row)

            high_avg = mean([float(r.get(metric_field, 0)) for r in segments["high"]]) if segments["high"] else 0
            medium_avg = mean([float(r.get(metric_field, 0)) for r in segments["medium"]]) if segments["medium"] else 0
            low_avg = mean([float(r.get(metric_field, 0)) for r in segments["low"]]) if segments["low"] else 0

            return {
                "high_performers": len(segments["high"]),
                "medium_performers": len(segments["medium"]),
                "low_performers": len(segments["low"]),
                "high_avg": high_avg,
                "medium_avg": medium_avg,
                "low_avg": low_avg,
                "gap_high_to_low": high_avg - low_avg if low_avg > 0 else 0
            }

        except Exception as e:
            logger.error(f"Segmentation error: {str(e)}")
            return {"error": str(e)}
