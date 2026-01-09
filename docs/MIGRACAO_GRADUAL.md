# 🔄 Estratégia de Migração Gradual - BodyVision

## 📌 Princípio: Migração Incremental Sem Quebrar o Sistema

A migração será feita em fases, garantindo que o sistema atual continue funcional enquanto construímos a nova arquitetura.

---

## 🎯 Fases da Migração

### **FASE 1: Preparação e Estrutura Base** ⏱️ ~1-2 semanas

**Objetivo**: Criar estrutura de pastas e setup básico sem afetar código existente.

#### Tarefas:

1. ✅ Criar estrutura de pastas (`backend/`, `frontend/`)
2. ✅ Setup inicial do FastAPI (`backend/app/main.py`)
3. ✅ Setup inicial do Flutter (`frontend/`)
4. ✅ Docker para desenvolvimento
5. ✅ Documentação de arquitetura

#### Estrutura Criada:

```
BodyVision/
├── backend/              # NOVO
│   └── app/
│       └── main.py      # FastAPI básico
├── frontend/             # NOVO (Flutter)
│   └── lib/
│       └── main.dart    # App Flutter básico
├── bodyvision/          # EXISTENTE (mantido intacto)
└── ...
```

#### Critério de Sucesso:
- ✅ Backend responde em `http://localhost:8000`
- ✅ Flutter app compila e roda
- ✅ Código existente continua funcionando

---

### **FASE 2: Backend API - Serviço de Visão Computacional** ⏱️ ~2-3 semanas

**Objetivo**: Extrair e expor lógica de CV como serviço isolado.

#### Tarefas:

1. **Mover módulos CV para `backend/app/core/`**
   - `pose_evaluator.py` → `backend/app/core/pose_evaluator.py`
   - `ml_evaluator.py` → `backend/app/core/ml_evaluator.py`
   - Adaptar imports

2. **Criar `CVService` wrapper**
   - `backend/app/core/cv_service.py`
   - Encapsula `PoseDetector` e `PoseEvaluator`
   - Interface limpa para API

3. **Implementar endpoint básico**
   - `POST /api/v1/pose/evaluate`
   - Recebe imagem base64
   - Retorna avaliação JSON
   - Testes unitários

#### Exemplo de Código:

```python
# backend/app/core/cv_service.py
from typing import Dict, Any
import base64
import cv2
import numpy as np
from .pose_evaluator import PoseDetector

class CVService:
    def __init__(self):
        self.detector = PoseDetector()
    
    def evaluate_frame(self, image_base64: str, pose_mode: str) -> Dict[str, Any]:
        # Decodifica imagem
        image_bytes = base64.b64decode(image_base64)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Processa (reaproveita lógica existente)
        # ... código do bodyvision/app.py adaptado ...
        
        return {
            "pose_quality": "...",
            "status": "correct",
            "landmarks": {...},
            "metrics": {...}
        }
```

```python
# backend/app/api/v1/pose.py
from fastapi import APIRouter
from app.models.pose import PoseEvaluateRequest, EvaluationResponse
from app.core.cv_service import CVService

router = APIRouter()
cv_service = CVService()

@router.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_pose(request: PoseEvaluateRequest):
    result = cv_service.evaluate_frame(request.image, request.pose_mode)
    return EvaluationResponse(**result)
```

#### Testes:

```bash
# Testar endpoint
curl -X POST http://localhost:8000/api/v1/pose/evaluate \
  -H "Content-Type: application/json" \
  -d '{"image": "base64...", "pose_mode": "double_biceps"}'
```

#### Critério de Sucesso:
- ✅ Endpoint funciona e retorna JSON válido
- ✅ Resultados idênticos ao sistema atual
- ✅ Performance aceitável (< 100ms por frame)

---

### **FASE 3: WebSocket para Stream em Tempo Real** ⏱️ ~1-2 semanas

**Objetivo**: Comunicação em tempo real entre Flutter e backend.

#### Tarefas:

1. **Implementar WebSocket handler**
   - `backend/app/api/v1/websocket.py`
   - Recebe frames via WebSocket
   - Retorna resultados em tempo real

