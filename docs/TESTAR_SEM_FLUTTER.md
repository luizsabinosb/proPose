# 🧪 Testar Backend Sem Flutter

## ✅ Você Pode Testar Tudo do Backend!

Não precisa do Flutter para testar se o sistema funciona. O backend é **independente** e pode ser testado de várias formas.

---

## 🚀 Método 1: Script Automatizado (Mais Fácil)

```bash
cd backend
source venv/bin/activate
python test_api.py
```

Este script testa todos os endpoints automaticamente.

---

## 🌐 Método 2: Interface Web (Mais Visual)

### 1. Iniciar Backend:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### 2. Abrir no Navegador:
Acesse: **http://localhost:8000/docs**

Esta é a **documentação interativa Swagger** onde você pode:
- ✅ Ver todos os endpoints
- ✅ Testar diretamente no navegador
- ✅ Enviar imagens e ver resultados
- ✅ Ver exemplos de requisições/respostas

---

## 🔧 Método 3: curl (Linha de Comando)

### Health Check:
```bash
curl http://localhost:8000/health
```

### Selecionar Pose:
```bash
curl -X POST http://localhost:8000/api/v1/pose/select \
  -H "Content-Type: application/json" \
  -d '{"pose_mode": "enquadramento"}'
```

### Avaliar Pose (com imagem):
```bash
# Precisa de uma imagem em base64
curl -X POST http://localhost:8000/api/v1/pose/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "image": "base64_da_imagem_aqui",
    "pose_mode": "enquadramento",
    "camera_width": 640
  }'
```

---

## 📊 O Que Você Pode Testar

### ✅ Funcionalidades Validadas:
1. ✅ **Health Check** - Verifica se servidor está rodando
2. ✅ **Seleção de Pose** - Trocar entre modos de pose
3. ✅ **Avaliação de Pose** - Processar frame e retornar feedback
4. ✅ **Processamento CV** - MediaPipe funcionando
5. ✅ **ML Integration** - Se modelos estiverem disponíveis

### ✅ Resultados Esperados:
- Mesmas mensagens do sistema antigo
- Mesmos cálculos de ângulos
- Mesmas regras de avaliação
- Performance similar

---

## 🎯 Próximos Passos

**Opção 1: Continuar sem Flutter**
- ✅ Backend funciona completamente sozinho
- ✅ Pode ser usado por qualquer cliente (web, mobile, desktop)
- ✅ Interface Flutter pode ser adicionada depois

**Opção 2: Instalar Flutter Depois**
- Quando quiser testar a interface visual
- Siga o guia `INSTALAR_FLUTTER.md`

---

## 💡 Vantagens de Testar Só o Backend

1. ✅ **Mais rápido** - Não precisa instalar Flutter
2. ✅ **Valida toda lógica** - CV, ML, avaliações
3. ✅ **Facilita debug** - Logs claros no terminal
4. ✅ **Interface opcional** - Flutter pode ser adicionado depois

---

## 🐛 Se algo não funcionar

1. **Verifique se backend está rodando:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Veja logs no terminal** onde o backend está rodando

3. **Verifique dependências:**
   ```bash
   pip install -r requirements.txt
   ```

---

**Resumo:** O Flutter é opcional! O backend funciona perfeitamente sozinho. 🚀

