# 🔄 Plano de Refatoração - Remoção do Kivy e Migração para Flutter + FastAPI

## 📋 Análise do Código Atual

### ✅ Código a MANTER (Core de Visão Computacional)

1. **`bodyvision/pose_evaluator.py`**
   - `PoseDetector` - Detecção MediaPipe
   - `calculate_angle()` - Cálculo de ângulos
   - Métodos de avaliação: `evaluate_double_biceps()`, `evaluate_centered()`, etc.
   - ✅ **MANTER INTEGRO** - Lógica de CV funcional

2. **`bodyvision/data_collector.py`**
   - `DataCollector` - Sistema de coleta para ML
   - Validações de qualidade
   - ✅ **MANTER** - Necessário para treinamento

3. **`bodyvision/ml_evaluator.py`**
   - `MLEvaluator` - Avaliação com ML
   - ✅ **MANTER** - Integração com modelos treinados

4. **`bodyvision/camera_utils.py`**
   - `find_camera()` - Detecção de câmera
   - ✅ **MANTER** - Útil no backend

### ❌ Código a REMOVER (Interface)

1. **`bodyvision/gui/kivy_app.py`** - Interface Kivy completa
2. **`bodyvision/ui_renderer.py`** - Renderização UI OpenCV
3. **`bodyvision/ui_helpers.py`** - Helpers de UI OpenCV
4. **`bodyvision/text_renderer.py`** - Renderização de texto (será no Flutter)
5. **`run_kivy.py`** - Entry point Kivy

### 🔄 Código a REFATORAR

1. **`bodyvision/app.py`**
   - Método `process_frame()` → Extrair para serviço CV
   - Método `_evaluate_pose()` → Extrair para serviço CV
   - Loop `run()` → Remover (será no Flutter)
   - Classe `BodyVisionApp` → Dividir em:
     - `CVService` (backend)
     - `PoseSession` (backend)

---

## 🎯 Nova Estrutura de Pastas

```
BodyVision/
├── backend/                          # Backend FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app
│   │   ├── config.py                 # Configurações
│   │   │
│   │   ├── core/                     # Motor de Visão Computacional
│   │   │   ├── __init__.py
│   │   │   ├── cv_service.py         # Serviço principal CV (refatorado de app.py)
│   │   │   ├── pose_detector.py      # (movido de bodyvision/pose_evaluator.py)
│   │   │   ├── ml_evaluator.py       # (movido de bodyvision/ml_evaluator.py)
│   │   │   └── frame_processor.py    # Processamento de frames
│   │   │
│   │   ├── api/                      # Rotas da API
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── pose.py           # Endpoints de pose
│   │   │   │   ├── data.py           # Endpoints de coleta
│   │   │   │   └── websocket.py      # WebSocket handler
│   │   │
│   │   ├── models/                   # Modelos Pydantic
│   │   │   ├── __init__.py
│   │   │   ├── pose.py               # Schemas de pose
│   │   │   └── evaluation.py         # Schemas de avaliação
│   │   │
│   │   └── services/                 # Serviços de negócio
│   │       ├── __init__.py
│   │       ├── session_manager.py    # Gerencia sessões
│   │       └── data_collection.py    # (movido de bodyvision/data_collector.py)
│   │
│   ├── requirements.txt
│   └── Dockerfile
│
├── interface/                        # App Flutter
│   ├── lib/
│   │   ├── main.dart
│   │   ├── app.dart
│   │   │
│   │   ├── data/                     # Camada de dados
│   │   │   ├── models/               # Modelos Dart
│   │   │   ├── repositories/         # Repositórios
│   │   │   └── api/                  # Cliente HTTP/WebSocket
│   │   │       ├── api_client.dart
│   │   │       └── websocket_client.dart
│   │   │
│   │   ├── presentation/             # UI
│   │   │   ├── screens/
│   │   │   │   └── camera_screen.dart
│   │   │   ├── widgets/
│   │   │   │   ├── camera_view.dart
│   │   │   │   ├── pose_selector.dart
│   │   │   │   ├── feedback_panel.dart
│   │   │   │   └── skeleton_overlay.dart
│   │   │   └── providers/            # State management
│   │   │       └── pose_provider.dart
│   │   │
│   │   └── core/
│   │       ├── config.dart
│   │       └── theme.dart
│   │
│   ├── pubspec.yaml
│   └── README.md
│
├── treinamento/                      # Scripts de ML
│   ├── export_training_data.py       # (movido de scripts/)
│   ├── train_model.py                # (movido de scripts/)
│   └── README.md
│
├── bodyvision/                       # LEGADO (manter temporariamente)
│   └── ...                           # Código antigo (será removido após migração)
│
├── data_collected/                   # Dados coletados (compartilhado)
├── models/                           # Modelos ML (compartilhado)
│
├── docs/                             # Documentação
└── README.md
```

---

## 📝 Passo a Passo da Refatoração

### **PASSO 1: Criar Estrutura Base** ⏱️ ~1 hora