2. **Otimizações**
   - Queue de processamento assíncrono
   - Compressão de imagens
   - Throttling de FPS

#### Exemplo:

```python
# backend/app/api/v1/websocket.py
from fastapi import WebSocket
import asyncio
from app.core.cv_service import CVService

async def pose_stream(websocket: WebSocket, session_id: str, pose_mode: str):
    await websocket.accept()
    cv_service = CVService()
    
    while True:
        data = await websocket.receive_json()
        
        if data["type"] == "frame":
            # Processa frame
            result = cv_service.evaluate_frame(data["data"]["image"], pose_mode)
            
            # Envia resultado
            await websocket.send_json({
                "type": "evaluation",
                "data": result
            })
```

#### Critério de Sucesso:
- ✅ WebSocket funciona
- ✅ Latência < 150ms (30 FPS possível)
- ✅ Estável por sessões longas

---

### **FASE 4: Frontend Flutter - UI Básica** ⏱️ ~2-3 semanas

**Objetivo**: Criar interface Flutter funcional conectada ao backend.

#### Tarefas:

1. **Configurar cliente HTTP/WebSocket**
   - `frontend/lib/data/api/api_client.dart`
   - `frontend/lib/data/api/websocket_client.dart`

2. **Implementar widgets básicos**
   - Camera view (usando `camera` package)
   - Pose selector (lista de poses)
   - Feedback panel (mostra resultados)

3. **Tela principal**
   - Layout responsivo
   - Integração com backend via WebSocket

#### Estrutura Flutter:

```
frontend/lib/
├── data/
│   ├── api/
│   │   ├── api_client.dart
│   │   └── websocket_client.dart
│   └── models/
│       ├── pose.dart
│       └── evaluation.dart
├── presentation/
│   ├── screens/
│   │   └── camera_screen.dart
│   └── widgets/
│       ├── camera_view.dart
│       ├── pose_selector.dart
│       └── feedback_panel.dart
└── main.dart
```

#### Critério de Sucesso:
- ✅ Interface funcional
- ✅ Conecta ao backend
- ✅ Mostra feedback em tempo real
- ✅ Performance fluida (30 FPS UI)

---

### **FASE 5: Design System e UI Moderna** ⏱️ ~2 semanas

**Objetivo**: Aplicar design profissional e melhorar UX.

#### Tarefas:

1. **Design System**
   - Cores, tipografia, espaçamentos
   - Componentes reutilizáveis
   - Animações e transições

2. **Melhorias de UI**
   - Feedback visual claro (verde/vermelho)
   - Overlay de esqueleto otimizado
   - Métricas visuais (gráficos, badges)

3. **Responsividade**
   - Tablet e desktop
   - Orientação portrait/landscape

#### Critério de Sucesso:
- ✅ Interface profissional e moderna
- ✅ UX intuitiva
- ✅ Feedback visual claro
- ✅ Design consistente

---

### **FASE 6: Funcionalidades Avançadas** ⏱️ ~2-3 semanas

**Objetivo**: Adicionar features para produto comercial.

#### Tarefas:

1. **Sistema de Sessões**
   - Gerenciamento de sessões
   - Histórico de avaliações
   - Estatísticas por sessão

2. **Coleta de Dados**
   - Endpoint `/api/v1/data/collect`
   - Integração no Flutter
   - Validações de qualidade

3. **Otimizações**
   - Cache de modelos ML
   - Compressão de imagens
   - Pool de workers

#### Critério de Sucesso:
- ✅ Todas features do sistema atual funcionam
- ✅ Performance otimizada
- ✅ Pronto para uso em produção

---

### **FASE 7: Migração Completa e Depreciação** ⏱️ ~1 semana

**Objetivo**: Finalizar migração e descontinuar código legado.

#### Tarefas:

1. **Testes finais**
   - Testes de integração
   - Testes de carga
   - Testes de usuário

2. **Documentação**
   - Guias de uso
   - Documentação de API
   - README atualizado

