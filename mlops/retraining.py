"""
Retraining Module
Gestiona el pipeline de retraining automático de modelos
"""
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict, field
import mlflow

from mlops.config import config
from mlops.logging_config import get_logger
from mlops.model_registry import ModelRegistry, ModelMetadata
from mlops.evaluation import ModelEvaluator, EvaluationReport

logger = get_logger(__name__)

@dataclass
class RetrainingConfig:
    """Configuración de retraining"""
    enabled: bool = config.retrain_enabled
    interval_days: int = config.retrain_interval_days
    min_samples: int = config.retrain_data_threshold
    test_size: float = 0.2
    cv_folds: int = 5
    performance_threshold: float = 0.05  # 5% de degradación
    auto_approve: bool = False  # Requerir aprobación antes de promover a producción

@dataclass
class RetrainingJob:
    """Representa un job de retraining"""
    job_id: str
    model_id: str
    status: str = "pending"  # pending, running, completed, failed
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    new_version: Optional[str] = None
    metrics: Dict[str, float] = field(default_factory=dict)
    data_size: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return asdict(self)

class RetrainingOrchestrator:
    """Orquestador de retraining"""
    
    def __init__(self, config: RetrainingConfig = None):
        self.config = config or RetrainingConfig()
        self.registry = ModelRegistry()
        self.jobs: Dict[str, RetrainingJob] = {}
        self.data_store = (Path(__file__).parent.parent / "mlruns") / "retraining_data"
        self.data_store.mkdir(parents=True, exist_ok=True)
    
    def check_retrain_needed(self, model_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Verifica si un modelo necesita retraining
        
        Args:
            model_id: ID del modelo
        
        Returns:
            Tupla (necesita_retrain, razones)
        """
        reasons = {}
        needs_retrain = False
        
        # Obtener modelo en producción
        prod_model = self.registry.get_production_model(model_id)
        if not prod_model:
            logger.warning(f"No production model found for {model_id}")
            return False, {"reason": "no_production_model"}
        
        # Verificar intervalo de tiempo
        if prod_model.get('deployment_date'):
            deployment_time = datetime.fromisoformat(prod_model['deployment_date'])
            days_deployed = (datetime.utcnow() - deployment_time).days
            
            if days_deployed >= self.config.interval_days:
                reasons["time_interval"] = f"Deployed {days_deployed} days ago"
                needs_retrain = True
                logger.info(f"Retrain needed for {model_id}: Time interval exceeded")
        
        # Verificar si hay datos nuevos suficientes
        new_data_count = self._get_new_data_count(model_id)
        if new_data_count >= self.config.min_samples:
            reasons["new_data"] = f"{new_data_count} new samples available"
            needs_retrain = True
            logger.info(f"Retrain needed for {model_id}: New data available")
        
        # Verificar degradación de rendimiento (si está disponible)
        if "metrics" in prod_model:
            reasons["performance"] = "Performance monitoring enabled"
        
        return needs_retrain, reasons
    
    def _get_new_data_count(self, model_id: str) -> int:
        """Obtiene el conteo de datos nuevos disponibles"""
        # En una aplicación real, esto consultaría una base de datos
        # Por ahora, retornamos un valor placeholder
        return 0
    
    def create_retrain_job(self, model_id: str) -> RetrainingJob:
        """
        Crea un nuevo job de retraining
        
        Args:
            model_id: ID del modelo
        
        Returns:
            Job de retraining creado
        """
        job_id = f"{model_id}_{datetime.utcnow().timestamp()}"
        
        job = RetrainingJob(
            job_id=job_id,
            model_id=model_id
        )
        
        self.jobs[job_id] = job
        logger.info(f"Retraining job created: {job_id}")
        
        return job
    
    def execute_retrain(
        self,
        job: RetrainingJob,
        training_data: pd.DataFrame,
        validation_data: pd.DataFrame = None
    ) -> bool:
        """
        Ejecuta el retraining
        
        Args:
            job: Job de retraining
            training_data: Datos de entrenamiento
            validation_data: Datos de validación (opcional)
        
        Returns:
            True si fue exitoso
        """
        job.status = "running"
        job.started_at = datetime.utcnow().isoformat()
        job.data_size = len(training_data)
        
        try:
            logger.info(f"Starting retraining for job {job.job_id}")
            
            # Iniciar run en MLflow
            with mlflow.start_run(run_name=f"retrain_{job.job_id}"):
                # Log configuración
                mlflow.log_params(asdict(self.config))
                mlflow.log_param("data_size", job.data_size)
                
                # Aquí iría la lógica de entrenamiento real
                # Por ahora, simulamos evaluación
                metrics = self._simulate_training(training_data, validation_data)
                
                job.metrics = metrics
                job.new_version = self._increment_version(job.model_id)
                
                # Log métricas
                for metric_name, metric_value in metrics.items():
                    mlflow.log_metric(metric_name, metric_value)
                
                # Registrar nuevo modelo
                self._register_retrained_model(job, metrics)
                
                job.status = "completed"
                job.completed_at = datetime.utcnow().isoformat()
                
                logger.info(f"Retraining completed for job {job.job_id}")
                return True
        
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow().isoformat()
            logger.error(f"Retraining failed for job {job.job_id}: {e}")
            return False
    
    def _simulate_training(
        self,
        training_data: pd.DataFrame,
        validation_data: pd.DataFrame = None
    ) -> Dict[str, float]:
        """
        Simula entrenamiento (placeholder)
        
        Args:
            training_data: Datos de entrenamiento
            validation_data: Datos de validación
        
        Returns:
            Métricas calculadas
        """
        # Aquí iría la lógica real de entrenamiento
        # Por ahora, retornamos métricas simuladas
        metrics = {
            "accuracy": float(np.random.uniform(0.85, 0.95)),
            "precision": float(np.random.uniform(0.82, 0.93)),
            "recall": float(np.random.uniform(0.80, 0.92)),
            "f1_score": float(np.random.uniform(0.81, 0.92)),
            "training_samples": len(training_data),
        }
        
        if validation_data is not None:
            metrics["validation_samples"] = len(validation_data)
        
        return metrics
    
    def _register_retrained_model(self, job: RetrainingJob, metrics: Dict[str, float]):
        """Registra el modelo retrenado"""
        metadata = ModelMetadata(
            model_id=job.model_id,
            model_type="hybrid",
            version=job.new_version,
            description=f"Retrained model from job {job.job_id}",
            metrics=metrics,
            parameters=asdict(self.config),
            status="validation",
            tags={"retrain_job": job.job_id},
        )
        
        self.registry.register_model(metadata)
    
    def promote_to_production(
        self,
        model_id: str,
        version: str,
        approval_required: bool = True
    ) -> bool:
        """
        Promociona un modelo a producción
        
        Args:
            model_id: ID del modelo
            version: Versión a promover
            approval_required: Si se requiere aprobación
        
        Returns:
            True si fue exitoso
        """
        if approval_required and not self.config.auto_approve:
            logger.warning(f"Manual approval required for {model_id}_{version}")
            return False
        
        return self.registry.update_model_status(model_id, version, "production")
    
    def _increment_version(self, model_id: str) -> str:
        """Incrementa la versión de un modelo"""
        history = self.registry.get_version_history(model_id)
        
        if not history:
            return "0.1.0"
        
        last_version = history[0].get('version', '0.0.0')
        parts = last_version.split('.')
        
        try:
            parts[1] = str(int(parts[1]) + 1)
            return '.'.join(parts)
        except:
            return "0.1.0"
    
    def get_job_status(self, job_id: str) -> Optional[RetrainingJob]:
        """
        Obtiene el estado de un job
        
        Args:
            job_id: ID del job
        
        Returns:
            Job encontrado o None
        """
        return self.jobs.get(job_id)
    
    def list_jobs(self, model_id: str = None, status: str = None) -> list:
        """
        Lista jobs de retraining
        
        Args:
            model_id: Filtrar por modelo
            status: Filtrar por estado
        
        Returns:
            Lista de jobs
        """
        jobs = list(self.jobs.values())
        
        if model_id:
            jobs = [j for j in jobs if j.model_id == model_id]
        if status:
            jobs = [j for j in jobs if j.status == status]
        
        return sorted(jobs, key=lambda x: x.created_at, reverse=True)

class AutomaticRetrainingScheduler:
    """Programador de retraining automático"""
    
    def __init__(self, config: RetrainingConfig = None):
        self.config = config or RetrainingConfig()
        self.orchestrator = RetrainingOrchestrator(config)
        self.last_check = None
    
    def check_and_schedule_retraining(self, model_ids: list) -> Dict[str, Any]:
        """
        Verifica si hay modelos que necesiten retraining
        
        Args:
            model_ids: Lista de IDs de modelos a verificar
        
        Returns:
            Resultados de la verificación
        """
        self.last_check = datetime.utcnow()
        results = {
            "timestamp": self.last_check.isoformat(),
            "models_checked": len(model_ids),
            "retraining_needed": [],
            "scheduled_jobs": [],
        }
        
        for model_id in model_ids:
            needs_retrain, reasons = self.orchestrator.check_retrain_needed(model_id)
            
            if needs_retrain:
                results["retraining_needed"].append({
                    "model_id": model_id,
                    "reasons": reasons,
                })
                
                # Crear job de retraining
                job = self.orchestrator.create_retrain_job(model_id)
                results["scheduled_jobs"].append(job.job_id)
                logger.info(f"Retraining scheduled for {model_id}")
        
        return results

# Instancias globales
retrain_config = RetrainingConfig()
retraining_orchestrator = RetrainingOrchestrator(retrain_config)
auto_scheduler = AutomaticRetrainingScheduler(retrain_config)