```bash
# Criar pastas
mkdir -p backend/app/{core,api/v1,models,services}
mkdir -p interface/lib/{data/{models,repositories,api},presentation/{screens,widgets,providers},core}
mkdir -p treinamento
```

**Arquivos iniciais:**
- `backend/app/__init__.py`
- `backend/requirements.txt`
- `interface/pubspec.yaml`

---

### **PASSO 2: Mover Código CV para Backend** ⏱️ ~2 horas

#### 2.1 Mover `pose_evaluator.py`

```bash
cp bodyvision/pose_evaluator.py backend/app/core/pose_detector.py
```

**Ajustes necessários:**
- Renomear `PoseDetector` se necessário
- Ajustar imports

#### 2.2 Mover `ml_evaluator.py` e `data_collector.py`

```bash
cp bodyvision/ml_evaluator.py backend/app/core/ml_evaluator.py
cp bodyvision/data_collector.py backend/app/services/data_collection.py
```

#### 2.3 Criar `CVService` (refatorado de `app.py`)

Extrair métodos de `BodyVisionApp`:
- `process_frame()` → `CVService.process_frame()`
- `_evaluate_pose()` → `CVService.evaluate_pose()`

**Exemplo:**
```python
# backend/app/core/cv_service.py
from .pose_detector import PoseDetector
from .ml_evaluator import MLEvaluator

class CVService:
    def __init__(self):
        self.detector = PoseDetector()
        self.ml_evaluator = MLEvaluator()
    
    def process_frame(self, frame, pose_mode, camera_width):
        # Lógica extraída de BodyVisionApp.process_frame()
        # Retorna: frame_annotated, pose_quality, landmarks
        pass
```

---

### **PASSO 3: Criar API FastAPI** ⏱️ ~3 horas

#### 3.1 Modelos Pydantic

```python
# backend/app/models/pose.py
from pydantic import BaseModel
from typing import Literal, Optional, List

class LandmarkPoint(BaseModel):
    x: float
    y: float
    z: float
    visibility: Optional[float] = None

class PoseEvaluateRequest(BaseModel):
    image: str  # Base64
    pose_mode: Literal["double_biceps", "back_double_biceps", "side_chest", "most_muscular", "enquadramento"]
    session_id: Optional[str] = None

class PoseEvaluateResponse(BaseModel):
    pose_quality: str
    status: Literal["correct", "incorrect", "adjustment_needed", "no_detection"]
    landmarks: List[LandmarkPoint]
    annotated_image: str  # Base64
    processing_time_ms: int
```

#### 3.2 Endpoints REST

```python
# backend/app/api/v1/pose.py
from fastapi import APIRouter, HTTPException
from app.models.pose import PoseEvaluateRequest, PoseEvaluateResponse
from app.core.cv_service import CVService

router = APIRouter()
cv_service = CVService()

@router.post("/evaluate", response_model=PoseEvaluateResponse)
async def evaluate_pose(request: PoseEvaluateRequest):
    # Decodifica imagem
    # Chama cv_service.process_frame()
    # Retorna resposta
    pass
```

#### 3.3 WebSocket Handler

```python
# backend/app/api/v1/websocket.py
from fastapi import WebSocket
from app.core.cv_service import CVService

async def pose_stream(websocket: WebSocket, pose_mode: str):
    await websocket.accept()
    cv_service = CVService()
    
    while True:
        data = await websocket.receive_json()
        if data["type"] == "frame":
            result = cv_service.process_frame(...)
            await websocket.send_json({
                "type": "evaluation",
                "data": result
            })
```

#### 3.4 FastAPI Main

```python
# backend/app/main.py
from fastapi import FastAPI
from app.api.v1 import pose, websocket

app = FastAPI(title="BodyVision API")

app.include_router(pose.router, prefix="/api/v1/pose", tags=["pose"])
# WebSocket será adicionado depois
```

---

### **PASSO 4: Criar App Flutter Básico** ⏱️ ~4 horas

#### 4.1 Setup Flutter

```bash
cd interface
flutter create .
flutter pub add http web_socket_channel camera provider
```

#### 4.2 Cliente API

```dart
// interface/lib/data/api/api_client.dart
class ApiClient {
  final String baseUrl = 'http://localhost:8000';
  
  Future<EvaluationResponse> evaluatePose(String imageBase64, String poseMode) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/v1/pose/evaluate'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'image': imageBase64,
        'pose_mode': poseMode,
      }),
    );
    return EvaluationResponse.fromJson(jsonDecode(response.body));
  }
}
```

#### 4.3 Cliente WebSocket

```dart
// interface/lib/data/api/websocket_client.dart
class WebSocketClient {
  WebSocketChannel? _channel;
  
  Stream<Map<String, dynamic>> connect(String poseMode) {
    _channel = WebSocketChannel.connect(
      Uri.parse('ws://localhost:8000/ws/pose/stream?pose_mode=$poseMode'),
    );
    return _channel!.stream.map((data) => jsonDecode(data));
  }
  
  void sendFrame(String imageBase64) {
    _channel?.sink.add(jsonEncode({
      'type': 'frame',
      'data': {'image': imageBase64},
    }));
  }
}
```

