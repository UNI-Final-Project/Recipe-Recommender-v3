"""
Model Registry Module
Gestiona el versionado y registro de modelos
"""
import json
import mlflow
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from mlops.config import config, MODEL_VERSIONS
from mlops.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class ModelMetadata:
    """Metadatos de un modelo"""
    model_id: str
    model_type: str  # "embedding", "ranking", "hybrid"
    version: str  # semantic versioning: major.minor.patch
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    description: str = ""
    metrics: Dict[str, float] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: str = "training"  # training, validation, production, archived
    parent_version: Optional[str] = None
    deployment_date: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    
class ModelRegistry:
    """Registro central de modelos"""
    
    def __init__(self, registry_path: Path = config.model_registry_path):
        self.registry_path = registry_path
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_registry()
    
    def _load_registry(self):
        """Carga el registro de modelos desde archivo"""
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                self.models = json.load(f)
        else:
            self.models = {}
        logger.info(f"Registry loaded with {len(self.models)} models")
    
    def _save_registry(self):
        """Guarda el registro de modelos"""
        with open(self.registry_path, 'w') as f:
            json.dump(self.models, f, indent=2, default=str)
        logger.info(f"Registry saved with {len(self.models)} models")
    
    def register_model(self, metadata: ModelMetadata) -> str:
        """
        Registra un nuevo modelo
        
        Args:
            metadata: Metadatos del modelo
        
        Returns:
            ID del modelo registrado
        """
        model_key = f"{metadata.model_id}_{metadata.version}"
        
        if model_key in self.models:
            logger.warning(f"Model {model_key} already exists, updating...")
        
        self.models[model_key] = asdict(metadata)
        self._save_registry()
        
        # Log en MLflow
        try:
            with mlflow.start_run(run_name=f"register_{model_key}"):
                mlflow.log_params(metadata.parameters)
                mlflow.log_metrics(metadata.metrics)
                for tag_key, tag_val in metadata.tags.items():
                    mlflow.set_tag(tag_key, tag_val)
                mlflow.log_param("status", metadata.status)
            logger.info(f"Model {model_key} registered successfully")
        except Exception as e:
            logger.warning(f"Could not log to MLflow: {e}")
        
        return model_key
    
    def update_model_status(self, model_id: str, version: str, status: str) -> bool:
        """
        Actualiza el estado de un modelo
        
        Args:
            model_id: ID del modelo
            version: Versión del modelo
            status: Nuevo estado
        
        Returns:
            True si se actualizó exitosamente
        """
        model_key = f"{model_id}_{version}"
        
        if model_key not in self.models:
            logger.error(f"Model {model_key} not found")
            return False
        
        old_status = self.models[model_key]['status']
        self.models[model_key]['status'] = status
        
        if status == "production":
            self.models[model_key]['deployment_date'] = datetime.utcnow().isoformat()
        
        self._save_registry()
        logger.info(f"Model {model_key} status updated: {old_status} -> {status}")
        
        return True
    
    def get_production_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene el modelo en producción para un modelo_id
        
        Args:
            model_id: ID del modelo
        
        Returns:
            Metadatos del modelo en producción o None
        """
        for key, model_data in self.models.items():
            if key.startswith(model_id) and model_data.get('status') == 'production':
                return model_data
        return None
    
    def get_model(self, model_id: str, version: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un modelo específico
        
        Args:
            model_id: ID del modelo
            version: Versión del modelo
        
        Returns:
            Metadatos del modelo o None
        """
        model_key = f"{model_id}_{version}"
        return self.models.get(model_key)
    
    def list_models(self, model_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Lista modelos con filtros opcionales
        
        Args:
            model_id: Filtrar por ID del modelo
            status: Filtrar por estado
        
        Returns:
            Lista de modelos que coinciden con los filtros
        """
        results = []
        for key, model_data in self.models.items():
            if model_id and not key.startswith(model_id):
                continue
            if status and model_data.get('status') != status:
                continue
            results.append({**model_data, "model_key": key})
        
        return sorted(results, key=lambda x: x['timestamp'], reverse=True)
    
    def get_version_history(self, model_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de versiones de un modelo
        
        Args:
            model_id: ID del modelo
        
        Returns:
            Lista de versiones ordenadas por timestamp
        """
        versions = [m for m in self.list_models() if m.get('model_key', '').startswith(model_id)]
        return sorted(versions, key=lambda x: x['timestamp'], reverse=True)
    
    def archive_model(self, model_id: str, version: str) -> bool:
        """
        Archiva un modelo
        
        Args:
            model_id: ID del modelo
            version: Versión del modelo
        
        Returns:
            True si se archivó exitosamente
        """
        return self.update_model_status(model_id, version, "archived")
    
    def validate_semantic_version(self, version: str) -> bool:
        """
        Valida que una versión siga semantic versioning
        
        Args:
            version: Versión a validar (ej: 1.0.0)
        
        Returns:
            True si es válida
        """
        try:
            parts = version.split('.')
            if len(parts) != 3:
                return False
            return all(part.isdigit() for part in parts)
        except:
            return False

# Instancia global
model_registry = ModelRegistry()
