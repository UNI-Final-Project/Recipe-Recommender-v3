"""
Model Evaluation Module
Módulo para evaluación de modelos y cálculo de métricas
"""
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Any, List, Optional
from datetime import datetime
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, 
    precision_score, recall_score, f1_score, accuracy_score
)
import mlflow
from pathlib import Path
from mlops.config import config
from mlops.logging_config import get_logger
from mlops.model_registry import ModelMetadata

logger = get_logger(__name__)

class ModelEvaluator:
    """Evaluador de modelos con métricas estándar de ML"""
    
    @staticmethod
    def calculate_ranking_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calcula métricas de ranking
        
        Args:
            y_true: Valores verdaderos
            y_pred: Valores predichos
        
        Returns:
            Diccionario de métricas
        """
        mse = mean_squared_error(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        
        # R2 score (coeficiente de determinación)
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        r2_score = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        metrics = {
            "mse": float(mse),
            "mae": float(mae),
            "rmse": float(rmse),
            "r2_score": float(r2_score),
        }
        
        logger.info(f"Ranking metrics calculated: {metrics}")
        return metrics
    
    @staticmethod
    def calculate_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calcula métricas de clasificación
        
        Args:
            y_true: Valores verdaderos (binarios o multi-clase)
            y_pred: Valores predichos
        
        Returns:
            Diccionario de métricas
        """
        accuracy = accuracy_score(y_true, y_pred)
        
        # Determinar si es binario o multi-clase
        if len(np.unique(y_true)) == 2:
            average = 'binary'
        else:
            average = 'weighted'
        
        precision = precision_score(y_true, y_pred, average=average, zero_division=0)
        recall = recall_score(y_true, y_pred, average=average, zero_division=0)
        f1 = f1_score(y_true, y_pred, average=average, zero_division=0)
        
        metrics = {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
        }
        
        logger.info(f"Classification metrics calculated: {metrics}")
        return metrics
    
    @staticmethod
    def calculate_ndcg(y_true: np.ndarray, y_scores: np.ndarray, k: int = 5) -> float:
        """
        Calcula NDCG (Normalized Discounted Cumulative Gain) para ranking
        
        Args:
            y_true: Valores de relevancia verdaderos
            y_scores: Scores predichos
            k: Número de elementos a considerar
        
        Returns:
            Score NDCG
        """
        def dcg(scores: np.ndarray, k: int) -> float:
            return np.sum((2 ** scores[:k] - 1) / np.log2(np.arange(2, k + 2)))
        
        # DCG ideal (ordenado por valores verdaderos)
        idcg = dcg(np.sort(y_true)[::-1], k)
        
        if idcg == 0:
            return 0
        
        # DCG real (ordenado por scores predichos)
        indices = np.argsort(y_scores)[::-1]
        dcg_score = dcg(y_true[indices], k)
        
        ndcg = dcg_score / idcg
        logger.debug(f"NDCG@{k} calculated: {ndcg:.4f}")
        
        return float(ndcg)
    
    @staticmethod
    def calculate_mrr(y_true: np.ndarray, y_scores: np.ndarray) -> float:
        """
        Calcula MRR (Mean Reciprocal Rank)
        
        Args:
            y_true: Valores de relevancia
            y_scores: Scores predichos
        
        Returns:
            Score MRR
        """
        indices = np.argsort(y_scores)[::-1]
        for i, idx in enumerate(indices):
            if y_true[idx] > 0:
                mrr = 1 / (i + 1)
                logger.debug(f"MRR calculated: {mrr:.4f}")
                return float(mrr)
        return 0.0
    
    @staticmethod
    def calculate_retrieval_metrics(
        y_true: np.ndarray,
        y_scores: np.ndarray,
        threshold: float = 0.5
    ) -> Dict[str, float]:
        """
        Calcula métricas de recuperación (retrieval metrics)
        
        Args:
            y_true: Relevancia verdadera
            y_scores: Scores predichos
            threshold: Umbral para positivos
        
        Returns:
            Diccionario de métricas
        """
        y_pred_binary = (y_scores >= threshold).astype(int)
        y_true_binary = (y_true >= threshold).astype(int)
        
        tp = np.sum((y_true_binary == 1) & (y_pred_binary == 1))
        fp = np.sum((y_true_binary == 0) & (y_pred_binary == 1))
        fn = np.sum((y_true_binary == 1) & (y_pred_binary == 0))
        tn = np.sum((y_true_binary == 0) & (y_pred_binary == 0))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        
        metrics = {
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "specificity": float(specificity),
            "tp": int(tp),
            "fp": int(fp),
            "tn": int(tn),
            "fn": int(fn),
        }
        
        logger.info(f"Retrieval metrics calculated: {metrics}")
        return metrics


