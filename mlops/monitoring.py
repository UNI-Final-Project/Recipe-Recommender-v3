"""
Monitoring Module
Monitoreo en tiempo real del sistema y detección de anomalías
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import deque
import json
import mlflow

from mlops.config import config
from mlops.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class MetricPoint:
    """Punto de datos de una métrica"""
    timestamp: str
    value: float
    labels: Dict[str, str] = None

class MetricsCollector:
    """Recolector de métricas en tiempo real"""
    
    def __init__(self, max_points: int = 10000):
        self.metrics: Dict[str, deque] = {}
        self.max_points = max_points
        self.metrics_file = config.metrics_dir / "metrics.jsonl"
    
    def record(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """
        Registra una métrica
        
        Args:
            metric_name: Nombre de la métrica
            value: Valor de la métrica
            labels: Etiquetas adicionales
        """
        if metric_name not in self.metrics:
            self.metrics[metric_name] = deque(maxlen=self.max_points)
        
        point = MetricPoint(
            timestamp=datetime.utcnow().isoformat(),
            value=value,
            labels=labels or {}
        )
        
        self.metrics[metric_name].append(point)
        
        # Persistir en archivo
        self._persist_metric(metric_name, point)
    
    def _persist_metric(self, metric_name: str, point: MetricPoint):
        """Persiste métrica en archivo JSONL"""
        try:
            with open(self.metrics_file, 'a') as f:
                record = {
                    "metric": metric_name,
                    "timestamp": point.timestamp,
                    "value": point.value,
                    "labels": point.labels,
                }
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            logger.warning(f"Could not persist metric: {e}")
    
    def get_latest(self, metric_name: str, n: int = 1) -> List[MetricPoint]:
        """
        Obtiene los últimos n puntos de una métrica
        
        Args:
            metric_name: Nombre de la métrica
            n: Número de puntos
        
        Returns:
            Lista de puntos más recientes
        """
        if metric_name not in self.metrics:
            return []
        
        return list(self.metrics[metric_name])[-n:]
    
    def get_stats(self, metric_name: str, window_minutes: int = 60) -> Dict[str, float]:
        """
        Obtiene estadísticas de una métrica en una ventana de tiempo
        
        Args:
            metric_name: Nombre de la métrica
            window_minutes: Ventana de tiempo en minutos
        
        Returns:
            Diccionario con estadísticas
        """
        if metric_name not in self.metrics:
            return {}
        
        cutoff_time = (datetime.utcnow() - timedelta(minutes=window_minutes)).isoformat()
        points = [
            p.value for p in self.metrics[metric_name]
            if p.timestamp >= cutoff_time
        ]
        
        if not points:
            return {}
        
        return {
            "count": len(points),
            "mean": float(np.mean(points)),
            "std": float(np.std(points)),
            "min": float(np.min(points)),
            "max": float(np.max(points)),
            "p50": float(np.percentile(points, 50)),
            "p95": float(np.percentile(points, 95)),
            "p99": float(np.percentile(points, 99)),
        }

class AnomalyDetector:
    """Detector de anomalías basado en Z-score"""
    
    @staticmethod
    def detect_anomalies(
        values: np.ndarray,
        threshold: float = 3.0
    ) -> Dict[str, Any]:
        """
        Detecta anomalías usando Z-score
        
        Args:
            values: Array de valores
            threshold: Umbral de Z-score
        
        Returns:
            Diccionario con información de anomalías
        """
        if len(values) < 2:
            return {"anomalies": [], "anomaly_indices": []}
        
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            return {"anomalies": [], "anomaly_indices": []}
        
        z_scores = np.abs((values - mean) / std)
        anomaly_mask = z_scores > threshold
        anomaly_indices = np.where(anomaly_mask)[0].tolist()
        
        anomalies = [
            {
                "index": int(idx),
                "value": float(values[idx]),
                "z_score": float(z_scores[idx]),
            }
            for idx in anomaly_indices
        ]
        
        logger.info(f"Anomalies detected: {len(anomalies)} out of {len(values)}")
        
        return {
            "anomalies": anomalies,
            "anomaly_indices": anomaly_indices,
            "anomaly_count": len(anomalies),
            "anomaly_rate": float(len(anomalies) / len(values)),
        }
    
    @staticmethod
    def detect_performance_degradation(
        metrics: List[float],
        window_size: int = 10,
        threshold: float = 0.1
    ) -> bool:
        """
        Detecta degradación de rendimiento
        
        Args:
            metrics: Lista de métricas de rendimiento
            window_size: Tamaño de ventana para comparación
            threshold: Umbral de degradación (%)
        
        Returns:
            True si se detecta degradación
        """
        if len(metrics) < window_size * 2:
            return False
        
        recent_window = np.mean(metrics[-window_size:])
        historical_window = np.mean(metrics[-window_size*2:-window_size])
        
        if historical_window == 0:
            return False
        
        degradation = (historical_window - recent_window) / historical_window
        
        if degradation > threshold:
            logger.warning(f"Performance degradation detected: {degradation:.2%}")
            return True
        
        return False

class HealthMonitor:
    """Monitor de salud del sistema"""
    
    def __init__(self):
        self.status = "healthy"
        self.last_check = None
        self.issues: List[str] = []
        self.metrics_collector = MetricsCollector()
    
    def check_api_health(self) -> Dict[str, Any]:
        """
        Verifica salud de la API
        
        Returns:
            Estado de salud
        """
        latency_stats = self.metrics_collector.get_stats("api_latency_ms", window_minutes=60)
        error_rate = self._calculate_error_rate()
        
        health = {
            "api_status": "healthy" if error_rate < 0.05 else "degraded",
            "latency_stats": latency_stats,
            "error_rate": error_rate,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Alertas
        if latency_stats.get("mean", 0) > config.alert_threshold_latency:
            health["alerts"] = ["High latency detected"]
        
        return health
    
    def check_model_health(self, model_metrics: Dict[str, float]) -> Dict[str, Any]:
        """
        Verifica salud del modelo
        
        Args:
            model_metrics: Métricas del modelo
        
        Returns:
            Estado de salud del modelo
        """
        health = {
            "model_status": "healthy",
            "metrics": model_metrics,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Verificar si hay degradación de accuracy
        if "accuracy" in model_metrics:
            if model_metrics["accuracy"] < 0.7:
                health["model_status"] = "degraded"
                health["alerts"] = ["Low accuracy detected"]
        
        return health
    
    def _calculate_error_rate(self) -> float:
        """Calcula la tasa de error de la última hora"""
        stats = self.metrics_collector.get_stats("error_rate", window_minutes=60)
        return stats.get("mean", 0) if stats else 0
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Obtiene estado general del sistema
        
        Returns:
            Estado del sistema
        """
        self.last_check = datetime.utcnow()
        
        status = {
            "timestamp": self.last_check.isoformat(),
            "overall_status": self.status,
            "api": self.check_api_health(),
            "checks": {
                "api_latency": self._check_latency(),
                "error_rate": self._check_error_rate(),
            }
        }
        
        return status
    
    def _check_latency(self) -> bool:
        """Verifica latencia"""
        stats = self.metrics_collector.get_stats("api_latency_ms")
        mean_latency = stats.get("mean", 0)
        return mean_latency <= config.alert_threshold_latency
    
    def _check_error_rate(self) -> bool:
        """Verifica tasa de error"""
        error_rate = self._calculate_error_rate()
        return error_rate < 0.05

# Instancia global
metrics_collector = MetricsCollector()
anomaly_detector = AnomalyDetector()
health_monitor = HealthMonitor()
