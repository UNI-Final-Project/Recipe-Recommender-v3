"""
MLOps Module
Sistema completo de MLOps para Recipe Recommender
"""

from mlops.config import config, MODEL_VERSIONS, METRICS_NAMES
from mlops.logging_config import (
    setup_logging,
    get_logger,
    app_logger,
    mlops_logger,
    model_logger,
    monitoring_logger,
    retraining_logger,
)
from mlops.model_registry import ModelRegistry, ModelMetadata, model_registry
from mlops.evaluation import (
    ModelEvaluator,
    ModelValidator,
    EvaluationReport,
)
from mlops.monitoring import (
    MetricsCollector,
    AnomalyDetector,
    HealthMonitor,
    metrics_collector,
    anomaly_detector,
    health_monitor,
)
from mlops.retraining import (
    RetrainingConfig,
    RetrainingJob,
    RetrainingOrchestrator,
    AutomaticRetrainingScheduler,
    retrain_config,
    retraining_orchestrator,
    auto_scheduler,
)

__all__ = [
    # Config
    "config",
    "MODEL_VERSIONS",
    "METRICS_NAMES",
    # Logging
    "setup_logging",
    "get_logger",
    "app_logger",
    "mlops_logger",
    "model_logger",
    "monitoring_logger",
    "retraining_logger",
    # Model Registry
    "ModelRegistry",
    "ModelMetadata",
    "model_registry",
    # Evaluation
    "ModelEvaluator",
    "ModelValidator",
    "EvaluationReport",
    # Monitoring
    "MetricsCollector",
    "AnomalyDetector",
    "HealthMonitor",
    "metrics_collector",
    "anomaly_detector",
    "health_monitor",
    # Retraining
    "RetrainingConfig",
    "RetrainingJob",
    "RetrainingOrchestrator",
    "AutomaticRetrainingScheduler",
    "retrain_config",
    "retraining_orchestrator",
    "auto_scheduler",
]
