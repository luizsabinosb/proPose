# 🎓 Guia de Treinamento Avançado - Web Scraping e Imagens/Vídeos

Este guia explica como usar **artigos web** e **imagens/vídeos** para treinar a IA automaticamente, sem precisar coletar dados manualmente durante o uso.

## 🎯 Visão Geral

O sistema agora suporta **3 fontes de dados** para treinamento:

1. **Coleta Manual** - Durante o uso (teclas V/X)
2. **Web Scraping** - Artigos sobre poses de fisiculturismo
3. **Processamento de Imagens/Vídeos** - Extração automática de landmarks

## 📋 Pipeline Completo

```
┌─────────────────────────────────────────────────────────────┐
│  FASE 1: COLETA DE DADOS                                   │
│  ─────────────────────────────────────────────────────────  │
│  Opção A: Coleta Manual (durante uso)                      │
│  Opção B: Web Scraping (artigos)                           │
│  Opção C: Processamento de Imagens/Vídeos                   │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  FASE 2: CONSOLIDAÇÃO                                       │
│  ─────────────────────────────────────────────────────────  │
│  python consolidate_training_data.py                        │
│  Combina todas as fontes em um único arquivo                │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  FASE 3: TREINAMENTO                                        │
│  ─────────────────────────────────────────────────────────  │
│  python train_model.py                                      │
│  Treina modelos com dados consolidados                      │
└─────────────────────────────────────────────────────────────┘
```

## 🌐 FASE 1A: Web Scraping

### O que faz:
- Coleta artigos sobre poses de fisiculturismo
- Extrai imagens dos artigos
- Identifica poses mencionadas no texto
- Salva metadados para processamento posterior

### Como usar:

```bash
cd treinamento
python web_scraper.py
```

### Passos:
1. O script oferece URLs conhecidas (ex: BarBend)
2. Você pode adicionar mais URLs
3. Escolhe se quer baixar imagens
4. O script faz scraping e salva em `ml/data/web/`

### Resultado:
- `scraped_articles.json` - Metadados dos artigos
- `images/` - Imagens baixadas (se escolhido)

## 🖼️ FASE 1B: Processamento de Imagens/Vídeos

### O que faz:
- Processa imagens/vídeos com MediaPipe
- Extrai landmarks automaticamente
- Usa regras atuais para gerar labels (correct/incorrect)
- Salva dados no formato de treinamento

### Como usar:

```bash
cd treinamento
python image_processor.py
```

### Opções:
1. **Diretório de imagens** - Processa todas as imagens de uma pasta
2. **Diretório de vídeos** - Extrai frames de vídeos
3. **Arquivo único** - Processa uma imagem ou vídeo específico

### Exemplo:
```bash
# Processa todas as imagens de uma pasta
python image_processor.py
# Escolha: 1
# Caminho: /caminho/para/imagens/
# Modo: side_chest
# Label: (deixe vazio para auto-detectar)
```

### Como funciona:
1. Carrega imagem/vídeo
2. Detecta pose com MediaPipe
3. Extrai landmarks e calcula ângulos
4. Avalia usando regras atuais (mesmas do sistema)
5. Gera label automático (ou usa o que você especificar)
6. Salva em formato de treinamento

### Labels automáticos:
- **Correct**: Se não há erros na avaliação
- **Incorrect**: Se há erros detectados pelas regras

### Labels manuais:
Você pode especificar o label esperado:
- `correct` - Marca como correto
- `incorrect` - Marca como incorreto

## 🔄 FASE 2: Consolidação

### O que faz:
- Combina dados de todas as fontes
- Remove duplicatas
- Gera estatísticas
- Cria arquivo único para treinamento

### Como usar:

```bash
cd treinamento
python consolidate_training_data.py
```

### Resultado:
- `data_for_training.json` - Arquivo consolidado na raiz
- Estatísticas por pose, label e fonte

## 🎓 FASE 3: Treinamento

Após consolidar, treine normalmente:

```bash
python train_model.py
```

## 📊 Exemplo Completo

### Cenário: Treinar com imagens da web

```bash
# 1. Faz scraping de artigos
cd treinamento
python web_scraper.py
# Adicione URLs, baixe imagens

# 2. Processa imagens baixadas
python image_processor.py
# Escolha: 1 (diretório de imagens)
# Caminho: ml/data/web/images/
# Modo: side_chest
# Label: (auto)

# 3. Consolida tudo
python consolidate_training_data.py

# 4. Treina
python train_model.py
```

## 🎯 Vantagens desta Abordagem

### ✅ Escalabilidade
- Pode processar centenas de imagens/vídeos rapidamente
- Não precisa coletar manualmente durante o uso

### ✅ Diversidade
- Dados de múltiplas fontes (web, imagens, vídeos)
- Diferentes pessoas, condições, iluminações

### ✅ Qualidade
- Labels gerados pelas mesmas regras do sistema
- Consistência com a avaliação real

### ✅ Flexibilidade
- Pode revisar e ajustar labels manualmente
- Pode combinar com dados coletados manualmente

## ⚙️ Configurações Avançadas

### Processar apenas imagens corretas:
```python
# Em image_processor.py, especifique label:
python image_processor.py
# Escolha: 3 (arquivo único)
# Label: correct
```

### Processar vídeo com taxa específica:
```python
# Em image_processor.py, ajuste sample_rate:
samples = processor.process_video(video_path, pose_mode, sample_rate=60)
# Processa 1 frame a cada 60 (1 por segundo em 60fps)
```

### Filtrar por qualidade:
O `DataCollector` já valida qualidade automaticamente:
- Blur mínimo
- Landmarks visíveis
- Tamanho mínimo

## 📁 Estrutura de Arquivos

```
ProPosing/
├── treinamento/
│   ├── web_scraper.py              # Scraping de artigos
│   ├── image_processor.py          # Processamento de imagens/vídeos
│   ├── consolidate_training_data.py # Consolidação
│   └── train_model.py              # Treinamento
├── ml/
│   └── data/
│       ├── web/                    # Dados de web scraping
│       │   ├── scraped_articles.json
│       │   └── images/
│       └── processed/              # Dados processados
│           └── web_training_data.json
└── data_for_training.json          # Arquivo consolidado final
```

## 💡 Dicas

### Para melhores resultados:
1. **Diversifique fontes**: Use web scraping + imagens + coleta manual
2. **Revise labels**: Especialmente para imagens da web
3. **Balance dados**: Tente ter ~50/50 correct/incorrect por pose
4. **Qualidade > Quantidade**: Melhor ter 100 boas amostras que 1000 ruins

### Fontes recomendadas:
- **Artigos**: BarBend, Bodybuilding.com, Muscle & Fitness
- **Imagens**: Competições profissionais, tutoriais
- **Vídeos**: Demonstrações de poses, competições

## ⚠️ Considerações Legais

- Respeite termos de uso dos sites
- Use dados apenas para treinamento
- Dê crédito quando apropriado
- Considere usar APIs oficiais quando disponíveis

## 🚀 Próximos Passos

Após treinar com dados externos:
1. Teste o modelo no sistema real
2. Colete mais dados durante uso (refinamento)
3. Re-treine periodicamente com novos dados
4. Monitore performance e ajuste

---

**Pronto!** Agora você pode treinar a IA usando artigos web e imagens/vídeos automaticamente! 🎉
