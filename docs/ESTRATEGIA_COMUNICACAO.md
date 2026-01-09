# 📡 Estratégia de Comunicação - Flutter ↔ FastAPI

## 📋 Opções de Comunicação

### **Opção 1: WebSocket (Recomendado para Tempo Real)**

**Quando usar:**
- ✅ Stream contínuo de frames
- ✅ Feedback em tempo real
- ✅ Baixa latência necessária

**Vantagens:**
- Conexão persistente (menos overhead)
- Bidirecional (cliente ↔ servidor)
- Ideal para 30 FPS
- Menor latência

**Desvantagens:**
- Mais complexo de implementar
- Requer gerenciamento de reconexão

#### Implementação:

**Backend (FastAPI):**
```python
@app.websocket("/ws/pose/stream")
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

**Flutter:**
```dart
final channel = WebSocketChannel.connect(
  Uri.parse('ws://localhost:8000/ws/pose/stream?pose_mode=$poseMode'),
);

channel.stream.listen((data) {
  final result = jsonDecode(data);
  // Atualiza UI
});

// Envia frame
channel.sink.add(jsonEncode({
  'type': 'frame',
  'data': {'image': base64Image},
}));
```

---

### **Opção 2: REST API (Alternativa Simples)**

**Quando usar:**
- ✅ Ações pontuais (trocar pose, coletar dados)
- ✅ Debug e desenvolvimento
- ✅ Latência não crítica

**Vantagens:**
- Simples de implementar
- Fácil debug
- Cacheável
- Stateless

**Desvantagens:**
- Overhead de HTTP
- Latência maior
- Não ideal para stream contínuo

#### Implementação:

**Backend:**
```python
@router.post("/evaluate")
async def evaluate_pose(request: PoseEvaluateRequest):
    result = cv_service.process_frame(...)
    return result
```

**Flutter:**
```dart
final response = await http.post(
  Uri.parse('$baseUrl/api/v1/pose/evaluate'),
  body: jsonEncode({
    'image': base64Image,
    'pose_mode': poseMode,
  }),
);
```

---

## 🎯 Estratégia Recomendada (Híbrida)

### **Uso Combinado:**

1. **WebSocket para Stream Principal**
   - Processamento de frames da câmera
   - Feedback contínuo
   - 30 FPS

2. **REST para Ações Pontuais**
   - Trocar modo de pose
   - Coletar dados
   - Configurações

### **Arquitetura:**

```
Flutter App
    │
    ├─ WebSocket ────────┐
    │                    │
    └─ REST API ─────────┤
                         │
                    FastAPI Backend
                         │
                    CV Service
```

---

## ⚡ Otimizações de Performance

### 1. **Compressão de Imagens**

**Flutter:**
```dart
// Redimensiona antes de enviar
final resized = await resizeImage(imageBytes, width: 640);
final compressed = await compressImage(resized, quality: 80);
final base64 = base64Encode(compressed);
```

**Backend:**
```python
# Redimensiona se necessário
if frame.shape[1] > 640:
    frame = cv2.resize(frame, (640, 480))
```

### 2. **Throttling de Frames**

**Flutter:**
```dart
Timer.periodic(Duration(milliseconds: 33), (timer) {
  // Envia frame (30 FPS)
  _sendFrame();
});
```

### 3. **Queue de Processamento**

**Backend:**
```python
from asyncio import Queue

frame_queue = Queue(maxsize=5)

async def process_queue():
    while True:
        frame_data = await frame_queue.get()
        result = cv_service.process_frame(...)
        await websocket.send_json(result)
```

### 4. **Cache de Modelos**

**Backend:**
```python
# Carrega modelos uma vez na inicialização
cv_service = CVService()  # Singleton
```

---

## 📊 Métricas de Performance Alvo

- **Latência:** < 150ms (frame → resposta)
- **FPS:** 30 FPS estável
- **Throughput:** ~30 frames/segundo
- **Tamanho de mensagem:** < 200KB por frame (comprimido)

---

## 🔄 Fluxo de Dados

### **WebSocket Stream:**

```
1. Flutter captura frame (30 FPS)
2. Flutter comprime e converte para Base64
3. Flutter envia via WebSocket
4. Backend recebe e processa
5. Backend retorna resultado via WebSocket
6. Flutter atualiza UI instantaneamente
```

### **REST Request:**

```
1. Flutter prepara requisição
2. Flutter envia POST /api/v1/pose/evaluate
3. Backend processa
4. Backend retorna JSON
5. Flutter atualiza UI
```

---

## 🛠️ Implementação Recomendada

### **Fase 1: REST Básico (MVP)**
- Implementar endpoints REST
- Testar funcionalidade básica
- Validar resultados

### **Fase 2: WebSocket (Otimização)**
- Adicionar WebSocket handler
- Migrar stream principal para WebSocket
- Manter REST para ações pontuais

### **Fase 3: Otimizações**
- Compressão de imagens
- Throttling e queue
- Cache e pooling

---

**Documento v1.0** - Estratégia de Comunicação

