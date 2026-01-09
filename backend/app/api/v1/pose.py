"""
Endpoints REST para avaliação de poses
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import base64
import cv2
import numpy as np
import time
from typing import Dict

from app.models.pose import (
    PoseEvaluateRequest,
    PoseEvaluateResponse,
    PoseSelectRequest,
    PoseSelectResponse,
    ErrorResponse
)
from app.core.cv_service import CVService

router = APIRouter()

# Singleton do serviço CV (carrega modelos uma vez)
cv_service = CVService(use_ml=True)


def decode_base64_image(image_base64: str) -> np.ndarray:
    """
    Decodifica imagem Base64 para numpy array (BGR)
    
    Args:
        image_base64: String Base64 (com ou sem prefixo data:image/jpeg;base64,)
    
    Returns:
        Frame OpenCV (BGR)
    """
    # Remove prefixo se existir
    if ',' in image_base64:
        image_base64 = image_base64.split(',')[1]
    
    # Decodifica Base64
    image_bytes = base64.b64decode(image_base64)
    
    # Converte para numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    
    # Decodifica imagem (JPEG/PNG)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if frame is None:
        raise ValueError("Não foi possível decodificar a imagem")
    
    return frame


def encode_base64_image(frame: np.ndarray, quality: int = 85) -> str:
    """
    Codifica frame OpenCV para Base64 (JPEG)
    
    Args:
        frame: Frame OpenCV (BGR)
        quality: Qualidade JPEG (0-100)
    
    Returns:
        String Base64
    """
    # Codifica como JPEG
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    success, encoded_image = cv2.imencode('.jpg', frame, encode_param)
    
    if not success:
        raise ValueError("Não foi possível codificar a imagem")
    
    # Converte para Base64
    image_base64 = base64.b64encode(encoded_image.tobytes()).decode('utf-8')
    
    return image_base64


def landmarks_to_dict(landmarks_obj) -> list:
    """Converte landmarks do MediaPipe para lista de dicts"""
    if landmarks_obj is None:
        return []
    
    landmarks_list = []
    for landmark in landmarks_obj.landmark:
        landmarks_list.append({
            "x": landmark.x,
            "y": landmark.y,
            "z": landmark.z,
            "visibility": landmark.visibility if hasattr(landmark, 'visibility') else None
        })
    return landmarks_list


def determine_status(pose_quality: str) -> str:
    """
    Determina status baseado na mensagem de qualidade
    IMPORTANTE: Verifica "incorreta" ANTES de "correta" para evitar falsos positivos
    """
    if pose_quality is None or pose_quality.strip() == "":
        return "no_detection"
    
    pose_lower = pose_quality.lower()
    
    # Verifica primeiro se é incorreto (prioridade máxima)
    # Procura por padrões que indicam erro/correção necessária
    incorrect_patterns = [
        "posicao incorreta", "posição incorreta",
        "incorreta", 
        "erro", "erros",
        "nao foi possivel", "não foi possível",
        "muito baixo", "muito alto", "fora do intervalo",
        "cotovelo", "angulo", "braco",  # Quando menciona problemas específicos
    ]
    
    correct_patterns = [
        "posicao correta", "posição correta",
        "correta",
        "excelente",
        "bem centralizado", "bem posicionado",
    ]
    
    # Conta quantos padrões de erro aparecem
    incorrect_count = sum(1 for pattern in incorrect_patterns if pattern in pose_lower)
    
    # Se houver qualquer indicação de erro, é incorreto
    if incorrect_count > 0:
        return "incorrect"
    
    # Verifica se é correto (só se não houver erros)
    correct_count = sum(1 for pattern in correct_patterns if pattern in pose_lower)
    if correct_count > 0:
        return "correct"
    
    # Se menciona "centralizado" mas não tem erros explícitos
    if "centralizado" in pose_lower:
        return "correct"
    
    # Se menciona ajustes
    if "ajuste" in pose_lower or "melhor" in pose_lower:
        return "adjustment_needed"
    
    # Padrão não reconhecido
    return "no_detection"


@router.post("/evaluate", response_model=PoseEvaluateResponse)
async def evaluate_pose(request: PoseEvaluateRequest):
    """
    Avalia uma pose a partir de um frame de imagem
    
    Recebe uma imagem Base64, processa com MediaPipe e retorna avaliação
    """
    start_time = time.time()
    
    try:
        # Decodifica imagem
        frame = decode_base64_image(request.image)
        
        # Obtém dimensões
        h, w = frame.shape[:2]
        camera_width = request.camera_width or w
        
        # Processa frame
        frame_annotated, pose_quality, landmarks_obj = cv_service.process_frame(
            frame.copy(),  # Cópia para não modificar original
            request.pose_mode,
            camera_width
        )
        
        # Converte landmarks
        landmarks = landmarks_to_dict(landmarks_obj)
        
        # Determina status
        status = determine_status(pose_quality)
        
        # Codifica imagem anotada
        annotated_image_b64 = encode_base64_image(frame_annotated)
        
        # Calcula tempo de processamento
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return PoseEvaluateResponse(
            success=True,
            pose_quality=pose_quality,
            status=status,
            landmarks=landmarks,
            annotated_image=annotated_image_b64,
            processing_time_ms=processing_time_ms
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar: {str(e)}")


@router.post("/select", response_model=PoseSelectResponse)
async def select_pose(request: PoseSelectRequest):
    """
    Seleciona o modo de pose para avaliação
    """
    pose_names = {
        'double_biceps': 'Duplo Biceps (Frente)',
        'side_chest': 'Side Chest',
        'side_triceps': 'Side Triceps',
        'most_muscular': 'Most Muscular',
        'enquadramento': 'Enquadramento'
    }
    
    if request.pose_mode not in pose_names:
        raise HTTPException(
            status_code=400,
            detail=f"Modo de pose inválido: {request.pose_mode}"
        )
    
    return PoseSelectResponse(
        success=True,
        pose_mode=request.pose_mode,
        pose_name=pose_names[request.pose_mode]
    )

