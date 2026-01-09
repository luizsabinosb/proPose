# 🧪 Guia de Testes - BodyVision

## 🚀 Teste Rápido

### **1. Testar Backend (Python)**

#### Opção A: Script Automático
```bash
cd backend
./start.sh
```

#### Opção B: Manual
```bash
cd backend

# Criar ambiente virtual (primeira vez)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Iniciar servidor
uvicorn app.main:app --reload
```

**O servidor estará em:** `http://localhost:8000`
**Documentação:** `http://localhost:8000/docs`

#### Testar API
```bash
# Em outro terminal
cd backend
python test_api.py
```

Ou use curl:
```bash
# Health check
curl http://localhost:8000/health

# Selecionar pose
curl -X POST http://localhost:8000/api/v1/pose/select \
  -H "Content-Type: application/json" \
  -d '{"pose_mode": "enquadramento"}'
```

---

### **2. Testar Flutter App**

```bash
cd interface

# Instalar dependências
flutter pub get

# Executar (certifique-se que o backend está rodando)
flutter run
```

**Importante:** 
- Se usar dispositivo físico, altere o IP em `interface/lib/data/api/api_client.dart`
- Substitua `localhost` pelo IP da sua máquina (ex: `192.168.1.100`)

---

## ✅ Checklist de Testes

### **Backend**
- [ ] Servidor inicia sem erros
- [ ] Health check responde (`/health`)
- [ ] Documentação acessível (`/docs`)
- [ ] Endpoint de seleção funciona (`/api/v1/pose/select`)
- [ ] Endpoint de avaliação funciona (`/api/v1/pose/evaluate`)

### **Flutter**
- [ ] App compila sem erros
- [ ] Câmera funciona
- [ ] Conecta ao backend
- [ ] Recebe avaliações
- [ ] Feedback visual funciona

---

## 🐛 Problemas Comuns

### **Backend não inicia**
- Verifique se todas as dependências estão instaladas: `pip install -r requirements.txt`
- Verifique se a porta 8000 está livre
- Verifique erros no console

### **Flutter não conecta ao backend**
- Verifique se o backend está rodando
- Se usar dispositivo físico, use IP da máquina (não localhost)
- Verifique firewall/antivírus

### **Erro de importação no backend**
- Verifique se `bodyvision/` está acessível
- Execute a partir da raiz do projeto ou ajuste o PYTHONPATH

---

## 📝 Próximos Testes

1. **Teste com câmera real:** Usar frame real da câmera
2. **Teste de performance:** Medir latência e FPS
3. **Teste de todas as poses:** Validar cada modo
4. **Teste de ML:** Verificar se modelos funcionam

---

**Boa sorte com os testes! 🚀**

