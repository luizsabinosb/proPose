# 🎓 Guia Completo: Treinamento e Uso de ML

Este guia explica o pipeline completo para treinar modelos de ML e usar no sistema principal.

## 📋 Pipeline Completo

```
┌─────────────────────────────────────────────────────────────┐
│  FASE 1: COLETA DE DADOS                                    │
│  ─────────────────────────────────────────────────────────  │
│  1. Rode: python BodyVision.py                              │
│  2. Colete dados usando teclas V, X, C                      │
│  3. Colete pelo menos 100+ amostras por pose                │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  FASE 2: EXPORTAÇÃO                                         │
│  ─────────────────────────────────────────────────────────  │
│  1. Rode: python export_training_data.py                    │
│  2. Isso cria: data_for_training.json                       │
│  3. Apenas amostras confirmadas são exportadas              │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  FASE 3: TREINAMENTO                                        │
│  ─────────────────────────────────────────────────────────  │
│  1. Rode: python train_model.py                             │
│  2. Escolha tipo de treinamento (1, 2 ou 3)                 │
│  3. Modelos são salvos em: models/                          │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  FASE 4: USO NO SISTEMA                                     │
│  ─────────────────────────────────────────────────────────  │
│  1. Rode: python BodyVision.py                              │
│  2. Sistema detecta modelos automaticamente                 │
│  3. Feedbacks agora usam ML + regras combinadas             │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Passo a Passo Detalhado

### FASE 1: Coleta de Dados

```bash
# 1. Inicie o sistema
python BodyVision.py

# 2. Durante o uso, colete dados:
#    - V = Marca como CORRETO e coleta
#    - X = Marca como INCORRETO e coleta
#    - C = Coleta como PENDENTE (revisar depois)

# 3. Objetivo: pelo menos 100 amostras por pose
#    - 50 corretas + 50 incorretas (mínimo)
#    - 200+ de cada (ideal)
```

**Dicas:**
- Varie posições, distâncias, iluminações
- Seja consistente nas labels (correto = sempre V)
- O sistema valida qualidade automaticamente

### FASE 2: Exportação

```bash
# Exporta dados coletados para formato de treinamento
python export_training_data.py
```

**Resultado:**
- Cria arquivo `data_for_training.json`
- Apenas amostras confirmadas (correct/incorrect)
- Amostras "pending" são ignoradas

### FASE 3: Treinamento

```bash
# Treina modelos de ML
python train_model.py
```

**Opções de treinamento:**

1. **Modelo Geral** (Opção 1)
   - Um modelo para todas as poses
   - Mais rápido de treinar
   - Salva em: `models/pose_classifier_general.pkl`
   - Boa quando há poucos dados

2. **Modelos Individuais** (Opção 2)
   - Um modelo por tipo de pose
   - Mais preciso por pose
   - Salva em: `models/pose_classifier_{pose_mode}.pkl`
   - Melhor com mais dados

3. **Ambos** (Opção 3)
   - Treina os dois tipos
   - Sistema usa modelo específico se disponível, senão usa geral
   - Recomendado para produção

**Durante o treinamento você verá:**
```
📊 Carregados 500 amostras de treinamento
🔄 Processando dados...
✅ 500 amostras processadas
   - Correct: 250
   - Incorrect: 250

🎓 Iniciando treinamento...
📚 Dados de treino: 400 amostras
📝 Dados de teste: 100 amostras
🌲 Treinando Random Forest...

📊 Resultados do Treinamento:
   Acurácia no Treino: 95.50%
   Acurácia no Teste: 89.00%

