# 📊 Sistema de Coleta de Dados para Treinamento

Este documento descreve o sistema de coleta de dados integrado ao BodyVision para treinamento de modelos de machine learning.

## 🎯 Objetivo

Coletar dados de alta qualidade (imagens + landmarks + labels) durante o uso normal do sistema para treinar modelos de ML que melhorarão a precisão da avaliação de poses.

## 🚀 Como Usar

### Durante o Uso Normal

O sistema de coleta está **habilitado por padrão**. Você pode coletar dados durante qualquer sessão:

1. **Coletar amostra pendente** (para revisar depois):
   - Pressione `C` quando a pose estiver detectada
   - A amostra será salva como "pending" (precisa confirmação depois)

2. **Marcar como CORRETO e coletar**:
   - Pressione `V` quando a pose estiver **correta** conforme sua avaliação
   - A amostra será salva como "correct" com sua confirmação

3. **Marcar como INCORRETO e coletar**:
   - Pressione `X` quando a pose estiver **incorreta** conforme sua avaliação
   - A amostra será salva como "incorrect" com sua confirmação

### Validações Automáticas

O sistema valida automaticamente a qualidade antes de coletar:
- ✅ **Blur mínimo**: Rejeita imagens muito borradas
- ✅ **Landmarks visíveis**: Garante que pelo menos 25 dos 33 landmarks estejam visíveis
- ✅ **Detecção de pose**: Só coleta quando uma pose é detectada
- ✅ **Detecção de duplicatas**: Evita coletar frames muito similares consecutivamente

### Visualização

Durante a coleta, você verá:
- **Mensagens temporárias** (últimos 3 segundos) no canto inferior direito quando coletar
- **Estatísticas** no canto superior esquerdo mostrando:
  - Total de amostras coletadas
  - Quantas são "correct" e "incorrect"

## 📁 Estrutura de Dados

Os dados são salvos em `data_collected/`:

```
data_collected/
├── raw/              # Imagens originais (.jpg)
├── processed/        # (Reservado para futuras expansões)
└── annotations/      # Metadados JSON com landmarks e labels
```

### Formato dos Metadados

Cada arquivo JSON contém:
```json
{
  "sample_id": "double_biceps_correct_20231206_143025_123_0001",
  "timestamp": "2023-12-06T14:30:25.123456",
  "pose_mode": "double_biceps",
  "label": "correct",
  "user_confirmed": true,
  "frame_filename": "...",
  "frame_size": {"width": 1280, "height": 720},
  "landmarks": {
    "0": {"x": 0.5, "y": 0.3, "z": -0.1, "visibility": 0.9},
    ...
  },
  "quality_metrics": {
    "blur_score": 245.6,
    "visible_landmarks": 30,
    "visibility_ratio": 0.91,
    "overall_quality": 0.85
  },
  "pose_quality_feedback": "Posicao correta - Excelente postura!"
}
```

## 📤 Exportar para Treinamento

Após coletar dados, exporte-os para treinamento:

```bash
python export_training_data.py
```

Isso cria `data_for_training.json` com apenas amostras:
- ✅ Confirmadas pelo usuário (`user_confirmed: true`)
- ✅ Com labels válidas (`correct` ou `incorrect`)
- ❌ Exclui amostras `pending`

## 🎓 Dicas para Boa Coleta

### Diversidade
- Coleta de **diferentes pessoas** (quanto mais, melhor)
- Coleta em **diferentes ângulos** e distâncias da câmera
- Coleta com **diferentes iluminações**

### Qualidade
- **Não colete imagens borradas** - o sistema rejeitará automaticamente, mas evite tentar
- **Seja consistente** nas labels:
  - "correct" = pose está realmente correta segundo os critérios
  - "incorrect" = pose tem algum erro visível
- **Revise amostras "pending"** periodicamente e reclassifique

### Quantidade Recomendada
Para cada pose, objetivo inicial:
- **Mínimo**: 50 amostras corretas + 50 incorretas
- **Ideal**: 200+ amostras corretas + 200+ incorretas
- **Excelente**: 500+ de cada

## 🔧 Configuração Avançada

Para desabilitar a coleta (se não quiser usar):

```python
# Em BodyVision.py, main():
app = BodyVisionApp(enable_data_collection=False)
```

Para ajustar thresholds de qualidade (em `data_collector.py`):

```python
self.min_blur_threshold = 100      # Aumente para exigir imagens mais nítidas
self.min_visible_landmarks = 25    # Aumente para exigir mais landmarks visíveis
```

## 📊 Estatísticas

Você pode ver estatísticas a qualquer momento:

```python
from data_collector import DataCollector
collector = DataCollector()
stats = collector.get_statistics()
print(stats)
```

## ⚠️ Importante

- **Não delete manualmente** arquivos de `data_collected/` sem backup
- **Mantenha backups** regulares dos dados coletados
- **Revise periodicamente** amostras "pending" e reclassifique
- Os dados são **seu dataset de treinamento** - qualidade é crucial!

## 🚀 Próximos Passos

Após coletar dados suficientes:
1. Exporte com `export_training_data.py`
2. Use o arquivo JSON para treinar modelos de ML
3. Integre o modelo treinado no sistema (Fase 2+ do roadmap)

---

**Boa coleta! 🎯**

