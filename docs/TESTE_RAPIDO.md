# ⚡ Teste Rápido - BodyVision

## 🎯 Teste em 3 Passos

### **Passo 1: Instalar Dependências do Backend** (5 min)

```bash
cd backend

# Criar ambiente virtual
python3 -m venv venv

# Ativar (Linux/Mac)
source venv/bin/activate

# OU (Windows)
# venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### **Passo 2: Iniciar Backend** (1 min)

```bash
# Ainda no diretório backend, com venv ativado
uvicorn app.main:app --reload
```

**Deixe esse terminal aberto!** O servidor estará em: `http://localhost:8000`

### **Passo 3: Testar API** (2 min)

**Abra outro terminal** e execute:

```bash
cd backend
source venv/bin/activate  # Ativar venv novamente
python test_api.py
```

---

## ✅ Resultado Esperado

Você deve ver:
```
✅ Health check OK
✅ Endpoint raiz OK
✅ Seleção de pose OK
✅ Avaliação de pose OK
🎉 Todos os testes passaram!
```

---

## 🌐 Testar no Navegador

Abra no navegador:
- **Documentação:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health

---

## 🐛 Se algo der errado

### Erro: "ModuleNotFoundError"
```bash
# Instale as dependências
pip install -r requirements.txt
```

### Erro: "Port already in use"
```bash
# Matar processo na porta 8000
lsof -ti:8000 | xargs kill -9  # Mac/Linux
# ou mude a porta no main.py
```

### Erro: "Cannot import bodyvision"
O backend importa de `bodyvision/` que está na raiz. Isso é temporário.
Certifique-se de estar executando do diretório correto.

---

## 📱 Testar Flutter (Opcional)

Depois que o backend estiver funcionando:

```bash
cd interface
flutter pub get
flutter run
```

**Lembre-se:** O backend precisa estar rodando!

---

**Boa sorte! 🚀**