💾 Modelo salvo em: models/pose_classifier_general.pkl
```

### FASE 4: Uso no Sistema Principal

```bash
# Inicia o sistema (detecta modelos automaticamente)
python BodyVision.py
```

**O sistema automaticamente:**
- ✅ Carrega modelos treinados (se existirem)
- ✅ Usa ML + regras combinados
- ✅ Mostra feedbacks melhorados

**Você verá no terminal:**
```
✅ Modelo ML geral carregado
✅ Modelo ML para 'double_biceps' carregado
✅ Modelo ML para 'side_chest' carregado
...
```

## 🎯 Como Funciona a Combinação ML + Regras

O sistema usa uma abordagem híbrida:

1. **Regras (sempre ativas):**
   - Sistema base atual (ângulos, alturas, etc.)
   - Rápido e explicável
   - Bom para casos claros

2. **ML (quando disponível):**
   - Aprende padrões dos dados coletados
   - Identifica casos sutis e limite
   - Melhora precisão geral

3. **Combinação:**
   - **ML alta confiança (≥70%):** Prioriza ML
   - **ML baixa confiança:** Prioriza regras, mas menciona ML
   - **Sem ML:** Usa apenas regras

**Exemplos de feedbacks:**

- **Com ML (alta confiança):**
  ```
  ✅ [ML] Posição correta - Excelente postura!
  ```

- **Com ML (baixa confiança):**
  ```
  ❌ Cotovelo esquerdo muito baixo [ML:✓ conf:45%]
  ```

- **Sem ML:**
  ```
  ✅ Posição correta - Excelente postura!
  ```

## 📊 Estrutura de Arquivos

Após o treinamento, você terá:

```
BodyVision/
├── data_collected/          # Dados coletados
│   ├── raw/                # Imagens
│   └── annotations/        # Metadados JSON
├── models/                  # Modelos treinados
│   ├── pose_classifier_general.pkl
│   ├── pose_classifier_double_biceps.pkl
│   ├── pose_classifier_side_chest.pkl
│   └── ...
├── data_for_training.json   # Dados exportados
└── BodyVision.py           # Sistema principal (usa modelos)
```

## 🔧 Configurações Avançadas

### Desabilitar ML

Se quiser usar apenas regras (sem ML):

```python
# Em BodyVision.py, main():
app = BodyVisionApp(use_ml=False)
```

### Ajustar Confiança Mínima

Edite `ml_evaluator.py`, método `combine_with_rules`:

```python
confidence_threshold=0.7  # Aumente para 0.8 para ser mais conservador
```

### Treinar com Mais Dados

Após coletar mais dados:
1. Execute `export_training_data.py` novamente
2. Execute `train_model.py` novamente
3. Modelos serão sobrescritos com versões melhoradas

## 📈 Melhorando o Modelo

### Mais Dados = Melhor Modelo

- **100 amostras:** ~75-80% de precisão
- **500 amostras:** ~85-90% de precisão
- **1000+ amostras:** ~90-95% de precisão

### Qualidade dos Dados

- ✅ Dados diversos (diferentes pessoas, condições)
- ✅ Labels consistentes
- ✅ Boa distribuição (50/50 correct/incorrect)
- ❌ Evite viés (apenas um tipo de erro)

## ⚠️ Troubleshooting

### "Nenhum modelo ML encontrado"
- ✅ Execute `train_model.py` primeiro
- ✅ Verifique se arquivos `.pkl` existem em `models/`

### "Poucos dados para treinar"
- ✅ Colete mais dados (objetivo: 100+ por pose)
- ✅ Use modelo geral (opção 1) que precisa de menos dados

### "Acurácia baixa (<70%)"
- ✅ Colete mais dados
- ✅ Revise labels (podem estar incorretas)
- ✅ Varie mais as condições de coleta

### "Modelo não está sendo usado"
- ✅ Verifique se modelos foram carregados (veja mensagens no terminal)
- ✅ Verifique se `use_ml=True` no `__init__`

## 🎯 Resumo Rápido

```bash
# 1. Colete dados
python BodyVision.py  # Use V, X durante o uso

# 2. Exporte
python export_training_data.py

# 3. Treine
python train_model.py

# 4. Use (agora com ML!)
python BodyVision.py
```

---

**Pronto!** Seu sistema agora usa Machine Learning para melhorar os feedbacks automaticamente! 🚀

