"""
Logging Configuration Module
Configura logging estructurado y centralizado para todo el sistema
"""
import logging
import json
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Dict, Any
from mlops.config import config

class JSONFormatter(logging.Formatter):
    """Formatea logs en formato JSON estructurado"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Agregar excepciones si existen
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Agregar datos extra si están disponibles
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data, default=str)

class StructuredLogger(logging.LoggerAdapter):
    """Logger con capacidad de logging estructurado"""
    
    def process(self, msg: str, kwargs: Dict[Any, Any]) -> tuple:
        """Procesa mensajes de log"""
        return msg, kwargs
    
    def log_with_context(self, level: int, msg: str, extra_data: Dict[str, Any] = None, **kwargs):
        """Log con contexto adicional"""
        if extra_data:
            extra = {"extra_data": extra_data}
            kwargs.update(extra)
        self.log(level, msg, **kwargs)

def setup_logging(logger_name: str = "recipe_recommender") -> logging.Logger:
    """
    Configura logging estructurado para la aplicación
    
    Args:
        logger_name: Nombre del logger
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, config.log_level))
    
    # Evitar duplicados
    if logger.handlers:
        return logger
    
    # Formateador
    json_formatter = JSONFormatter()
    standard_formatter = logging.Formatter(config.log_format)
    
    # Handler para archivos
    log_file = config.logs_dir / f"{logger_name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=config.max_log_size_mb * 1024 * 1024,
        backupCount=config.backup_count
    )
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(standard_formatter)
    logger.addHandler(console_handler)
    
    return logger

# Loggers globales
app_logger = setup_logging("app")
mlops_logger = setup_logging("mlops")
model_logger = setup_logging("model_training")
monitoring_logger = setup_logging("monitoring")
retraining_logger = setup_logging("retraining")

def get_logger(name: str) -> StructuredLogger:
    """Obtiene un logger estructurado"""
    base_logger = logging.getLogger(name)
    return StructuredLogger(base_logger, {})
