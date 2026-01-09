# 📁 Estrutura Detalhada do Projeto BodyVision

> **Nota:** Para visão geral, veja [ORGANIZACAO.md](./ORGANIZACAO.md)

## 🗂️ Organização Atual

```
BodyVision/
├── backend/                    # ✅ Backend FastAPI (Python)
│   ├── app/
│   │   ├── main.py            # Aplicação FastAPI
│   │   ├── core/              # Motor de visão computacional
│   │   │   └── cv_service.py  # Serviço principal CV
│   │   ├── api/v1/            # Endpoints REST
│   │   │   └── pose.py        # Endpoints de pose
│   │   ├── models/            # Modelos Pydantic
│   │   │   └── pose.py
│   │   └── services/          # Serviços de negócio
│   ├── requirements.txt       # Dependências Python
│   ├── test_api.py           # Script de teste
│   └── start.sh              # Script de inicialização
│
├── interface/                  # ✅ Interface Flutter (Dart)
│   ├── lib/
│   │   ├── main.dart          # Entry point
│   │   ├── data/              # Camada de dados
│   │   │   └── api/           # Clientes HTTP
│   │   └── presentation/      # UI
│   │       ├── screens/       # Telas
│   │       └── widgets/       # Componentes
│   └── pubspec.yaml           # Dependências Flutter
│
├── treinamento/                # ✅ Scripts de ML
│   ├── export_training_data.py
│   ├── train_model.py
│   └── README.md
│
├── bodyvision/                 # ⚠️ LEGADO (temporário)
│   ├── pose_evaluator.py      # (usado pelo backend)
│   ├── ml_evaluator.py        # (usado pelo backend)
│   ├── data_collector.py      # (usado pelo backend)
│   └── camera_utils.py        # (usado pelo backend)
│
├── docs/                       # ✅ Documentação
│   ├── README.md              # Documentação principal
│   ├── PLANO_REFATORACAO.md   # Plano de migração
│   ├── API_CONTRACTS.md       # Contratos de API
│   └── ...
│
├── data_collected/             # 📊 Dados coletados (gerado)
├── models/                     # 🤖 Modelos ML (gerado)
│
├── README.md                   # Este arquivo
├── COMO_TESTAR.md             # Guia de testes
├── .gitignore                 # Arquivos ignorados
└── ESTRUTURA_PROJETO.md       # Este arquivo
```

## 📋 Descrição das Pastas

### ✅ **backend/** - Backend FastAPI
Contém toda a lógica de negócio e processamento de visão computacional.

**Principais arquivos:**
- `app/main.py` - Inicializa servidor FastAPI
- `app/core/cv_service.py` - Serviço principal de CV
- `app/api/v1/pose.py` - Endpoints REST

### ✅ **interface/** - App Flutter
Interface moderna para usuários finais.

**Principais arquivos:**
- `lib/main.dart` - Entry point da aplicação
- `lib/data/api/api_client.dart` - Cliente HTTP
- `lib/presentation/` - Telas e widgets

### ✅ **treinamento/** - Scripts ML
Scripts para exportar dados e treinar modelos.

### ⚠️ **bodyvision/** - Código Legado
Código original mantido temporariamente para compatibilidade com o backend.

**Será removido quando:**
- Todos os módulos forem migrados para `backend/app/core/`
- Backend não depender mais desses imports

### ✅ **docs/** - Documentação
Toda a documentação do projeto.

## 🧹 Arquivos Removidos

Os seguintes arquivos foram removidos (não são mais necessários):

- ❌ `run_kivy.py` - Entry point Kivy antigo
- ❌ `main.py` - Entry point antigo
- ❌ `bodyvision/gui/` - Interface Kivy
- ❌ `bodyvision/ui_renderer.py` - Renderização UI antiga
- ❌ `bodyvision/ui_helpers.py` - Helpers de UI antiga
- ❌ `bodyvision/text_renderer.py` - Renderização de texto antiga
- ❌ `bodyvision/app.py` - Loop principal antigo
- ❌ `scripts/` - Movido para `treinamento/`

## 📊 Pastas Geradas (não versionadas)

Estas pastas são geradas automaticamente e ignoradas pelo git:

- `__pycache__/` - Bytecode Python
- `venv/` - Ambientes virtuais
- `data_collected/` - Dados coletados
- `models/*.pkl` - Modelos treinados
- `interface/build/` - Build do Flutter
- `interface/flutter/` - SDK Flutter

## 🔄 Fluxo de Dados

```
Interface (Flutter)
    ↓ HTTP/WebSocket
Backend (FastAPI)
    ↓ Importa
bodyvision/ (Legado)
    ↓ Usa
OpenCV + MediaPipe
```

## 🎯 Próximas Mudanças

1. **Migrar módulos de `bodyvision/` para `backend/app/core/`**
2. **Remover pasta `bodyvision/` completamente**
3. **Implementar WebSocket no backend**
4. **Completar interface Flutter**

---

**Última atualização:** Após limpeza e organização

