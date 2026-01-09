# 🏗️ Arquitetura Profissional - BodyVision

## Visão Geral da Arquitetura

O BodyVision será migrado para uma arquitetura moderna, escalável e preparada para monetização, separando claramente as responsabilidades entre interface, lógica de negócio e processamento de visão computacional.

## 🎯 Stack Tecnológica

### Frontend: **Flutter (Dart)**
- ✅ Cross-platform (iOS, Android, Web, Desktop)
- ✅ Performance nativa
- ✅ UI/UX moderna e fluida
- ✅ Suporte a câmera nativo
- ✅ Hot reload para desenvolvimento rápido
- ✅ Ecossistema maduro para apps comerciais

### Backend: **FastAPI (Python)**
- ✅ API REST moderna e assíncrona
- ✅ Validação automática com Pydantic
- ✅ Documentação automática (OpenAPI/Swagger)
- ✅ WebSocket para comunicação em tempo real
- ✅ Performance excelente (comparable a Node.js)
- ✅ Integração perfeita com código Python existente

### Visão Computacional: **Python (Módulo Isolado)**
- ✅ Mantém OpenCV + MediaPipe (código atual)
- ✅ Isolado como serviço interno
- ✅ Processamento assíncrono
- ✅ Possibilidade de GPU/CUDA no futuro

## 📐 Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Flutter)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   UI Layer   │  │ State Mgmt   │  │  Camera API  │  │
│  │   (Widgets)  │  │  (Provider/  │  │   (Native)   │  │
│  │              │  │   Bloc)      │  │              │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │           │
│         └─────────────────┼──────────────────┘           │
│                           │                              │
└───────────────────────────┼──────────────────────────────┘
                            │
                            │ HTTP/WebSocket
                            │
┌───────────────────────────▼──────────────────────────────┐
│              BACKEND API (FastAPI)                        │
│  ┌────────────────────────────────────────────────────┐  │
│  │           API Routes Layer                         │  │
│  │  - /api/v1/pose/evaluate                           │  │
│  │  - /api/v1/pose/select                             │  │
│  │  - /api/v1/data/collect                            │  │
│  │  - /api/v1/session/start                           │  │
│  │  - /ws (WebSocket para stream)                     │  │
│  └──────────────────┬─────────────────────────────────┘  │
│                     │                                     │
│  ┌──────────────────▼─────────────────────────────────┐  │
│  │         Business Logic Layer                       │  │
│  │  - Pose Session Manager                            │  │
│  │  - Data Collection Service                         │  │
│  │  - ML Model Manager                                │  │
│  │  - Statistics Service                              │  │
│  └──────────────────┬─────────────────────────────────┘  │
│                     │                                     │
└─────────────────────┼─────────────────────────────────────┘
                      │
                      │ Internal Calls
                      │
┌─────────────────────▼─────────────────────────────────────┐
│      VISÃO COMPUTACIONAL (Python Module)                  │
│  ┌────────────────────────────────────────────────────┐  │
│  │      CV Service (Reaproveita código atual)         │  │
│  │  - PoseDetector (MediaPipe)                        │  │
│  │  - PoseEvaluator (Lógica de avaliação)            │  │
│  │  - MLEvaluator (Modelos treinados)                │  │
│  │  - Frame Processor                                 │  │
│  └────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              PERSISTÊNCIA                                │
│  - SQLite/PostgreSQL (sessões, estatísticas)           │
│  - Sistema de arquivos (dados coletados, modelos)      │
└─────────────────────────────────────────────────────────┘
```

## 🔄 Fluxo de Dados (Tempo Real)

### Modo Stream (WebSocket - Recomendado)
```
1. Flutter captura frame da câmera (nativo)
2. Flutter envia frame via WebSocket para FastAPI
3. FastAPI recebe e enfileira processamento
4. FastAPI chama CV Service (processamento assíncrono)
5. CV Service retorna:
   - Frame anotado (com esqueleto)
   - Avaliação (qualidade, feedback)
   - Landmarks normalizados
