"""
BodyVision - Sistema de Análise de Poses de Fisiculturismo
Pacote principal do sistema
"""

__version__ = "1.0.0"
__author__ = "BodyVision Team"

# Importações principais para facilitar uso
# BodyVisionApp foi removido - agora use backend/app/core/cv_service.py
# from .app import BodyVisionApp  # REMOVIDO
from .pose_evaluator import PoseDetector
from .data_collector import DataCollector
from .ml_evaluator import MLEvaluator

from .pose_metrics_loader import PoseMetricsLoader, get_metrics_loader, reload_metrics

__all__ = [
    # 'BodyVisionApp',  # REMOVIDO - use backend/app/core/cv_service.py
    'PoseDetector',
    'DataCollector',
    'MLEvaluator',
    'PoseMetricsLoader',
    'get_metrics_loader',
    'reload_metrics',
]

