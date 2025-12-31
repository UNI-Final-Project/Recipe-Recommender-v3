"""
MLOps Integration Tests and Examples
Demuestra cómo usar todos los componentes del sistema de MLOps
"""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

# MLOps imports
from mlops import (
    config,
    model_registry,
    ModelMetadata,
    ModelEvaluator,
    ModelValidator,
    EvaluationReport,
    metrics_collector,
    anomaly_detector,
    health_monitor,
    retraining_orchestrator,
    auto_scheduler,
    get_logger,
)

logger = get_logger(__name__)


class TestModelRegistry(unittest.TestCase):
    """Tests para el Model Registry"""
    
    def setUp(self):
        """Preparar tests"""
        self.model_id = "test_hybrid_ranker"
        self.version = "0.1.0"
    
    def test_register_model(self):
        """Test: Registrar un nuevo modelo"""
        metadata = ModelMetadata(
            model_id=self.model_id,
            model_type="hybrid",
            version=self.version,
            description="Test model",
            metrics={"accuracy": 0.92, "f1": 0.89},
            parameters={"alpha": 0.7, "top_k": 3},
            status="validation"
        )
        
        model_key = model_registry.register_model(metadata)
        
        self.assertEqual(model_key, f"{self.model_id}_{self.version}")
        print(f"✓ Model registered: {model_key}")
    
    def test_update_status(self):
        """Test: Actualizar estado del modelo"""
        # Primero registrar
        self.test_register_model()
        
        # Actualizar a producción
        success = model_registry.update_model_status(
            self.model_id,
            self.version,
            "production"
        )
        
        self.assertTrue(success)
        
        # Verificar
        model = model_registry.get_model(self.model_id, self.version)
        self.assertEqual(model['status'], 'production')
        print(f"✓ Model status updated to production")
    
    def test_get_production_model(self):
        """Test: Obtener modelo en producción"""
        self.test_update_status()
        
        prod_model = model_registry.get_production_model(self.model_id)
        self.assertIsNotNone(prod_model)
        self.assertEqual(prod_model['status'], 'production')
        print(f"✓ Retrieved production model: {prod_model['version']}")
    
    def test_list_models(self):
        """Test: Listar modelos"""
        models = model_registry.list_models()
        
        self.assertIsInstance(models, list)
        print(f"✓ Found {len(models)} models in registry")
    
    def test_version_history(self):
        """Test: Obtener historial de versiones"""
        history = model_registry.get_version_history(self.model_id)
        
        self.assertIsInstance(history, list)
        print(f"✓ Version history: {[m['version'] for m in history]}")


class TestEvaluation(unittest.TestCase):
    """Tests para el módulo de Evaluación"""
    
    def test_ranking_metrics(self):
        """Test: Calcular métricas de ranking"""
        y_true = np.array([4, 3, 5, 2, 1])
        y_pred = np.array([3.8, 3.2, 5.1, 2.3, 1.1])
        
        evaluator = ModelEvaluator()
        metrics = evaluator.calculate_ranking_metrics(y_true, y_pred)
        
        self.assertIn('mse', metrics)
        self.assertIn('mae', metrics)
        self.assertIn('r2_score', metrics)
        
        print(f"✓ Ranking metrics: {metrics}")
    
    def test_classification_metrics(self):
        """Test: Calcular métricas de clasificación"""
        y_true = np.array([1, 0, 1, 1, 0, 1, 0, 0])
        y_pred = np.array([1, 0, 1, 0, 0, 1, 1, 0])
        
        evaluator = ModelEvaluator()
        metrics = evaluator.calculate_classification_metrics(y_true, y_pred)
        
        self.assertIn('accuracy', metrics)
        self.assertIn('precision', metrics)
        self.assertIn('recall', metrics)
        self.assertIn('f1_score', metrics)
        
        print(f"✓ Classification metrics: {metrics}")
    
    def test_ndcg_metric(self):
        """Test: Calcular NDCG"""
        y_true = np.array([3, 2, 3, 0, 1, 2])
        y_scores = np.array([0.8, 0.7, 0.9, 0.2, 0.3, 0.6])
        
        evaluator = ModelEvaluator()
        ndcg = evaluator.calculate_ndcg(y_true, y_scores, k=3)
        
        self.assertGreaterEqual(ndcg, 0)
        self.assertLessEqual(ndcg, 1)
        
        print(f"✓ NDCG@3: {ndcg:.4f}")
    
    def test_data_drift_detection(self):
        """Test: Detectar data drift"""
        baseline_df = pd.DataFrame({
            'price': [10, 20, 30, 40, 50],
            'rating': [3.5, 4.0, 3.8, 4.2, 4.1]
        })
        
        current_df = pd.DataFrame({
            'price': [20, 30, 40, 50, 60],
            'rating': [3.5, 4.0, 3.8, 4.2, 4.1]
        })
        
        validator = ModelValidator()
        drift = validator.check_data_drift(baseline_df, current_df, threshold=0.1)
        
        self.assertIn('drift_detected', drift)
        self.assertIn('details', drift)
        
        print(f"✓ Data drift detected: {drift['drift_detected']}")
        if drift['drift_detected']:
            print(f"  Columns with drift: {drift['columns_with_drift']}")
    
    def test_model_output_validation(self):
        """Test: Validar outputs del modelo"""
        validator = ModelValidator()
        
        # Test válido
        valid_predictions = np.array([0.3, 0.7, 0.5])
        result = validator.validate_model_output(
            valid_predictions,
            expected_shape=(3,),
            value_range=(0, 1)
        )
        
        self.assertTrue(result['valid'])
        print(f"✓ Valid predictions: {result['valid']}")
        
        # Test inválido (NaN)
        invalid_predictions = np.array([0.3, np.nan, 0.5])
        result = validator.validate_model_output(invalid_predictions)
        
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['issues']), 0)
        print(f"✓ Invalid predictions detected: {result['issues']}")