#### 4.4 Tela Principal

```dart
// interface/lib/presentation/screens/camera_screen.dart
class CameraScreen extends StatefulWidget {
  @override
  _CameraScreenState createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  CameraController? _controller;
  WebSocketClient? _wsClient;
  
  @override
  void initState() {
    super.initState();
    _initCamera();
    _initWebSocket();
  }
  
  void _processFrame() async {
    final image = await _controller!.takePicture();
    final imageBytes = await File(image.path).readAsBytes();
    final base64Image = base64Encode(imageBytes);
    
    _wsClient?.sendFrame(base64Image);
  }
  
  // ... resto da implementação
}
```

---

### **PASSO 5: Remover Código Kivy** ⏱️ ~1 hora

```bash
# Remover arquivos Kivy
rm -rf bodyvision/gui/
rm bodyvision/ui_renderer.py
rm bodyvision/ui_helpers.py
rm bodyvision/text_renderer.py
rm run_kivy.py

# Remover de requirements.txt
# kivy e kivymd
```

**Atualizar `requirements.txt` do backend:**
```
fastapi
uvicorn[standard]
opencv-python
mediapipe
numpy
scikit-learn
joblib
Pillow
pydantic
python-multipart
```

---

### **PASSO 6: Testes e Validação** ⏱️ ~2 horas

1. **Testar Backend:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   # Testar endpoints com curl ou Postman
   ```

2. **Testar Flutter:**
   ```bash
   cd interface
   flutter run
   ```

3. **Validar Resultados:**
   - Comparar resultados com sistema antigo
   - Verificar performance (latência < 150ms)
   - Validar todas as poses

---

### **PASSO 7: Otimizações** ⏱️ ~2 horas

1. **Compressão de Imagens**
   - Redimensionar antes de enviar
   - JPEG quality 75-85%

2. **Cache**
   - Cache de modelos ML em memória
   - Cache de resultados

3. **Assíncrono**
   - Processamento assíncrono no backend
   - Queue de frames

---

## 🔀 Estratégia de Comunicação

### **Opção 1: WebSocket (Recomendado para Tempo Real)**

**Vantagens:**
- ✅ Baixa latência
- ✅ Conexão persistente
- ✅ Bidirecional
- ✅ Ideal para stream contínuo

**Uso:**
- Flutter envia frames via WebSocket
- Backend retorna avaliação imediata
- Atualização contínua da UI

### **Opção 2: REST (Alternativa Simples)**

**Vantagens:**
- ✅ Simples de implementar
- ✅ Fácil debug
- ✅ Cacheável

**Desvantagens:**
- ❌ Overhead de HTTP
- ❌ Latência maior

**Recomendação:** Usar WebSocket para stream principal, REST para ações pontuais (trocar pose, coletar dados).

---

## ⚡ Performance em Tempo Real

### Otimizações no Backend:

1. **Compressão de Imagens**
   ```python
   # Redimensionar antes de processar
   frame_resized = cv2.resize(frame, (640, 480))
   ```

2. **Processamento Assíncrono**
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   executor = ThreadPoolExecutor(max_workers=4)
   ```

3. **Cache de Modelos**
   ```python
   # Carregar modelos uma vez na inicialização
   ml_evaluator = MLEvaluator()  # Singleton
   ```

### Otimizações no Flutter:

1. **Throttling de Frames**
   ```dart
   Timer.periodic(Duration(milliseconds: 33), (timer) {
     // Envia frame (30 FPS)
   });
   ```

2. **Compressão**
   ```dart
   final resized = await resizeImage(imageBytes, width: 640);
   final compressed = await compressImage(resized, quality: 80);
   ```

---

## ✅ Checklist Final

- [ ] Estrutura de pastas criada
- [ ] Código CV movido para backend
- [ ] CVService criado e testado
- [ ] API FastAPI implementada
- [ ] Endpoints REST funcionando
- [ ] WebSocket implementado
- [ ] App Flutter básico funcionando
- [ ] Camera integrada no Flutter
- [ ] WebSocket conectando corretamente
- [ ] Feedback visual funcionando
- [ ] Código Kivy removido
- [ ] Testes de performance (< 150ms)
- [ ] Validação de resultados idênticos ao sistema antigo
- [ ] Documentação atualizada

---

## 🚀 Próximos Passos Imediatos

1. **Criar estrutura de pastas**
2. **Mover código CV para backend**
3. **Implementar CVService**
4. **Criar API FastAPI básica**
5. **Testar backend isoladamente**
6. **Criar app Flutter básico**
7. **Integrar câmera no Flutter**
8. **Conectar Flutter com backend**

---

**Documento v1.0** - Plano de Refatoração Completo

