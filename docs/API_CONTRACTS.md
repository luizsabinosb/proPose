# 📡 Contratos de API - BodyVision

## Base URL

```
Desenvolvimento: http://localhost:8000
Produção: https://api.bodyvision.app
```

## WebSocket Endpoint

```
ws://localhost:8000/ws/pose/stream
```

---

## 🔄 Endpoints REST

### 1. Avaliar Pose (Frame Único)

**POST** `/api/v1/pose/evaluate`

Avalia um frame de imagem para uma pose específica.

#### Request Body

```json
{
  "image": "base64_encoded_image_jpeg",
  "pose_mode": "double_biceps",
  "session_id": "optional_session_id"
}
```

#### Response 200 OK

```json
{
  "success": true,
  "data": {
    "pose_quality": "Usuário bem centralizado na imagem. Posição correta.",
    "status": "correct",  // "correct" | "incorrect" | "adjustment_needed" | "no_detection"
    "landmarks": {
      "normalized": [
        {"x": 0.5, "y": 0.3, "z": 0.1, "visibility": 0.9},
        // ... 33 landmarks do MediaPipe
      ],
      "pixel": [
        {"x": 640, "y": 360, "z": 0.1},
        // ... coordenadas em pixels
      ]
    },
    "metrics": {
      "symmetry_score": 0.95,
      "angles": {
        "left_arm": 165.0,
        "right_arm": 163.0,
        "left_leg": 175.0,
        "right_leg": 174.0
      },
      "alignment": {
        "shoulders_level": true,
        "hips_level": true,
        "spine_straight": true
      }
    },
    "annotated_image": "base64_encoded_image_with_skeleton",
    "timestamp": "2024-01-15T10:30:00Z",
    "processing_time_ms": 45
  }
}
```

#### Response 400 Bad Request

```json
{
  "success": false,
  "error": {
    "code": "INVALID_IMAGE",
    "message": "Imagem inválida ou corrompida",
    "details": {}
  }
}
```