class TestMonitoring(unittest.TestCase):
    """Tests para el módulo de Monitoreo"""
    
    def test_metrics_collection(self):
        """Test: Recolectar métricas"""
        metrics_collector.record("api_latency_ms", 145.5)
        metrics_collector.record("api_latency_ms", 152.3)
        metrics_collector.record("error_rate", 0.02)
        
        latest = metrics_collector.get_latest("api_latency_ms", n=2)
        
        self.assertEqual(len(latest), 2)
        print(f"✓ Metrics collected: {len(latest)} points for api_latency_ms")
    
    def test_anomaly_detection(self):
        """Test: Detectar anomalías"""
        values = np.array([10, 12, 11, 13, 12, 11, 100, 12, 11, 10])
        
        result = anomaly_detector.detect_anomalies(values, threshold=3.0)
        
        self.assertIn('anomalies', result)
        self.assertGreater(len(result['anomalies']), 0)
        print(f"✓ Anomalies detected: {len(result['anomalies'])} anomalies found")
    
    def test_performance_degradation(self):
        """Test: Detectar degradación de rendimiento"""
        metrics = [0.92, 0.91, 0.90, 0.89, 0.88, 0.85, 0.84, 0.83, 0.80]
        
        degraded = anomaly_detector.detect_performance_degradation(
            metrics,
            window_size=3,
            threshold=0.1
        )
        
        self.assertTrue(degraded)
        print(f"✓ Performance degradation detected: {degraded}")
    
    def test_health_check(self):
        """Test: Verificar salud del sistema"""
        status = health_monitor.get_system_status()
        
        self.assertIn('timestamp', status)
        self.assertIn('overall_status', status)
        self.assertIn('api', status)
        
        print(f"✓ System status: {status['overall_status']}")


class TestRetraining(unittest.TestCase):
    """Tests para el módulo de Retraining"""
    
    def test_check_retrain_needed(self):
        """Test: Verificar si es necesario retraining"""
        # Primero registrar un modelo de producción
        metadata = ModelMetadata(
            model_id="test_ranker",
            model_type="hybrid",
            version="1.0.0",
            metrics={"accuracy": 0.92},
            status="production"
        )
        model_registry.register_model(metadata)
        
        # Verificar si necesita retraining
        needs_retrain, reasons = retraining_orchestrator.check_retrain_needed("test_ranker")
        
        self.assertIsInstance(needs_retrain, bool)
        self.assertIsInstance(reasons, dict)
        
        print(f"✓ Retrain needed: {needs_retrain}")
        if needs_retrain:
            print(f"  Reasons: {reasons}")
    
    def test_create_retrain_job(self):
        """Test: Crear job de retraining"""
        job = retraining_orchestrator.create_retrain_job("test_ranker")
        
        self.assertIsNotNone(job.job_id)
        self.assertEqual(job.status, "pending")
        
        print(f"✓ Retrain job created: {job.job_id}")
    
    def test_schedule_retraining(self):
        """Test: Programar retraining automático"""
        results = auto_scheduler.check_and_schedule_retraining(["test_ranker"])
        
        self.assertIn('models_checked', results)
        self.assertIn('scheduled_jobs', results)
        
        print(f"✓ Models checked: {results['models_checked']}")
        print(f"✓ Jobs scheduled: {len(results['scheduled_jobs'])}")


