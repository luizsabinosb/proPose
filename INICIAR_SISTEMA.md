# 🚀 Como Iniciar o Sistema - Guia Rápido

## ⚡ Início Rápido

### **1. Iniciar Backend** (Terminal 1)

```bash
cd backend
./iniciar_backend.sh
```

**OU manualmente:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Deixe este terminal aberto!** ✅

### **2. Testar Conexão** (Terminal 2)

```bash
./testar_conexao.sh
```

Isso vai testar se o backend está respondendo.

### **3. Iniciar Flutter** (Terminal 3)

```bash
cd interface
flutter pub get
flutter run
```

---

## 🔍 Verificar se Está Funcionando

Após iniciar o backend, você deve ver:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Teste no navegador: http://localhost:8000/docs

---

## ❗ Problemas Comuns

### Backend não inicia:
- Verifique se está na pasta `backend/`
- Ative o venv: `source venv/bin/activate`
- Instale dependências: `pip install -r requirements.txt`

### Conexão não funciona:
- Certifique-se de usar `--host 0.0.0.0`
- Verifique firewall do Mac
- Teste com `./testar_conexao.sh`

---

**Pronto! Agora está tudo configurado!** 🎉