6. FastAPI envia resposta via WebSocket
7. Flutter recebe e atualiza UI instantaneamente
```

### Modo REST (Alternativa para latência não crítica)
```
1. Flutter captura frame
2. Flutter envia POST /api/v1/pose/evaluate
3. Backend processa e retorna JSON
4. Flutter renderiza resultado
```

## 📦 Estrutura de Pastas Proposta

```
BodyVision/
├── backend/                          # Backend FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app principal
│   │   ├── config.py                 # Configurações
│   │   ├── dependencies.py           # Injeção de dependências
│   │   │
│   │   ├── api/                      # Rotas da API
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── pose.py           # Endpoints de pose
│   │   │   │   ├── data.py           # Endpoints de coleta
│   │   │   │   ├── session.py        # Gerenciamento de sessões
│   │   │   │   └── websocket.py      # WebSocket handlers
│   │   │   └── dependencies.py       # Dependencies das rotas
│   │   │
│   │   ├── core/                     # Módulo de visão computacional
│   │   │   ├── __init__.py
│   │   │   ├── cv_service.py         # Serviço principal CV
│   │   │   ├── pose_detector.py      # (Move de bodyvision/)
│   │   │   ├── pose_evaluator.py     # (Move de bodyvision/)
│   │   │   ├── ml_evaluator.py       # (Move de bodyvision/)
│   │   │   └── frame_processor.py    # Processamento de frames
│   │   │
│   │   ├── services/                 # Lógica de negócio
│   │   │   ├── __init__.py
│   │   │   ├── pose_session.py       # Gerencia sessões de pose
│   │   │   ├── data_collection.py    # Gerencia coleta de dados
│   │   │   ├── statistics.py         # Estatísticas e métricas
│   │   │   └── model_manager.py      # Carrega/gerencia modelos ML
│   │   │
│   │   ├── models/                   # Modelos Pydantic
│   │   │   ├── __init__.py
│   │   │   ├── pose.py               # Schemas de pose
│   │   │   ├── evaluation.py         # Schemas de avaliação
│   │   │   ├── data.py               # Schemas de dados
│   │   │   └── session.py            # Schemas de sessão
│   │   │
│   │   └── utils/                    # Utilitários
│   │       ├── __init__.py
│   │       ├── image_utils.py        # Utilitários de imagem
│   │       └── validation.py         # Validações
│   │
│   ├── tests/                        # Testes do backend
│   ├── alembic/                      # Migrations (se usar DB)
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                         # App Flutter
│   ├── lib/
│   │   ├── main.dart
│   │   ├── app.dart
│   │   │
│   │   ├── core/                     # Configurações core
│   │   │   ├── config.dart
│   │   │   ├── theme.dart
│   │   │   └── constants.dart
│   │   │
│   │   ├── data/                     # Camada de dados
│   │   │   ├── models/               # Modelos Dart
│   │   │   ├── repositories/         # Repositórios
│   │   │   └── api/                  # Cliente HTTP/WebSocket
│   │   │       ├── api_client.dart
│   │   │       └── websocket_client.dart
│   │   │
│   │   ├── domain/                   # Lógica de domínio
│   │   │   ├── entities/             # Entidades
│   │   │   └── usecases/             # Casos de uso
│   │   │
│   │   ├── presentation/             # UI e estado
│   │   │   ├── screens/              # Telas principais
│   │   │   │   ├── camera_screen.dart
│   │   │   │   ├── evaluation_screen.dart
│   │   │   │   └── settings_screen.dart
│   │   │   ├── widgets/              # Widgets reutilizáveis
│   │   │   │   ├── camera_view.dart
│   │   │   │   ├── pose_selector.dart
│   │   │   │   ├── feedback_panel.dart
│   │   │   │   ├── skeleton_overlay.dart
│   │   │   │   └── metric_card.dart
│   │   │   └── providers/            # Gerenciamento de estado
│   │   │       ├── pose_provider.dart
│   │   │       ├── camera_provider.dart
│   │   │       └── session_provider.dart
│   │   │
│   │   └── utils/                    # Utilitários
│   │       ├── image_utils.dart
│   │       └── validators.dart
│   │
│   ├── assets/                       # Assets
│   │   ├── images/
│   │   └── fonts/
│   ├── test/                         # Testes
│   ├── pubspec.yaml
│   └── README.md
│
├── shared/                           # Código compartilhado (se necessário)
│   └── schemas/                      # Schemas compartilhados
│
├── bodyvision/                       # Código legado (manter durante migração)
│   └── ...                          # (será gradualmente movido para backend/core)
│
├── scripts/                          # Scripts utilitários
│   ├── export_training_data.py
│   └── train_model.py
│
├── models/                           # Modelos ML (compartilhado)
├── data_collected/                   # Dados coletados (compartilhado)
│
├── docs/                             # Documentação
│   ├── ARQUITETURA_PROFISSIONAL.md   # Este arquivo
│   ├── MIGRACAO_GRADUAL.md
│   ├── API_CONTRACTS.md
│   ├── UI_DESIGN_SYSTEM.md
│   └── DEPLOYMENT.md
│
├── docker-compose.yml                # Orquestração de serviços
├── .gitignore
└── README.md
```

## 🎨 Design de Interface (Conceitual)

### Layout Principal

```
┌──────────────────────────────────────────────────────────┐
│  ┌────────────┐  ┌──────────────────┐  ┌─────────────┐  │
│  │            │  │                  │  │             │  │
│  │  POSE      │  │                  │  │  AVALIAÇÃO  │  │
│  │  SELECTOR  │  │   CAMERA FEED    │  │             │  │
│  │  (Lista    │  │   + Skeleton     │  │  ┌───────┐  │  │
│  │  1-5)      │  │                  │  │  │Status │  │  │
│  │            │  │                  │  │  │ Verde │  │  │
│  │            │  │   [FPS: 30]      │  │  │Vermelho│  │  │
│  │            │  │                  │  │  └───────┘  │  │
│  │            │  │                  │  │             │  │
│  │            │  │                  │  │  Feedback:  │  │
│  │            │  │                  │  │  "Usuário   │  │
│  │            │  │                  │  │   bem       │  │
│  │            │  │                  │  │   centrali- │  │
│  │            │  │                  │  │   zado"     │  │
│  │            │  │                  │  │             │  │
│  │            │  │                  │  │  Métricas:  │  │
│  │            │  │                  │  │  • Simetria │  │
│  │            │  │                  │  │  • Ângulos  │  │
│  │            │  │                  │  │  • Postura  │  │
│  └────────────┘  └──────────────────┘  └─────────────┘  │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  INSTRUÇÕES                                         │ │
│  │  [V] POSE CORRETA  |  [X] POSE INCORRETA          │ │
│  └─────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