class TestIntegration(unittest.TestCase):
    """Tests de integración completa"""
    
    def test_complete_mlops_workflow(self):
        """Test: Flujo completo de MLOps"""
        print("\n" + "="*60)
        print("COMPLETE MLOps WORKFLOW TEST")
        print("="*60)
        
        # 1. Registrar modelo
        print("\n[1] Registering model...")
        metadata = ModelMetadata(
            model_id="integration_test_model",
            model_type="hybrid",
            version="1.0.0",
            description="Integration test model",
            metrics={"accuracy": 0.92, "f1": 0.89},
            parameters={"alpha": 0.7},
            status="validation",
            tags={"test": "true"}
        )
        model_registry.register_model(metadata)
        print("✓ Model registered")
        
        # 2. Evaluar modelo
        print("\n[2] Evaluating model...")
        evaluator = ModelEvaluator()
        y_true = np.array([4, 3, 5, 2, 1])
        y_pred = np.array([3.8, 3.2, 5.1, 2.3, 1.1])
        metrics = evaluator.calculate_ranking_metrics(y_true, y_pred)
        print(f"✓ Metrics calculated: {metrics}")
        
        # 3. Generar reporte
        print("\n[3] Generating evaluation report...")
        report = EvaluationReport("integration_test_model", "1.0.0")
        report.add_metrics(metrics)
        report_path = report.save()
        print(f"✓ Report saved: {report_path}")
        
        # 4. Monitorear
        print("\n[4] Recording metrics...")
        metrics_collector.record("api_latency_ms", 145.5)
        metrics_collector.record("request_count", 1)
        print("✓ Metrics recorded")
        
        # 5. Verificar salud
        print("\n[5] Checking system health...")
        health = health_monitor.get_system_status()
        print(f"✓ System status: {health['overall_status']}")
        
        # 6. Promover a producción
        print("\n[6] Promoting to production...")
        model_registry.update_model_status(
            "integration_test_model",
            "1.0.0",
            "production"
        )
        print("✓ Model promoted to production")
        
        # 7. Verificar en producción
        print("\n[7] Verifying production model...")
        prod_model = model_registry.get_production_model("integration_test_model")
        self.assertIsNotNone(prod_model)
        self.assertEqual(prod_model['status'], 'production')
        print(f"✓ Production model verified: {prod_model['version']}")
        
        print("\n" + "="*60)
        print("INTEGRATION TEST COMPLETED SUCCESSFULLY ✓")
        print("="*60)


def run_examples():
    """Ejecuta ejemplos de uso"""
    
    print("\n" + "="*60)
    print("MLOPS USAGE EXAMPLES")
    print("="*60)
    
    # Ejemplo 1: Usar Model Registry
    print("\n[EJEMPLO 1] Usar Model Registry")
    print("-" * 60)
    
    models = model_registry.list_models()
    print(f"Modelos registrados: {len(models)}")
    for model in models[:3]:
        print(f"  - {model['model_key']}: {model['status']}")
    
    # Ejemplo 2: Obtener métricas
    print("\n[EJEMPLO 2] Obtener Métricas")
    print("-" * 60)
    
    metrics_collector.record("api_latency_ms", 150)
    metrics_collector.record("api_latency_ms", 160)
    stats = metrics_collector.get_stats("api_latency_ms", window_minutes=60)
    print(f"Latencia media: {stats.get('mean', 0):.2f}ms")
    print(f"P95: {stats.get('p95', 0):.2f}ms")
    
    # Ejemplo 3: Detectar anomalías
    print("\n[EJEMPLO 3] Detectar Anomalías")
    print("-" * 60)
    
    values = np.array([100, 105, 102, 104, 103, 200, 101, 102])
    result = anomaly_detector.detect_anomalies(values, threshold=2.5)
    print(f"Anomalías detectadas: {result['anomaly_count']}")
    
    # Ejemplo 4: Evaluar modelo
    print("\n[EJEMPLO 4] Evaluar Modelo")
    print("-" * 60)
    
    evaluator = ModelEvaluator()
    y_true = np.array([1, 0, 1, 1, 0])
    y_pred = np.array([1, 0, 1, 0, 0])
    metrics = evaluator.calculate_classification_metrics(y_true, y_pred)
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"F1 Score: {metrics['f1_score']:.4f}")


if __name__ == "__main__":
    
    # Ejecutar ejemplos
    run_examples()
    
    # Ejecutar tests unitarios
    print("\n" + "="*60)
    print("RUNNING UNIT TESTS")
    print("="*60)
    
    unittest.main(argv=[''], exit=False, verbosity=2)
