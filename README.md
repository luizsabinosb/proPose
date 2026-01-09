# BodyVision - Sistema de Análise de Poses de Fisiculturismo

Sistema profissional de análise de poses de fisiculturismo em tempo real usando visão computacional e Machine Learning.

## 🏗️ Arquitetura

O projeto está organizado em três partes principais:

```
BodyVision/
├── backend/          # FastAPI - Motor de visão computacional
├── interface/        # Flutter - Interface moderna (mobile/desktop/web)
└── treinamento/      # Scripts de Machine Learning
```

## 🚀 Início Rápido

### **1. Backend (Recomendado para começar)**

```bash
cd backend

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Iniciar servidor
uvicorn app.main:app --reload
```

**Servidor estará em:** `http://localhost:8000`
**Documentação:** `http://localhost:8000/docs`

### **2. Testar Backend**

```bash
cd backend
source venv/bin/activate
python test_api.py
```

### **3. Interface Flutter (Opcional)**

```bash
cd interface
flutter pub get
flutter run
```

**Nota:** O Flutter precisa estar instalado. Veja **[docs/INSTALAR_FLUTTER.md](docs/INSTALAR_FLUTTER.md)** se necessário.

## 📚 Documentação

### **Guias de Teste (Comece aqui!):**

- **[docs/TESTE_RAPIDO.md](docs/TESTE_RAPIDO.md)** - Teste rápido em 3 passos ⚡
- **[docs/COMO_TESTAR.md](docs/COMO_TESTAR.md)** - Guia completo de testes
- **[docs/TESTAR_SEM_FLUTTER.md](docs/TESTAR_SEM_FLUTTER.md)** - Testar só o backend

### **Documentação Técnica:**

- **[docs/README_REFATORACAO.md](docs/README_REFATORACAO.md)** - Guia completo de refatoração
- **[docs/PLANO_REFATORACAO.md](docs/PLANO_REFATORACAO.md)** - Plano detalhado da migração
- **[docs/API_CONTRACTS.md](docs/API_CONTRACTS.md)** - Documentação da API
- **[docs/ARQUITETURA_PROFISSIONAL.md](docs/ARQUITETURA_PROFISSIONAL.md)** - Arquitetura do sistema

### **Índice Completo:**

Consulte **[docs/INDICE.md](docs/INDICE.md)** para acessar toda a documentação.

## 📁 Estrutura do Projeto

### **Backend (`backend/`)**
- `app/main.py` - Aplicação FastAPI
- `app/core/` - Motor de visão computacional
- `app/api/` - Endpoints REST
- `app/models/` - Modelos Pydantic

### **Interface (`interface/`)**
- `lib/main.dart` - Aplicação Flutter
- `lib/data/` - Clientes de API
- `lib/presentation/` - UI e widgets

### **Treinamento (`treinamento/`)**
- Scripts para exportar dados e treinar modelos ML

### **Legado (`bodyvision/`)**
- Código original (mantido temporariamente para compatibilidade)
- Será removido após migração completa

## 🎯 Funcionalidades

- ✅ Detecção de poses em tempo real (MediaPipe)
- ✅ Avaliação automática de postura e simetria
- ✅ Feedback visual (verde/vermelho)
- ✅ Machine Learning para melhoria contínua
- ✅ API REST completa
- ✅ Interface moderna (Flutter)

## 🔧 Desenvolvimento

### **Adicionar Nova Funcionalidade:**

1. **Backend:** Adicione em `backend/app/`
2. **Interface:** Adicione em `interface/lib/`
3. **Documentação:** Atualize `docs/`

### **Estrutura de Pastas:**

- `backend/` - Lógica de negócio e CV
- `interface/` - UI e experiência do usuário
- `treinamento/` - Scripts de ML
- `docs/` - Documentação completa

## 📦 Dependências

### **Backend:**
- FastAPI, OpenCV, MediaPipe, NumPy, scikit-learn

### **Interface:**
- Flutter SDK

## 🎮 Poses Suportadas

1. **Enquadramento** - Centralização do usuário
2. **Duplo Bíceps**
3. **Side Chest**
4. **Side Triceps**
5. **Most Muscular**

## 🔄 Status do Projeto

- ✅ Backend FastAPI funcionando
- ✅ Motor de CV isolado e testado
- ✅ API REST completa
- 🔄 Interface Flutter (em desenvolvimento)
- ⏳ WebSocket para stream em tempo real (planejado)

## 📄 Licença

Este projeto é de uso educacional e pessoal.

---

**BodyVision Team** - Sistema Profissional de Análise de Poses