### Princípios de Design

1. **Hierarquia Visual Clara**
   - Câmera como elemento central
   - Informações secundárias nas laterais
   - Feedback destacado com cores semânticas

2. **Estados Visuais**
   - ✅ **Verde**: Pose correta (rgba(0, 128, 0, 0.3) no fundo + borda)
   - ❌ **Vermelho**: Pose incorreta (rgba(128, 0, 0, 0.3) no fundo + borda)
   - ⚠️ **Amarelo**: Ajuste necessário (rgba(255, 193, 7, 0.3))
   - ⚪ **Cinza**: Aguardando detecção

3. **Sobreposição de Esqueleto**
   - Linhas finas e suaves
   - Pontos visíveis mas discretos
   - Cores contrastantes com fundo
   - Opacidade ajustável

4. **Feedback Textual**
   - Sem textos redundantes ("FEEDBACK:", "AVALIAÇÃO:")
   - Mensagens diretas e objetivas
   - Hierarquia tipográfica clara
   - Animações sutis de transição

## 🔐 Responsabilidades por Camada

### Frontend (Flutter)
- ✅ Captura de vídeo da câmera
- ✅ Renderização de UI
- ✅ Gerenciamento de estado da aplicação
- ✅ Envio de frames para backend
- ✅ Exibição de feedback visual
- ✅ Interação do usuário
- ❌ Processamento de visão computacional
- ❌ Lógica de avaliação de poses

### Backend API (FastAPI)
- ✅ Validação de requisições
- ✅ Gerenciamento de sessões
- ✅ Orquestração de serviços
- ✅ Comunicação WebSocket
- ✅ Autenticação/autorização (futuro)
- ✅ Cache e otimizações
- ❌ Processamento pesado de CV

### Core CV (Python)
- ✅ Detecção de poses (MediaPipe)
- ✅ Avaliação de poses
- ✅ Processamento de frames
- ✅ Aplicação de modelos ML
- ✅ Cálculos de ângulos e métricas
- ❌ Interface com usuário
- ❌ Gerenciamento de estado da UI

## 📊 Performance e Escalabilidade

### Otimizações Planejadas

1. **Processamento Assíncrono**
   - Frames processados em background
   - Queue para evitar bloqueios
   - Pool de workers para paralelização

2. **Compressão de Dados**
   - JPEG quality ajustável (70-85%)
   - Redimensionamento antes de enviar
   - WebSocket com compressão

3. **Caching**
   - Cache de modelos ML em memória
   - Cache de resultados de avaliação
   - Redis para sessões (futuro)

4. **Limitação de Taxa**
   - Rate limiting por usuário
   - Throttling de frames (max 30 FPS)
   - Priorização de requisições

### Escalabilidade Futura

- Horizontal: Múltiplas instâncias do backend
- Vertical: GPU para processamento CV
- CDN: Servir assets estáticos
- Database: PostgreSQL para produção
- Message Queue: RabbitMQ/Kafka para processamento assíncrono

## 🚀 Próximos Passos

1. ✅ Documentação de arquitetura (este documento)
2. ⏳ Criar estrutura de pastas inicial
3. ⏳ Implementar contratos de API
4. ⏳ Criar estratégia de migração gradual
5. ⏳ Implementar design system de UI
6. ⏳ Setup de ambiente de desenvolvimento

---

**Documento v1.0** - Data: 2024
**Status**: Proposta inicial para revisão

