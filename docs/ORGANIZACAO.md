# 📁 Organização do Projeto

## 🗂️ Estrutura de Pastas

```
BodyVision/
├── backend/                    # ✅ Backend FastAPI
│   ├── app/                   # Código da aplicação
│   ├── requirements.txt       # Dependências Python
│   ├── test_api.py           # Testes automatizados
│   └── start.sh              # Script de inicialização
│
├── interface/                  # ✅ App Flutter
│   ├── lib/                  # Código Dart
│   └── pubspec.yaml          # Dependências Flutter
│
├── treinamento/                # ✅ Scripts ML
│   ├── export_training_data.py
│   ├── train_model.py
│   └── README.md
│
├── bodyvision/                 # ⚠️ LEGADO (temporário)
│   ├── pose_evaluator.py     # (usado pelo backend)
│   ├── ml_evaluator.py       # (usado pelo backend)
│   ├── data_collector.py     # (usado pelo backend)
│   └── camera_utils.py       # (usado pelo backend)
│
├── docs/                       # ✅ TODA A DOCUMENTAÇÃO
│   ├── GUIA_TESTES.md        # Índice de testes
│   ├── TESTE_RAPIDO.md       # Teste rápido
│   ├── COMO_TESTAR.md        # Guia completo
│   ├── PLANO_REFATORACAO.md  # Plano de migração
│   ├── API_CONTRACTS.md      # Documentação API
│   └── ...
│
├── data_collected/             # 📊 Dados coletados (gerado)
├── models/                     # 🤖 Modelos ML (gerado)
│
├── README.md                   # Este arquivo
└── .gitignore                 # Arquivos ignorados
```

## 📚 Organização da Documentação

Toda a documentação está em `docs/` organizada por categoria:

### **Testes:**
- `GUIA_TESTES.md` - Índice
- `TESTE_RAPIDO.md` - Teste rápido
- `COMO_TESTAR.md` - Guia completo
- `TESTAR_SEM_FLUTTER.md` - Backend only
- `INSTALAR_FLUTTER.md` - Instalação
- `CORRIGIR_FLUTTER.md` - Troubleshooting

### **Arquitetura:**
- `ARQUITETURA_PROFISSIONAL.md` - Arquitetura completa
- `PLANO_REFATORACAO.md` - Plano de migração
- `ESTRUTURA_PROJETO.md` - Estrutura detalhada
- `ESTRATEGIA_COMUNICACAO.md` - WebSocket vs REST

### **Técnica:**
- `API_CONTRACTS.md` - Contratos de API
- `UI_DESIGN_SYSTEM.md` - Design system
- `GUIA_COLETA.md` - Coleta de dados
- `GUIA_TREINAMENTO.md` - Treinamento ML

## 🧹 Arquivos Removidos

- ❌ `run_kivy.py` - Kivy não é mais usado
- ❌ `main.py` - Entry point antigo
- ❌ `bodyvision/gui/` - Interface Kivy
- ❌ `scripts/` - Movido para `treinamento/`
- ❌ `requirements.txt` (raiz) - Agora só em `backend/`

## 📝 Arquivos na Raiz

Apenas arquivos essenciais na raiz:
- `README.md` - Documentação principal
- `.gitignore` - Configuração Git

Tudo mais está organizado nas pastas apropriadas.

---

**Última atualização:** Após reorganização completa

