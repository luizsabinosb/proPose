# 📊 Guia Prático de Coleta de Dados

## 🚀 Iniciando a Coleta

### Passo 1: Inicie o programa normalmente

```bash
cd /Users/luizsabino/Desktop/BodyVision
source venv/bin/activate
python BodyVision.py
```

### Passo 2: Posicione-se na frente da câmera

- Fique em uma boa distância da câmera (2-3 metros)
- Certifique-se de que a iluminação está boa
- O sistema detectará automaticamente sua pose

### Passo 3: Escolha uma pose

Pressione as teclas:
- **1** - Enquadramento
- **2** - Duplo Bíceps (Frente)
- **3** - Duplo Bíceps de Costas
- **4** - Side Chest
- **5** - Most Muscular

## 📸 Como Coletar Dados

### Durante o uso, você verá feedback na tela

O sistema mostra:
- ✅ **Verde** = Pose correta
- ❌ **Vermelho** = Pose incorreta (com detalhes do que está errado)

### Três tipos de coleta:

#### 1️⃣ Coletar como CORRETO (Recomendado)

**Quando usar:**
- A pose está **realmente correta** segundo os critérios
- Você quer treinar o modelo para reconhecer poses corretas

**Como fazer:**
1. Execute a pose corretamente
2. Aguarde o feedback verde aparecer (ou mesmo se aparecer vermelho, mas você sabe que está correto)
3. **Pressione `V`** (maiúscula ou minúscula)
4. Você verá: `✅ CORRETO coletado: [mensagem]` no terminal
5. Uma mensagem verde aparecerá no canto inferior direito da tela

**Exemplo prático:**
```
1. Você está fazendo "Duplo Bíceps (Frente)"
2. Posiciona corretamente os braços
3. Sistema mostra: "Posicao correta - Excelente postura!"
4. Você pressiona V
5. Sistema coleta: frame + landmarks + label "correct"
```

#### 2️⃣ Coletar como INCORRETO (Recomendado)

**Quando usar:**
- A pose tem **erros visíveis**
- Você quer treinar o modelo a identificar erros

**Como fazer:**
1. Execute a pose com algum erro proposital (ou natural)
2. O sistema pode mostrar feedback vermelho
3. **Pressione `X`** (maiúscula ou minúscula)
4. Você verá: `❌ INCORRETO coletado: [mensagem]` no terminal
5. Uma mensagem vermelha aparecerá no canto inferior direito

**Exemplo prático:**
```
1. Você está fazendo "Duplo Bíceps (Frente)"
2. Deixa os cotovelos muito baixos (erro proposital)
3. Sistema mostra: "Posicao incorreta - Cotovelo esquerdo muito baixo..."
4. Você pressiona X
5. Sistema coleta: frame + landmarks + label "incorrect"
```

#### 3️⃣ Coletar como PENDENTE (Opcional)

**Quando usar:**
- Você quer revisar depois se a pose está correta
- Está em dúvida se é correct ou incorrect

**Como fazer:**
1. Execute a pose
2. **Pressione `C`** (maiúscula ou minúscula)
3. A amostra será salva como "pending"
4. Você pode revisar depois e reclassificar manualmente nos arquivos

**⚠️ Importante:** Amostras "pending" NÃO são exportadas automaticamente para treinamento. Você precisa revisá-las depois.

## 🎯 Estratégia de Coleta Recomendada

### Fase 1: Coleta Básica (Objetivo: 50-100 de cada)

**Para cada pose, colete:**

1. **Poses Corretas** (pressione `V`):
   - Execute a pose corretamente 50-100 vezes
   - Varie sua posição na câmera (esquerda, centro, direita)
   - Varie a distância (um pouco mais perto, um pouco mais longe)

2. **Poses Incorretas** (pressione `X`):
   - Execute com erros propositais 50-100 vezes
   - Diferentes tipos de erros:
     - Cotovelos muito baixos/altos
     - Ângulos incorretos
     - Posicionamento errado
     - Etc.

### Fase 2: Diversificação (Objetivo: 200+ de cada)

- **Diferentes pessoas** (se possível)
- **Diferentes iluminações** (dia, noite, diferentes ambientes)
- **Diferentes ângulos** da câmera
- **Diferentes roupas** (quanto mais variação, melhor)

### Fase 3: Refinamento (Objetivo: 500+ de cada)

- Casos limite (quase corretos, quase incorretos)
- Variações sutis
- Diferentes tipos corporais (se possível)

## 📊 Monitorando a Coleta

### Durante a coleta, você verá:

**No canto superior esquerdo da tela:**
```
Coletadas: 45
✓ 23  ✗ 22
```

Isso mostra:
- Total de amostras coletadas
- Quantas são "correct" (✓)
- Quantas são "incorrect" (✗)

### No terminal:

Cada vez que coletar, verá mensagens como:
```
✅ CORRETO coletado: Coletado: double_biceps_correct_20231206_143025_123_0001.jpg
```

Ou em caso de erro de validação:
```
⚠️ Imagem muito borrada
⚠️ Poucos landmarks visíveis (20/33)
```

## 🧪 Cenários de Teste

### Teste 1: Coleta Básica

**Objetivo:** Familiarizar-se com o sistema

1. Execute o programa
2. Escolha pose "Duplo Bíceps (Frente)" (tecla 2)
3. Execute a pose corretamente 5 vezes
4. Cada vez que estiver correto, pressione `V`
5. Execute a pose incorretamente 5 vezes
6. Cada vez que estiver incorreto, pressione `X`
7. Verifique as estatísticas na tela

**Resultado esperado:** 
- 10 amostras coletadas
- 5 correct, 5 incorrect

### Teste 2: Validações Automáticas

**Objetivo:** Ver como o sistema rejeita dados ruins

1. Execute o programa
2. Movimente-se muito rápido (causa blur)
3. Tente coletar (pressione `V`)
4. Observe a mensagem de erro

**Outros testes:**
- Fique muito longe da câmera
- Fique parcialmente fora do frame
- Movimente-se durante a coleta

**Resultado esperado:**
- Sistema rejeita automaticamente
- Mensagens de erro aparecem

### Teste 3: Verificar Dados Coletados

**Objetivo:** Confirmar que os dados estão sendo salvos

```bash
# Veja as estatísticas
python export_training_data.py

# Veja os arquivos coletados
ls -lh data_collected/raw/
ls -lh data_collected/annotations/

# Veja um exemplo de metadados
cat data_collected/annotations/*.json | head -50
```

### Teste 4: Exportação para Treinamento

**Objetivo:** Preparar dados para ML

```bash
# Exporta apenas amostras confirmadas
python export_training_data.py
```

**Resultado esperado:**
- Arquivo `data_for_training.json` criado
- Apenas amostras "correct" e "incorrect" são exportadas
- Amostras "pending" são ignoradas

## ✅ Checklist de Coleta Ideal

Para cada pose, certifique-se de ter:

- [ ] **Diversidade de poses corretas:**
  - [ ] Posição centralizada
  - [ ] Posição à esquerda
  - [ ] Posição à direita
  - [ ] Diferentes distâncias
  
- [ ] **Diversidade de poses incorretas:**
  - [ ] Cada tipo de erro identificado nas métricas
  - [ ] Erros sutis
  - [ ] Erros graves
  
- [ ] **Validação de qualidade:**
  - [ ] Todas as imagens são nítidas
  - [ ] Todas têm landmarks bem visíveis
  - [ ] Nenhuma duplicata óbvia

## 💡 Dicas Importantes

### ✅ FAÇA:

1. **Seja consistente** nas labels
   - Se a pose está correta → SEMPRE use `V`
   - Se tem erros → SEMPRE use `X`

2. **Colete gradualmente**
   - Não tente coletar tudo de uma vez
   - Faça sessões de 20-30 amostras por vez

3. **Revise periodicamente**
   - Exporte os dados e veja as estatísticas
   - Verifique se está balanceado (corretas vs incorretas)

4. **Colete em diferentes condições**
   - Diferentes horários do dia
   - Diferentes ambientes
   - Diferentes roupas

### ❌ NÃO FAÇA:

1. **Não colete imagens muito borradas**
   - O sistema rejeitará, mas é perda de tempo

2. **Não seja inconsistente**
   - Não marque a mesma situação como correct às vezes e incorrect outras vezes

3. **Não ignore as validações**
   - Se o sistema rejeitar, há um motivo (blur, poucos landmarks, etc.)

4. **Não delete dados coletados**
   - Faça backups regulares
   - Os dados são valiosos!

## 🎯 Meta Inicial

**Para começar bem:**

- **Por pose:** 50 corretas + 50 incorretas = 100 amostras
- **Total (5 poses):** 500 amostras
- **Tempo estimado:** 2-3 horas de coleta

Com 500 amostras bem coletadas, você já pode começar a treinar um modelo básico!

---

**Boa coleta! 🎯**

Qualquer dúvida, consulte o `README_COLETA_DADOS.md` para mais detalhes técnicos.

