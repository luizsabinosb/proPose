# Scripts de Treinamento - BodyVision

Este diretório contém os scripts para treinamento de modelos de Machine Learning.

## Scripts

- **`export_training_data.py`** - Exporta dados coletados para formato de treinamento
- **`train_model.py`** - Treina modelos ML usando os dados exportados

## Como Usar

### 1. Coletar Dados

Durante o uso do sistema, colete dados usando os controles:
- `V` - Marcar como CORRETO
- `X` - Marcar como INCORRETO

### 2. Exportar Dados

```bash
cd treinamento
python export_training_data.py
```

Isso cria o arquivo `data_for_training.json` na raiz do projeto.

### 3. Treinar Modelos

```bash
python train_model.py
```

Os modelos treinados serão salvos em `models/` na raiz do projeto.

---

**Nota:** Os dados coletados devem estar em `data_collected/` na raiz do projeto.

