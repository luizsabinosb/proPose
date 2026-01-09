"""
Modelos Pydantic para requisições e respostas de pose
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from datetime import datetime


class LandmarkPoint(BaseModel):
    """Ponto de landmark do MediaPipe"""
    x: float = Field(..., description="Coordenada X normalizada (0-1)")
    y: float = Field(..., description="Coordenada Y normalizada (0-1)")
    z: float = Field(..., description="Coordenada Z normalizada")
    visibility: Optional[float] = Field(None, description="Visibilidade do landmark (0-1)")


class PoseEvaluateRequest(BaseModel):
    """Requisição para avaliar uma pose"""
    image: str = Field(..., description="Imagem codificada em Base64 (JPEG)")
    pose_mode: Literal[
        "double_biceps",
        "side_chest",
        "side_triceps",
        "most_muscular",
        "enquadramento"
    ] = Field(..., description="Modo de pose a avaliar")
    session_id: Optional[str] = Field(None, description="ID da sessão (opcional)")
    camera_width: Optional[int] = Field(1280, description="Largura da câmera em pixels")


class PoseEvaluateResponse(BaseModel):
    """Resposta da avaliação de pose"""
    success: bool = Field(True, description="Se a avaliação foi bem-sucedida")
    pose_quality: Optional[str] = Field(None, description="Mensagem de avaliação da pose")
    status: Literal[
        "correct",
        "incorrect",
        "adjustment_needed",
        "no_detection"
    ] = Field(..., description="Status da avaliação")
    landmarks: List[LandmarkPoint] = Field(default_factory=list, description="Landmarks detectados")
    annotated_image: Optional[str] = Field(None, description="Imagem anotada em Base64")
    processing_time_ms: int = Field(..., description="Tempo de processamento em milissegundos")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp da avaliação")


class PoseSelectRequest(BaseModel):
    """Requisição para selecionar modo de pose"""
    pose_mode: Literal[
        "double_biceps",
        "side_chest",
        "side_triceps",
        "most_muscular",
        "enquadramento"
    ] = Field(..., description="Modo de pose a selecionar")
    session_id: Optional[str] = Field(None, description="ID da sessão")


class PoseSelectResponse(BaseModel):
    """Resposta da seleção de pose"""
    success: bool = True
    pose_mode: str
    pose_name: str
    selected_at: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Resposta de erro"""
    success: bool = False
    error: str
    details: Optional[dict] = None

