# 🧪 Como Testar o BodyVision

## 🚀 Método Mais Rápido

### **1. Testar Backend (Python)**

#### Terminal 1 - Iniciar Backend:
```bash
cd backend

# Primeira vez: criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# ou: venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Iniciar servidor
uvicorn app.main:app --reload
```

**Deixe esse terminal aberto!** ✅

#### Terminal 2 - Testar API:
```bash
cd backend
source venv/bin/activate  # Ativar venv novamente
python test_api.py
```

**Resultado esperado:**
```
✅ Health check OK
✅ Endpoint raiz OK  
✅ Seleção de pose OK
✅ Avaliação de pose OK
🎉 Todos os testes passaram!
```

---

## 🌐 Verificar no Navegador

Com o backend rodando, abra:

1. **Documentação Interativa:** http://localhost:8000/docs
   - Interface Swagger para testar endpoints manualmente
   
2. **Health Check:** http://localhost:8000/health
   - Deve retornar: `{"status": "healthy"}`

---

## 📱 Testar Flutter (Opcional)

**⚠️ IMPORTANTE:** O Flutter precisa estar instalado no seu sistema!

Se aparecer `command not found: flutter`, você precisa instalar o Flutter primeiro.

**Opções:**

1. **Instalar Flutter** (se quiser testar interface):
   - Veja guia: `INSTALAR_FLUTTER.md`
   - Ou: https://docs.flutter.dev/get-started/install/macos

2. **Testar sem Flutter** (recomendado primeiro):
   - O backend funciona perfeitamente sozinho!
   - Veja: `TESTAR_SEM_FLUTTER.md`
   - Use a interface web: http://localhost:8000/docs

**Se Flutter estiver instalado:**

```bash
cd interface

# Instalar dependências
flutter pub get

# Executar
flutter run
```

**Se usar dispositivo físico:**
- Altere o IP em `interface/lib/data/api/api_client.dart`
- Substitua `localhost` pelo IP da sua máquina

---

## ✅ Checklist de Testes

### Backend
- [ ] Servidor inicia sem erros
- [ ] Porta 8000 está disponível
- [ ] Health check funciona (`/health`)
- [ ] Documentação acessível (`/docs`)
- [ ] Teste automatizado passa (`test_api.py`)

### Flutter (se testar)
- [ ] App compila
- [ ] Câmera funciona
- [ ] Conecta ao backend
- [ ] Recebe avaliações

---

## 🐛 Problemas Comuns

### ❌ "ModuleNotFoundError: No module named 'fastapi'"
**Solução:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### ❌ "Address already in use" (porta 8000 ocupada)
**Solução:**
```bash
# Encontrar processo
lsof -i :8000  # Mac/Linux
# ou
netstat -ano | findstr :8000  # Windows

# Matar processo
kill -9 <PID>  # Mac/Linux
# ou mude a porta no main.py
```

### ❌ "Cannot import bodyvision"
**Solução:** Isso é normal. O backend importa de `bodyvision/` na raiz do projeto.
Certifique-se de executar os comandos do diretório correto.

### ❌ Flutter não conecta
**Solução:**
- Verifique se backend está rodando
- Verifique IP (use IP da máquina, não localhost, se usar dispositivo físico)
- Verifique firewall

---

## 📊 Testes Adicionais

### Testar com câmera real:
1. Use a interface Flutter
2. Ou faça POST manual no `/docs` com imagem real

### Testar todas as poses:
```bash
# No navegador, vá para /docs e teste cada pose_mode:
# - enquadramento
# - double_biceps
# - back_double_biceps
# - side_chest
# - most_muscular
```

---

## 🎯 Próximos Passos

Após validar que tudo funciona:

1. ✅ Testar com frames reais da câmera
2. ✅ Validar todas as poses
3. ✅ Testar performance (FPS, latência)
4. ✅ Implementar WebSocket (para melhor performance)

---

**Boa sorte! 🚀**

Se encontrar problemas, verifique:
- Logs do backend (terminal onde está rodando)
- Mensagens de erro do Flutter
- `TESTE_GUIA.md` para mais detalhes

