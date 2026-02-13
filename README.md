# ProPosing

Sistema de análise de poses de fisiculturismo em tempo real com visão computacional e Machine Learning.

---

## 📌 Visão Geral

O projeto é dividido em **dois componentes** que se comunicam via API REST:

1. **Backend** (Python/FastAPI) — Processa frames da câmera com MediaPipe, avalia poses e retorna landmarks e feedback
2. **Interface** (Flutter) — Exibe a câmera, envia frames para o backend e mostra o esqueleto + avaliação em tempo real

**Fluxo:** Câmera → Interface captura frame → Envia Base64 ao backend → Backend processa com MediaPipe → Retorna landmarks + status → Interface desenha overlay e feedback.

---

## ✅ Pré-requisitos

| Requisito | Uso |
|-----------|-----|
| **Python 3.10+** | Backend |
| **Flutter SDK** | Interface |
| **CocoaPods** | Interface macOS (`gem install cocoapods`) |
| **Chrome** | Para rodar na web |

---

## 📁 Estrutura do Projeto

```
ProPosing/
├── backend/                 # API REST - processamento de imagens
│   ├── app/
│   │   ├── main.py          # App FastAPI, rotas, CORS
│   │   ├── api/v1/pose.py   # Endpoints /api/v1/pose/evaluate e /select
│   │   ├── core/cv_service.py  # MediaPipe, regras de avaliação, ML
│   │   └── models/pose.py   # Schemas Pydantic (request/response)
│   ├── requirements.txt
│   └── run_standalone.py    # Launcher para app empacotado
│
├── interface/               # App Flutter
│   ├── lib/
│   │   ├── main.dart        # Entrada: escolhe CameraScreen ou CameraScreenMacOS
│   │   ├── core/            # AppTheme, AppColors, PoseConstants
│   │   ├── data/            # ApiClient, modelos (EvaluationResponse, etc.)
│   │   └── presentation/    # Screens (câmera), widgets (feedback, skeleton, pose selector)
│   ├── packages/camera_macos/  # Plugin patcheado para câmera no macOS
│   ├── macos/               # Config macOS (Info.plist, entitlements)
│   └── web/                 # index.html (Permissions-Policy para câmera)
│
├── proposing/               # Lógica de avaliação (usada pelo backend)
│   ├── pose_evaluator.py    # Regras geométricas por pose
│   ├── ml_evaluator.py      # Integração com modelos ML
│   ├── pose_metrics_loader.py  # Métricas da ml/pose_info
│   └── data_collector.py    # Coleta de dados para treino
│
├── treinamento/             # Scripts de ML
│   ├── train_model.py       # Treina modelos
│   ├── process_pose_info.py # Extrai métricas de .pages
│   ├── consolidate_training_data.py
│   └── README.md
│
├── ml/
│   ├── pose_info/           # Dados de referência (textos .pages e imagens)
│   ├── models/              # Modelos ML treinados (.pkl, gerados pelo train_model)
│   └── data/                # Dados coletados para treinamento
│
├── config/                  # Configurações de build
│   └── proposing_build.spec   # PyInstaller - empacotamento do backend
│
├── scripts/                 # Scripts de automação
│   ├── rodar_macos.sh       # Inicia backend + app macOS
│   ├── rodar_web.sh         # Inicia backend + app web (Chrome)
│   ├── parar_projeto.sh     # Para backend e Flutter
│   ├── iniciar_backend.sh   # Apenas backend
│   ├── build_executable.sh  # Gera ProPosing.app
│   └── limpar_flutter_macos.sh  # Limpa build (resolve CodeSign)
│
└── README.md
```

---

## 🚀 Como Rodar

**Execute os scripts a partir da raiz do projeto** (`ProPosing/`).

### macOS (app nativo)

```bash
./scripts/rodar_macos.sh
```

- Inicia o backend na porta 8000
- Roda o app Flutter em modo macOS
- Para parar: `Ctrl+C` ou, em outro terminal, `./scripts/parar_projeto.sh`

### Web (Chrome)

```bash
./scripts/rodar_web.sh
```

- Inicia o backend se não estiver rodando
- Abre o app no Chrome
- A câmera requer localhost ou HTTPS

### Parar tudo

```bash
./scripts/parar_projeto.sh
```

### Apenas backend (para testes de API)

```bash
./scripts/iniciar_backend.sh
```

API: `http://localhost:8000` | Docs: `http://localhost:8000/docs`

---

## 🔄 Funcionamento Técnico

### Plataformas

| Plataforma | Câmera | Tela |
|------------|--------|------|
| **macOS** | `camera_macos` (plugin local em `packages/`) | `CameraScreenMacOS` |
| **Web, iOS, Android** | `camera` (plugin oficial) | `CameraScreen` |

O `main.dart` detecta a plataforma e usa a tela correspondente.

### API principal

- **POST /api/v1/pose/evaluate** — Recebe imagem Base64, retorna landmarks, status e feedback
- **POST /api/v1/pose/select** — Seleciona modo de pose (sem efeito no fluxo atual)

### Dependências principais

- **Backend:** FastAPI, OpenCV, MediaPipe, NumPy, scikit-learn
- **Interface:** Flutter, camera, camera_macos (path override local)

---

## 📦 Build para Distribuição

```bash
./scripts/build_executable.sh
```

Gera `build_app/ProPosing.app` — um único app que inicia backend e interface.

**Requisitos:** Python3, Flutter SDK, PyInstaller (`pip3 install pyinstaller`)

**Se der erro de CodeSign:** execute `./scripts/limpar_flutter_macos.sh` (ou rode a partir da raiz) e rode o build novamente.

---

## 📚 Treinamento e Dados de ML

- **ml/pose_info/** — Contém descrições (.pages) e imagens de referência por pose
- **ml/models/** — Armazena modelos `.pkl` gerados pelo treinamento
- **ml/data/** — Armazena dados coletados/processados para treinamento

```bash
cd treinamento
python3 process_pose_info.py    # Extrai métricas da ml/pose_info
python3 consolidate_training_data.py
python3 train_model.py          # Treina e salva em ml/models/
```

Consulte `treinamento/README.md` para mais detalhes.

---

## 🎮 Poses Suportadas

1. Enquadramento  
2. Duplo Bíceps  
3. Side Chest  
4. Side Triceps  
5. Most Muscular  

Atalhos 1–5 no teclado alternam entre as poses.

---

## 🔧 Troubleshooting

| Problema | Solução |
|----------|---------|
| Backend não conecta | `curl http://localhost:8000/health` — se falhar, rode `./scripts/iniciar_backend.sh` |
| Câmera não funciona na web | Use localhost ou HTTPS. Execute `./scripts/rodar_web.sh` e permita a câmera no navegador |
| Flutter não encontra backend | Web/desktop: localhost por padrão. Mobile: `flutter run --dart-define=API_HOST=192.168.x.x` |
| Erro CodeSign no build macOS | `./scripts/limpar_flutter_macos.sh` e depois `./scripts/build_executable.sh` |
| Câmera não inicia no macOS | Preferências do Sistema → Privacidade → Câmera — permitir para o app |

---

## 📖 Documentação Adicional

- `treinamento/README.md` — Treinamento básico
- `treinamento/README_TREINAMENTO_AVANCADO.md` — Web scraping e fluxos avançados
- `scripts/README.md` — Guia rápido dos scripts de automação
- `docs/REPO_ORGANIZATION.md` — Convenções de organização do repositório

---

**ProPosing** — Sistema de Análise de Poses de Fisiculturismo
