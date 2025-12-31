"""
Ejemplo: Script de Retraining Automático Scheduled
Ejecutar con: python schedule_retraining.py
o con APScheduler/cron en producción
"""

import asyncio
import time
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# MLOps imports
from mlops import (
    auto_scheduler,
    retraining_orchestrator,
    model_registry,
    ModelMetadata,
    get_logger,
)

logger = get_logger(__name__)

class AutoRetrainingScheduler:
    """Programador de retraining automático"""
    
    def __init__(self, check_interval_hours: int = 24):
        self.check_interval_hours = check_interval_hours
        self.models_to_monitor = ["hybrid_ranker"]
        self.is_running = False
    
    def run_once(self):
        """Ejecuta una verificación de retraining"""
        logger.info("Starting retraining check...")
        
        try:
            # Verificar si hay modelos que necesiten retraining
            results = auto_scheduler.check_and_schedule_retraining(self.models_to_monitor)
            
            logger.info(f"Retraining check completed: {results}")
            
            # Si hay modelos que necesitan retraining, procesarlos
            for model_id in [r['model_id'] for r in results.get('retraining_needed', [])]:
                self._handle_retraining(model_id)
            
            return results
        
        except Exception as e:
            logger.error(f"Error in retraining check: {e}")
            return {"error": str(e)}
    
    def _handle_retraining(self, model_id: str):
        """Maneja el retraining de un modelo"""
        logger.info(f"Processing retraining for {model_id}")
        
        # Crear job
        job = retraining_orchestrator.create_retrain_job(model_id)
        
        try:
            # Cargar datos de entrenamiento
            # En producción, esto vendría de una base de datos
            training_data = self._load_training_data(model_id)
            validation_data = self._load_validation_data(model_id)
            
            if training_data is None or len(training_data) == 0:
                logger.warning(f"No training data available for {model_id}")
                job.status = "cancelled"
                return
            
            # Ejecutar retraining
            success = retraining_orchestrator.execute_retrain(
                job=job,
                training_data=training_data,
                validation_data=validation_data
            )
            
            if success and job.metrics.get('accuracy', 0) > 0.85:
                # Promover a producción
                logger.info(f"Metrics: {job.metrics}")
                
                # Obtener modelo anterior
                old_model = model_registry.get_production_model(model_id)
                
                if old_model:
                    old_accuracy = old_model.get('metrics', {}).get('accuracy', 0)
                    new_accuracy = job.metrics.get('accuracy', 0)
                    
                    # Si mejora significativamente, promover
                    if new_accuracy > old_accuracy * 1.02:  # 2% improvement
                        model_registry.update_model_status(
                            model_id,
                            job.new_version,
                            "production"
                        )
                        logger.info(f"Model {model_id} promoted to production")
                    else:
                        logger.warning(f"Model {model_id} not promoted: insufficient improvement")
                        # Archivar versión anterior
                        model_registry.update_model_status(
                            model_id,
                            job.new_version,
                            "archived"
                        )
                else:
                    # Primer modelo, promover directamente
                    model_registry.update_model_status(
                        model_id,
                        job.new_version,
                        "production"
                    )
                    logger.info(f"First production model {model_id} deployed")
        
        except Exception as e:
            logger.error(f"Error in retraining for {model_id}: {e}")
            job.status = "failed"
            job.error_message = str(e)
    
    def _load_training_data(self, model_id: str) -> pd.DataFrame:
        """
        Carga datos de entrenamiento
        
        En producción, esto se conectaría a una base de datos
        """
        # Placeholder: generar datos sintéticos para demostración
        logger.info(f"Loading training data for {model_id}")
        
        try:
            # Intentar cargar desde archivo
            data_path = Path("data") / "training_data.csv"
            if data_path.exists():
                return pd.read_csv(data_path)
            else:
                # Si no existe, retornar datos sintéticos
                logger.warning(f"No training data file found, using synthetic data")
                return pd.DataFrame({
                    'query': ['pollo', 'pasta', 'vegetales'] * 30,
                    'recipe_id': list(range(90)),
                    'rating': np.random.uniform(3, 5, 90),
                })
        
        except Exception as e:
            logger.error(f"Error loading training data: {e}")
            return None
    
    def _load_validation_data(self, model_id: str) -> pd.DataFrame:
        """
        Carga datos de validación
        """
        logger.info(f"Loading validation data for {model_id}")
        
        try:
            data_path = Path("data") / "validation_data.csv"
            if data_path.exists():
                return pd.read_csv(data_path)
            else:
                # Datos sintéticos
                logger.warning(f"No validation data file found, using synthetic data")
                return pd.DataFrame({
                    'query': ['pollo', 'pasta'] * 15,
                    'recipe_id': list(range(30)),
                    'rating': np.random.uniform(3, 5, 30),
                })
        
        except Exception as e:
            logger.error(f"Error loading validation data: {e}")
            return None
    
    def start_scheduler(self):
        """Inicia el programador (usa con APScheduler en producción)"""
        self.is_running = True
        logger.info(f"Scheduler started with interval: {self.check_interval_hours} hours")
        
        # Nota: En producción, usar APScheduler o cron
        # Este es solo un ejemplo simple
        
        try:
            while self.is_running:
                self.run_once()
                logger.info(f"Next check in {self.check_interval_hours} hours")
                time.sleep(self.check_interval_hours * 3600)
        
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            self.is_running = False


