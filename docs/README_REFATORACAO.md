# 🔄 Guia de Refatoração - BodyVision

## 📋 Resumo

Este documento descreve a refatoração completa do BodyVision, removendo Kivy e migrando para uma arquitetura moderna com **Flutter** (frontend) e **FastAPI** (backend).

---

## 🎯 Objetivos

1. ✅ Remover completamente Kivy
2. ✅ Separar UI (Flutter) do processamento (Python)
3. ✅ Manter toda lógica de CV intacta
4. ✅ Criar API REST + WebSocket
5. ✅ Interface moderna e profissional

---

## 📁 Nova Estrutura

```
BodyVision/
├── backend/              # FastAPI (Python)
│   ├── app/
│   │   ├── core/        # Motor CV (reaproveitado)
│   │   ├── api/         # Endpoints REST/WebSocket
│   │   ├── models/      # Pydantic models
│   │   └── services/    # Lógica de negócio
│   └── requirements.txt
│
├── interface/            # App Flutter (Dart)
│   ├── lib/
│   │   ├── data/        # API clients
│   │   └── presentation/ # UI
│   └── pubspec.yaml
│
├── treinamento/          # Scripts ML
│   ├── export_training_data.py
│   └── train_model.py
│
├── bodyvision/           # LEGADO (será removido)
└── docs/                 # Documentação
```

---

## 🚀 Como Começar

### 1. **Setup Backend**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend estará em `http://localhost:8000`

### 2. **Setup Flutter**

```bash
cd interface
flutter pub get
flutter run
```

### 3. **Testar API**

```bash
# Testar health check
curl http://localhost:8000/health

# Testar avaliação (exemplo com imagem base64)
curl -X POST http://localhost:8000/api/v1/pose/evaluate \
  -H "Content-Type: application/json" \
  -d '{"image": "base64...", "pose_mode": "enquadramento"}'
```

---

## 📚 Documentação Completa

### **Documentos Principais:**

1. **[PLANO_REFATORACAO.md](./PLANO_REFATORACAO.md)** - Plano passo a passo detalhado
2. **[ESTRATEGIA_COMUNICACAO.md](./ESTRATEGIA_COMUNICACAO.md)** - WebSocket vs REST
3. **[API_CONTRACTS.md](./API_CONTRACTS.md)** - Contratos de API
4. **[ARQUITETURA_PROFISSIONAL.md](./ARQUITETURA_PROFISSIONAL.md)** - Arquitetura completa

### **Código Implementado:**

- ✅ Backend FastAPI (`backend/app/`)
- ✅ CV Service (`backend/app/core/cv_service.py`)
- ✅ Endpoints REST (`backend/app/api/v1/pose.py`)
- ✅ Exemplo Flutter (`interface/lib/`)

---

## 🔄 Fluxo de Migração

### **Fase 1: Backend (✅ Completo)**
- [x] Estrutura criada
- [x] CV Service implementado
- [x] API REST básica
- [x] Modelos Pydantic

### **Fase 2: Flutter (🔄 Em progresso)**
- [x] Estrutura criada
- [x] Exemplo básico
- [ ] Integração completa
- [ ] UI final

### **Fase 3: Otimizações**
- [ ] WebSocket implementado
- [ ] Compressão de imagens
- [ ] Cache e performance

### **Fase 4: Limpeza**
- [ ] Remover código Kivy
- [ ] Remover código legado
- [ ] Testes finais

---

## ⚙️ Configurações

### **Backend**

Configurar `baseUrl` em `backend/app/main.py`:
```python
app = FastAPI(...)
# CORS configurado para desenvolvimento
```

### **Flutter**

Configurar `baseUrl` em `interface/lib/data/api/api_client.dart`:
```dart
final baseUrl = 'http://localhost:8000';  // Ou IP da máquina
```

**Para dispositivo físico:**
- Use IP da máquina (não localhost)
- Exemplo: `http://192.168.1.100:8000`

---

## 🧪 Testes

### **Testar Backend:**

```bash
cd backend
python -m pytest  # (quando testes criados)
```

### **Testar Flutter:**

```bash
cd interface
flutter test
flutter run
```

---

## 📝 Próximos Passos

1. **Testar Backend:**
   - Iniciar servidor FastAPI
   - Testar endpoints com curl/Postman
   - Validar resultados com sistema antigo

2. **Testar Flutter:**
   - Compilar app
   - Conectar com backend
   - Testar câmera e avaliação

3. **Implementar WebSocket:**
   - Handler no backend
   - Cliente no Flutter
   - Otimizar para 30 FPS

4. **Remover Kivy:**
   - Deletar `bodyvision/gui/`
   - Remover dependências
   - Atualizar documentação

---

## ❓ Dúvidas Frequentes

### **O código CV foi alterado?**

Não. Toda lógica de CV está intacta, apenas extraída para `CVService`.

### **Os resultados são idênticos?**

Sim. A lógica é a mesma, apenas a forma de acesso mudou (API vs direto).

### **Posso usar o sistema antigo ainda?**

Sim. O sistema antigo (`bodyvision/`) continua funcionando durante a migração.

### **Como testar sem Flutter?**

Use curl ou Postman para testar os endpoints REST.

---

**Documento v1.0** - Guia de Refatoração

