"""
Enumeraciones compartidas en el sistema de IA
"""

from enum import Enum


class RiskLevel(str, Enum):
    """Nivel de riesgo identificado en el análisis del proyecto"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class StatusCode(int, Enum):
    """Códigos de estado HTTP para logs de peticiones"""
    SUCCESS = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    SERVER_ERROR = 500
    TIMEOUT = 504