class ModelValidator:
    """Validador de modelos y datos"""
    
    @staticmethod
    def check_data_drift(
        baseline_data: pd.DataFrame,
        current_data: pd.DataFrame,
        threshold: float = 0.1
    ) -> Dict[str, Any]:
        """
        Detecta data drift comparando distribuciones
        
        Args:
            baseline_data: Datos de referencia
            current_data: Datos actuales
            threshold: Umbral de divergencia
        
        Returns:
            Diccionario con información de drift
        """
        drift_detected = False
        drift_details = {}
        
        for column in baseline_data.columns:
            if column not in current_data.columns:
                continue
            
            if baseline_data[column].dtype in ['float64', 'int64']:
                # Comparar distribuciones numéricas
                baseline_mean = baseline_data[column].mean()
                current_mean = current_data[column].mean()
                
                if baseline_mean != 0:
                    change_pct = abs(current_mean - baseline_mean) / abs(baseline_mean)
                else:
                    change_pct = 0
                
                if change_pct > threshold:
                    drift_detected = True
                    drift_details[column] = {
                        "baseline_mean": float(baseline_mean),
                        "current_mean": float(current_mean),
                        "change_pct": float(change_pct),
                    }
        
        logger.info(f"Data drift check complete. Drift detected: {drift_detected}")
        return {
            "drift_detected": drift_detected,
            "columns_with_drift": list(drift_details.keys()),
            "details": drift_details,
        }
    
    @staticmethod
    def validate_model_output(
        predictions: np.ndarray,
        expected_shape: Tuple[int, ...] = None,
        value_range: Tuple[float, float] = None
    ) -> Dict[str, Any]:
        """
        Valida las salidas de un modelo
        
        Args:
            predictions: Predicciones del modelo
            expected_shape: Forma esperada
            value_range: Rango de valores esperado (min, max)
        
        Returns:
            Diccionario de validación
        """
        validation_result = {
            "valid": True,
            "issues": [],
        }
        
        # Validar forma
        if expected_shape and predictions.shape != expected_shape:
            validation_result["valid"] = False
            validation_result["issues"].append(
                f"Shape mismatch: expected {expected_shape}, got {predictions.shape}"
            )
        
        # Validar valores NaN/Inf
        if np.any(np.isnan(predictions)):
            validation_result["valid"] = False
            validation_result["issues"].append("NaN values detected in predictions")
        
        if np.any(np.isinf(predictions)):
            validation_result["valid"] = False
            validation_result["issues"].append("Inf values detected in predictions")
        
        # Validar rango
        if value_range:
            if np.any(predictions < value_range[0]) or np.any(predictions > value_range[1]):
                validation_result["valid"] = False
                validation_result["issues"].append(
                    f"Values out of range [{value_range[0]}, {value_range[1]}]"
                )
        
        logger.info(f"Model output validation: {validation_result['valid']}")
        return validation_result


class EvaluationReport:
    """Genera reportes de evaluación"""
    
    def __init__(self, model_id: str, version: str):
        self.model_id = model_id
        self.version = version
        self.timestamp = datetime.utcnow()
        self.metrics: Dict[str, float] = {}
        self.validation_results: Dict[str, Any] = {}
    
    def add_metrics(self, metrics: Dict[str, float]):
        """Agrega métricas al reporte"""
        self.metrics.update(metrics)
    
    def add_validation(self, validation_name: str, result: Dict[str, Any]):
        """Agrega resultado de validación"""
        self.validation_results[validation_name] = result
    
    def save(self, output_path: Optional[Path] = None) -> Path:
        """
        Guarda el reporte en formato JSON
        
        Args:
            output_path: Ruta de salida
        
        Returns:
            Ruta del archivo guardado
        """
        if output_path is None:
            output_path = config.metrics_dir / f"{self.model_id}_{self.version}_{self.timestamp.timestamp()}.json"
        
        import json
        report_data = {
            "model_id": self.model_id,
            "version": self.version,
            "timestamp": self.timestamp.isoformat(),
            "metrics": self.metrics,
            "validation_results": self.validation_results,
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        logger.info(f"Evaluation report saved to {output_path}")
        return output_path
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el reporte a diccionario"""
        return {
            "model_id": self.model_id,
            "version": self.version,
            "timestamp": self.timestamp.isoformat(),
            "metrics": self.metrics,
            "validation_results": self.validation_results,
        }
