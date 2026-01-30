# proPose - Sistema de Análise de Poses de Fisiculturismo

Sistema profissional de análise de poses de fisiculturismo em tempo real usando visão computacional e Machine Learning.

## 🏗️ Estrutura

```
BodyVision/
├── backend/          # FastAPI - Motor de visão computacional
├── interface/        # Flutter - Interface moderna
├── treinamento/      # Scripts de Machine Learning
└── bodyvision/       # Lógica de avaliação de poses
```

## 🚀 Início Rápido

### ⚡ Iniciar Tudo de Uma Vez (Recomendado)

```bash
./iniciar_projeto.sh
```

Este script:
- ✅ Verifica e instala dependências
- ✅ Inicia o backend automaticamente
- ✅ Inicia a interface Flutter
- ✅ Configura tudo para você

**Para parar tudo:**
```bash
./parar_projeto.sh
```

Ou use `Ctrl+C` no terminal onde rodou `iniciar_projeto.sh`

---

### 🔧 Início Manual (Alternativa)

#### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./iniciar_backend.sh
```

Servidor: `http://localhost:8000` | Docs: `http://localhost:8000/docs`

#### 2. Interface Flutter

```bash
cd interface
flutter pub get
flutter run
```

## 📚 Treinamento da IA

### Processar poseInfo (Textos e Imagens de Referência)
```bash
cd treinamento
python3 process_pose_info.py
```
Extrai métricas dos arquivos `.pages` e processa imagens de referência. As métricas são usadas automaticamente nas regras de avaliação.

### Consolidar e Treinar
```bash
cd treinamento
python3 consolidate_training_data.py
python3 train_model.py
```

Veja `treinamento/README.md` para mais opções (coleta manual, web scraping, etc.).

## 🎮 Poses Suportadas

1. **Enquadramento** - Centralização do usuário
2. **Duplo Bíceps**
3. **Side Chest**
4. **Side Triceps**
5. **Most Muscular**

## 📁 Componentes Principais

### Backend (`backend/`)
- `app/main.py` - Aplicação FastAPI
- `app/core/cv_service.py` - Motor de visão computacional
- `app/api/v1/pose.py` - Endpoints REST

### Interface (`interface/`)
- `lib/main.dart` - Aplicação Flutter
- `lib/presentation/` - UI e widgets

### Treinamento (`treinamento/`)
- `train_model.py` - Treina modelos ML
- `export_training_data.py` - Exporta dados coletados
- `image_processor.py` - Processa imagens/vídeos
- `web_scraper.py` - Coleta dados de artigos web
- `consolidate_training_data.py` - Consolida todas as fontes

### Lógica de Poses (`bodyvision/`)
- `pose_evaluator.py` - Regras de avaliação de cada pose
- `ml_evaluator.py` - Integração com modelos ML
- `data_collector.py` - Coleta e validação de dados

## 🔧 Dependências

### Backend
- FastAPI, OpenCV, MediaPipe, NumPy, scikit-learn, beautifulsoup4

### Interface
- Flutter SDK

## 🧪 Testar o Sistema

```bash
./testar_tudo.sh
```

Verifica estrutura, Flutter e conexão com backend.

## 🔧 Troubleshooting

### Backend não conecta
- Verifique se está rodando: `curl http://localhost:8000/health`
- Se usar Flutter Web, use `localhost` no `api_client.dart`
- Backend deve usar `--host 0.0.0.0` para aceitar conexões externas

### Flutter não encontra backend
- Edite `interface/lib/data/api/api_client.dart` com o IP correto
- Para web: use `http://localhost:8000`
- Para mobile: use seu IP local (ex: `http://192.168.0.134:8000`)

## 📖 Documentação Adicional

- `treinamento/README.md` - Guia de treinamento básico
- `treinamento/README_TREINAMENTO_AVANCADO.md` - Treinamento avançado com web scraping

---

**BodyVision** - Sistema Profissional de Análise de Poses
