# 🎓 Treinamento da IA

Este diretório contém scripts para treinar modelos de Machine Learning que melhoram a avaliação de poses.

## 📋 Pipeline Básico

### 1. Coleta de Dados

**Opção A: Coleta Manual**
- Durante o uso do sistema, marque poses como corretas/incorretas
- Dados são salvos automaticamente em `ml/data/`

**Opção B: Processamento de Imagens/Vídeos**
```bash
python image_processor.py
```
- Processa imagens ou vídeos
- Extrai landmarks automaticamente
- Gera labels usando regras atuais

**Opção C: Web Scraping**
```bash
python web_scraper.py
```
- Coleta artigos sobre poses
- Baixa imagens de exemplos
- Veja `README_TREINAMENTO_AVANCADO.md` para detalhes

**Opção D: Processar poseInfo (Textos e Imagens de Referência)**
```bash
python process_pose_info.py
```
- Extrai texto dos arquivos `.pages` na pasta `ml/pose_info/`
- Processa as imagens de referência de cada pose
- Extrai landmarks e métricas do texto
- Gera dados de treinamento com label "correct" (imagens de referência)

### 2. Exportar Dados

```bash
python export_training_data.py
```

Exporta dados coletados manualmente para `data_for_training.json`.

### 3. Consolidar Dados (se usar múltiplas fontes)

```bash
python consolidate_training_data.py
```

Combina dados de todas as fontes em um único arquivo.

### 4. Treinar Modelo

```bash
python train_model.py
```

Escolha:
- **1**: Modelo geral (todas as poses)
- **2**: Modelos individuais (um por pose)
- **3**: Ambos

Modelos são salvos em `ml/models/` na raiz do projeto.

## 📊 Requisitos de Dados

- **Mínimo**: 100 amostras por pose (50 corretas + 50 incorretas)
- **Ideal**: 200+ de cada tipo
- **Total**: 500-1000+ amostras para bons resultados

## 🎯 Como Funciona

1. **Coleta**: Dados são coletados com landmarks e labels
2. **Exportação**: Dados são formatados para treinamento
3. **Treinamento**: Modelo aprende padrões dos dados
4. **Uso**: Sistema usa modelo para melhorar feedbacks

O modelo é combinado com as regras atuais para feedbacks mais precisos.

## 📁 Arquivos

- `train_model.py` - Treina modelos ML
- `export_training_data.py` - Exporta dados coletados
- `image_processor.py` - Processa imagens/vídeos
- `web_scraper.py` - Coleta dados de artigos web
- `process_pose_info.py` - Processa textos e imagens de referência da pasta ml/pose_info
- `consolidate_training_data.py` - Consolida todas as fontes

---

Para treinamento avançado com web scraping, veja `README_TREINAMENTO_AVANCADO.md`.