3. **Depreciação**
   - Marcar código legado como deprecated
   - Manter por compatibilidade temporária
   - Plano de remoção futura

#### Critério de Sucesso:
- ✅ Sistema novo funcional e testado
- ✅ Documentação completa
- ✅ Pronto para produção

---

## 🔀 Estratégia de Coexistência

Durante a migração, ambos sistemas podem coexistir:

```
┌─────────────────┐
│  Sistema Atual  │  (bodyvision/, main.py)
│  Python + Kivy  │  → Continua funcional
└─────────────────┘

┌─────────────────┐
│  Sistema Novo   │  (backend/, frontend/)
│  Flutter + API  │  → Desenvolvimento paralelo
└─────────────────┘
```

### Vantagens:

1. **Zero Downtime**: Sistema atual continua funcionando
2. **Testes Paralelos**: Comparar resultados lado a lado
3. **Rollback Fácil**: Se algo der errado, volta para o atual
4. **Migração Gradual**: Usuários podem migrar quando quiserem

---

## 📊 Checklist de Migração por Fase

### Fase 1: Preparação
- [ ] Criar `backend/` e `frontend/`
- [ ] Setup FastAPI básico
- [ ] Setup Flutter básico
- [ ] Docker compose
- [ ] Documentação

### Fase 2: Backend CV
- [ ] Mover módulos CV
- [ ] Criar `CVService`
- [ ] Endpoint `/api/v1/pose/evaluate`
- [ ] Testes unitários
- [ ] Validação de resultados

### Fase 3: WebSocket
- [ ] Handler WebSocket
- [ ] Queue de processamento
- [ ] Otimizações de performance
- [ ] Testes de carga

### Fase 4: Flutter Básico
- [ ] Cliente API/WebSocket
- [ ] Camera view
- [ ] Feedback panel
- [ ] Integração funcional

### Fase 5: Design System
- [ ] Cores e tipografia
- [ ] Componentes reutilizáveis
- [ ] Animações
- [ ] Responsividade

### Fase 6: Features Avançadas
- [ ] Sistema de sessões
- [ ] Coleta de dados
- [ ] Otimizações
- [ ] Testes finais

### Fase 7: Finalização
- [ ] Testes completos
- [ ] Documentação
- [ ] Depreciação código legado
- [ ] Release

---

## 🚨 Pontos de Atenção

### 1. Compatibilidade de Resultados

Durante a migração, garantir que resultados sejam idênticos:

```python
# Script de validação
def compare_results(old_result, new_result):
    assert old_result["pose_quality"] == new_result["pose_quality"]
    assert old_result["status"] == new_result["status"]
    # ... mais validações
```

### 2. Performance

Monitorar métricas:
- Latência de processamento
- Uso de CPU/Memória
- Taxa de FPS
- Taxa de erro

### 3. Dados Coletados

Garantir que dados coletados no sistema novo sejam compatíveis com scripts de treinamento existentes.

### 4. Modelos ML

Modelos treinados devem funcionar no novo sistema sem retreinamento.

---

## 📅 Timeline Estimada

| Fase | Duração | Total Acumulado |
|------|---------|-----------------|
| Fase 1 | 1-2 semanas | 1-2 semanas |
| Fase 2 | 2-3 semanas | 3-5 semanas |
| Fase 3 | 1-2 semanas | 4-7 semanas |
| Fase 4 | 2-3 semanas | 6-10 semanas |
| Fase 5 | 2 semanas | 8-12 semanas |
| Fase 6 | 2-3 semanas | 10-15 semanas |
| Fase 7 | 1 semana | 11-16 semanas |

**Total: ~3-4 meses** (desenvolvimento em tempo parcial)

---

## 🎯 Próximos Passos Imediatos

1. ✅ Revisar esta estratégia
2. ⏳ Iniciar Fase 1 (criar estrutura)
3. ⏳ Setup ambiente de desenvolvimento
4. ⏳ Começar migração do backend

---

**Documento v1.0** - Data: 2024
**Status**: Estratégia proposta para revisão e aprovação