#### Response 422 Unprocessable Entity

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Dados de entrada inválidos",
    "details": {
      "pose_mode": ["Valor inválido. Opções: double_biceps, back_double_biceps, side_chest, most_muscular, enquadramento"]
    }
  }
}
```

---

### 2. Selecionar Modo de Pose

**POST** `/api/v1/pose/select`

Define o modo de pose para avaliação.

#### Request Body

```json
{
  "pose_mode": "double_biceps",
  "session_id": "optional_session_id"
}
```

#### Response 200 OK

```json
{
  "success": true,
  "data": {
    "pose_mode": "double_biceps",
    "pose_name": "Duplo Bíceps (Frente)",
    "instructions": [
      "Mantenha os braços levantados",
      "Contraia os bíceps",
      "Mantenha simetria"
    ],
    "selected_at": "2024-01-15T10:30:00Z"
  }
}
```

---

### 3. Iniciar Sessão

**POST** `/api/v1/session/start`

Inicia uma nova sessão de avaliação.

#### Request Body (Opcional)

```json
{
  "initial_pose": "enquadramento",
  "user_preferences": {
    "fps_target": 30,
    "ml_enabled": true
  }
}
```

#### Response 201 Created

```json
{
  "success": true,
  "data": {
    "session_id": "uuid-v4-session-id",
    "created_at": "2024-01-15T10:30:00Z",
    "settings": {
      "fps_target": 30,
      "ml_enabled": true,
      "current_pose": "enquadramento"
    }
  }
}
```

---

### 4. Finalizar Sessão

**POST** `/api/v1/session/{session_id}/end`

Finaliza uma sessão e retorna estatísticas.

#### Response 200 OK

```json
{
  "success": true,
  "data": {
    "session_id": "uuid-v4-session-id",
    "duration_seconds": 300,
    "frames_processed": 9000,
    "statistics": {
      "total_evaluations": 9000,
      "correct_count": 7200,
      "incorrect_count": 1500,
      "no_detection_count": 300,
      "average_processing_time_ms": 42
    },
    "ended_at": "2024-01-15T10:35:00Z"
  }
}
```

---

### 5. Coletar Dados para Treinamento

**POST** `/api/v1/data/collect`

Salva um frame e landmarks para treinamento de ML.

#### Request Body

```json
{
  "image": "base64_encoded_image_jpeg",
  "landmarks": {
    "normalized": [/* 33 landmarks */],
    "pixel": [/* 33 landmarks */]
  },
  "label": "correct",  // "correct" | "incorrect" | "pending"
  "pose_mode": "double_biceps",
  "session_id": "optional_session_id",
  "metadata": {
    "user_notes": "Opcional",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

#### Response 201 Created

```json
{
  "success": true,
  "data": {
    "sample_id": "uuid-v4-sample-id",
    "saved_at": "2024-01-15T10:30:00Z",
    "validation": {
      "passed": true,
      "checks": {
        "blur_detection": true,
        "landmark_visibility": true,
        "duplicate_detection": false
      }
    }
  }
}
```

#### Response 400 Bad Request (Validação Falhou)

```json
{
  "success": false,
  "error": {
    "code": "QUALITY_CHECK_FAILED",
    "message": "Amostra não passou na validação de qualidade",
    "details": {
      "blur_detection": false,
      "reason": "Imagem muito borrada (Laplacian variance < 100)"
    }
  }
}
```

---

### 6. Obter Estatísticas de Coleta

**GET** `/api/v1/data/statistics`

Retorna estatísticas de dados coletados.

#### Query Parameters

- `pose_mode` (opcional): Filtrar por pose
- `start_date` (opcional): Data inicial (ISO 8601)
- `end_date` (opcional): Data final (ISO 8601)

#### Response 200 OK

```json
{
  "success": true,
  "data": {
    "total_samples": 1500,
    "by_label": {
      "correct": 800,
      "incorrect": 600,
      "pending": 100
    },
    "by_pose": {
      "double_biceps": 500,
      "back_double_biceps": 400,
      "side_chest": 300,
      "most_muscular": 200,
      "enquadramento": 100
    },
    "last_collected": "2024-01-15T10:30:00Z"
  }
}
```

---

## 🔌 WebSocket Stream

### Conectar

```
ws://localhost:8000/ws/pose/stream?session_id=uuid&pose_mode=double_biceps
```

### Enviar Frame (Client → Server)

```json
{
  "type": "frame",
  "data": {
    "image": "base64_encoded_image_jpeg",
    "frame_number": 1234,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Receber Resultado (Server → Client)

```json
{
  "type": "evaluation",
  "data": {
    "frame_number": 1234,
    "pose_quality": "Usuário bem centralizado na imagem.",
    "status": "correct",
    "landmarks": {
      "normalized": [/* ... */]
    },
    "metrics": {
      "symmetry_score": 0.95,
      "angles": {/* ... */}
    },
    "annotated_image": "base64_encoded_image_with_skeleton",
    "processing_time_ms": 45,
    "timestamp": "2024-01-15T10:30:00.045Z"
  }
}
```

### Receber Erro (Server → Client)

```json
{
  "type": "error",
  "data": {
    "code": "PROCESSING_ERROR",
    "message": "Erro ao processar frame",
    "frame_number": 1234
  }
}
```

### Comandos de Controle (Client → Server)

```json
// Mudar pose
{
  "type": "command",
  "command": "change_pose",
  "data": {
    "pose_mode": "side_chest"
  }
}

// Pausar stream
{
  "type": "command",
  "command": "pause"
}

// Retomar stream
{
  "type": "command",
  "command": "resume"
}

// Coletar dados
{
  "type": "command",
  "command": "collect",
  "data": {
    "label": "correct"
  }
}
```

---

## 📋 Modelos Pydantic (Backend)

### Request Models

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class PoseEvaluateRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded JPEG image")
    pose_mode: Literal[
        "double_biceps",
        "back_double_biceps", 
        "side_chest",
        "most_muscular",
        "enquadramento"
    ]
    session_id: Optional[str] = None

class PoseSelectRequest(BaseModel):
    pose_mode: Literal[
        "double_biceps",
        "back_double_biceps",
        "side_chest", 
        "most_muscular",
        "enquadramento"
    ]
    session_id: Optional[str] = None

class DataCollectRequest(BaseModel):
    image: str
    landmarks: dict
    label: Literal["correct", "incorrect", "pending"]
    pose_mode: str
    session_id: Optional[str] = None
    metadata: Optional[dict] = None
```

### Response Models

```python
class LandmarkPoint(BaseModel):
    x: float
    y: float
    z: float
    visibility: Optional[float] = None

class Metrics(BaseModel):
    symmetry_score: float
    angles: dict[str, float]
    alignment: dict[str, bool]

class EvaluationResponse(BaseModel):
    pose_quality: str
    status: Literal["correct", "incorrect", "adjustment_needed", "no_detection"]
    landmarks: dict[str, list[LandmarkPoint]]
    metrics: Metrics
    annotated_image: str
    timestamp: datetime
    processing_time_ms: int

class APIResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[dict] = None
```

---

## 🔐 Autenticação (Futuro)

Para produção, adicionar:

### Headers

```
Authorization: Bearer <jwt_token>
```

### Endpoint de Autenticação

**POST** `/api/v1/auth/login`

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "access_token": "jwt_token_here",
    "token_type": "bearer",
    "expires_in": 3600
  }
}
```

---

## 📊 Status Codes

- `200 OK`: Requisição bem-sucedida
- `201 Created`: Recurso criado com sucesso
- `400 Bad Request`: Dados inválidos
- `401 Unauthorized`: Não autenticado (futuro)
- `403 Forbidden`: Sem permissão (futuro)
- `404 Not Found`: Recurso não encontrado
- `422 Unprocessable Entity`: Validação falhou
- `500 Internal Server Error`: Erro interno do servidor
- `503 Service Unavailable`: Serviço temporariamente indisponível

---

## ⚡ Rate Limiting (Futuro)

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642262400
```

Limites propostos:
- REST endpoints: 100 req/min por IP
- WebSocket: 1 conexão por sessão
- Frame stream: 30 FPS máximo

---

**Documento v1.0** - Data: 2024

