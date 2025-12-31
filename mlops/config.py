"""
MLOps Configuration Module
Centraliza todas las configuraciones para el sistema de MLOps
"""
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MLOPS_ROOT = PROJECT_ROOT / "mlops"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"
METRICS_DIR = MLOPS_ROOT / "metrics"
ARTIFACTS_DIR = MLOPS_ROOT / "artifacts"

# Crear directorios si no existen
for dir_path in [MODELS_DIR, LOGS_DIR, METRICS_DIR, ARTIFACTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

@dataclass
class MLOpsConfig:
    """Configuración central para MLOps"""
    
    # MLflow
    mlflow_tracking_uri: str = os.getenv("MLFLOW_TRACKING_URI", str(PROJECT_ROOT / "mlruns"))
    mlflow_experiment_name: str = os.getenv("MLFLOW_EXPERIMENT_NAME", "recipe-recommendations")
    mlflow_registry_uri: str = os.getenv("MLFLOW_REGISTRY_URI", str(PROJECT_ROOT / "mlruns"))
    
    # Modelos
    models_dir: Path = MODELS_DIR
    model_registry_path: Path = MODELS_DIR / "registry.json"
    
    # Monitoreo
    monitoring_enabled: bool = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
    alert_threshold_latency: float = float(os.getenv("ALERT_THRESHOLD_LATENCY", "5000"))  # ms
    alert_threshold_accuracy_drop: float = float(os.getenv("ALERT_THRESHOLD_ACCURACY_DROP", "0.05"))  # 5%
    
    # Retraining
    retrain_enabled: bool = os.getenv("RETRAIN_ENABLED", "true").lower() == "true"
    retrain_interval_days: int = int(os.getenv("RETRAIN_INTERVAL_DAYS", "7"))
    retrain_data_threshold: int = int(os.getenv("RETRAIN_DATA_THRESHOLD", "100"))  # Muestras mínimas
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logs_dir: Path = LOGS_DIR
    max_log_size_mb: int = int(os.getenv("MAX_LOG_SIZE_MB", "50"))
    backup_count: int = int(os.getenv("BACKUP_COUNT", "5"))
    
    # Evaluación
    evaluation_test_size: float = 0.2
    evaluation_cv_folds: int = 5
    
    # Métricas y artefactos
    metrics_dir: Path = METRICS_DIR
    artifacts_dir: Path = ARTIFACTS_DIR
    
    # Data Validation
    data_validation_enabled: bool = True
    schema_file: Optional[Path] = PROJECT_ROOT / "mlops" / "data_schema.json"
    
    def __post_init__(self):
        """Inicializar directorios después de cargar configuración"""
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

# Instancia global de configuración
config = MLOpsConfig()

# Configuración de nombres de métrica
METRICS_NAMES = {
    "api_latency_ms": "API Latency (ms)",
    "translation_latency_ms": "Translation Latency (ms)",
    "embedding_latency_ms": "Embedding Latency (ms)",
    "num_recipes": "Number of Recipes Returned",
    "semantic_score_mean": "Mean Semantic Score",
    "popularity_score_mean": "Mean Popularity Score",
    "hybrid_score_mean": "Mean Hybrid Score",
    "request_count": "Request Count",
    "error_rate": "Error Rate (%)",
    "model_accuracy": "Model Accuracy",
    "model_precision": "Model Precision",
    "model_recall": "Model Recall",
    "model_f1": "Model F1 Score",
}

# Versiones de modelos relevantes
MODEL_VERSIONS = {
    "embedding_model": "text-embedding-3-small",
    "llm_model": "gpt-4.1-2025-04-14",
    "qdrant_collection": "recipes_embeddings_cloud",
}