def setup_apscheduler_example():
    """
    Ejemplo usando APScheduler (recommended para producción)
    Instalar: pip install apscheduler
    """
    
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    
    scheduler = BackgroundScheduler()
    
    # Crear instancia del programador
    retraining_scheduler = AutoRetrainingScheduler(check_interval_hours=24)
    
    # Agregar job
    scheduler.add_job(
        func=retraining_scheduler.run_once,
        trigger=IntervalTrigger(hours=24),
        id='retrain_check',
        name='Automatic Retraining Check',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("APScheduler started for retraining")
    
    return scheduler


def setup_cron_example():
    """
    Ejemplo usando cron (Linux/Mac)
    Agregar a crontab: crontab -e
    
    # Ejecutar cada día a las 2:00 AM
    0 2 * * * cd /path/to/project && python schedule_retraining.py
    """
    pass


if __name__ == "__main__":
    """
    Script principal para ejecutar retraining automático
    """
    
    print("=" * 60)
    print("AutoML Retraining Scheduler")
    print("=" * 60)
    
    # Crear programador
    scheduler = AutoRetrainingScheduler(check_interval_hours=24)
    
    # Ejecutar una verificación inmediata
    print("\n[1/3] Running initial retraining check...")
    results = scheduler.run_once()
    print(f"Results: {results}")
    
    # Opciones de ejecución
    print("\n" + "=" * 60)
    print("Execution Options:")
    print("=" * 60)
    print("1. Manual execution (una sola vez) ✓ Completado")
    print("2. Continuous monitoring (ejecutar cada 24h)")
    print("3. APScheduler (recomendado para producción)")
    
    response = input("\nSelect option (1-3) [default: 1]: ").strip() or "1"
    
    if response == "2":
        print("\nStarting continuous monitoring (Ctrl+C to stop)...")
        scheduler.start_scheduler()
    
    elif response == "3":
        print("\nAPScheduler requires: pip install apscheduler")
        print("Uncomment setup_apscheduler_example() to use it")
        # scheduler_obj = setup_apscheduler_example()
        # Keep running...
        # scheduler_obj.print_jobs()
    
    else:
        print("\nManual check completed. Use scheduling in production!")
        
        # Mostrar estado de modelos
        print("\n" + "=" * 60)
        print("Model Registry Status:")
        print("=" * 60)
        models = model_registry.list_models()
        for model in models:
            print(f"- {model['model_key']}: {model['status']}")
