# 🎨 Design System - BodyVision

## Princípios de Design

### 1. **Clareza Visual**
- Hierarquia clara de informações
- Feedback imediato e óbvio
- Sem informações redundantes

### 2. **Performance Visual**
- Animações suaves (60 FPS)
- Transições rápidas (< 200ms)
- Feedback instantâneo

### 3. **Acessibilidade**
- Contraste adequado (WCAG AA)
- Textos legíveis (mínimo 14px)
- Cores semânticas (não apenas cores)

### 4. **Consistência**
- Componentes reutilizáveis
- Padrões de layout
- Paleta de cores unificada

---

## 🎨 Paleta de Cores

### Cores Principais

```dart
// Primary (Azul moderno)
const Color primaryColor = Color(0xFF2196F3);        // Azul
const Color primaryDark = Color(0xFF1976D2);         // Azul escuro
const Color primaryLight = Color(0xFF64B5F6);        // Azul claro

// Background
const Color backgroundDark = Color(0xFF121212);      // Fundo escuro (Material Dark)
const Color surfaceDark = Color(0xFF1E1E1E);         // Superfície escura
const Color cardDark = Color(0xFF2D2D2D);            // Cards

// Text
const Color textPrimary = Color(0xFFFFFFFF);         // Texto principal
const Color textSecondary = Color(0xFFB0B0B0);       // Texto secundário
const Color textDisabled = Color(0xFF666666);        // Texto desabilitado
```

### Cores Semânticas (Feedback)

```dart
// Status: Correto (Verde)
const Color statusCorrect = Color(0xFF4CAF50);       // Verde Material
const Color statusCorrectBg = Color(0x1A4CAF50);     // Verde translúcido (10% opacidade)
const Color statusCorrectLight = Color(0xFF81C784);  // Verde claro

// Status: Incorreto (Vermelho)
const Color statusIncorrect = Color(0xFFF44336);     // Vermelho Material
const Color statusIncorrectBg = Color(0x1AF44336);   // Vermelho translúcido
const Color statusIncorrectLight = Color(0xFFE57373); // Vermelho claro

// Status: Ajuste Necessário (Amarelo)
const Color statusWarning = Color(0xFFFFC107);       // Amarelo Material
const Color statusWarningBg = Color(0x1AFFC107);     // Amarelo translúcido
const Color statusWarningLight = Color(0xFFFFD54F);  // Amarelo claro

// Status: Aguardando (Cinza)
const Color statusPending = Color(0xFF9E9E9E);       // Cinza
const Color statusPendingBg = Color(0x1A9E9E9E);     // Cinza translúcido
```

### Esqueleto Corporal (Overlay)

```dart
// Linhas do esqueleto
const Color skeletonLine = Color(0xFFFFFFFF);        // Branco
const Color skeletonLineCorrect = Color(0xFF4CAF50); // Verde quando correto
const Color skeletonLineIncorrect = Color(0xFFF44336); // Vermelho quando incorreto

// Pontos (landmarks)
const Color skeletonPoint = Color(0xFF2196F3);       // Azul
const Color skeletonPointCorrect = Color(0xFF4CAF50); // Verde
const Color skeletonPointIncorrect = Color(0xFFF44336); // Vermelho

// Opacidade
const double skeletonOpacity = 0.9;                  // Linhas
const double skeletonPointOpacity = 1.0;             // Pontos
```

---

## 📐 Tipografia

### Font Family

```dart
// Font principal (Roboto - Material Design)
const String fontFamily = 'Roboto';

// Alternativa para acentuação
const String fontFamilyFallback = 'SF Pro Display'; // iOS
// ou 'Segoe UI' para Windows
```

### Tamanhos

```dart
// Títulos
const double fontSizeH1 = 32.0;      // Título principal
const double fontSizeH2 = 24.0;      // Título secundário
const double fontSizeH3 = 20.0;      // Subtítulo
const double fontSizeH4 = 18.0;      // Cabeçalho de seção
const double fontSizeH5 = 16.0;      // Cabeçalho pequeno

// Texto
const double fontSizeBody = 14.0;    // Corpo de texto
const double fontSizeBodySmall = 12.0; // Texto pequeno
const double fontSizeCaption = 10.0; // Legenda

// Pesos
const FontWeight fontWeightBold = FontWeight.w700;
const FontWeight fontWeightMedium = FontWeight.w500;
const FontWeight fontWeightRegular = FontWeight.w400;
```

### Exemplo de Uso

```dart
Text(
  'AVALIAÇÃO',
  style: TextStyle(
    fontFamily: fontFamily,
    fontSize: fontSizeH2,
    fontWeight: fontWeightBold,
    color: textPrimary,
  ),
)
```

---

## 📏 Espaçamentos (Spacing)

```dart
// Sistema de espaçamento baseado em múltiplos de 4
const double spacing4 = 4.0;
const double spacing8 = 8.0;
const double spacing12 = 12.0;
const double spacing16 = 16.0;
const double spacing20 = 20.0;
const double spacing24 = 24.0;
const double spacing32 = 32.0;
const double spacing40 = 40.0;
const double spacing48 = 48.0;
const double spacing64 = 64.0;
```

### Uso

```dart
Padding(
  padding: EdgeInsets.all(spacing16),
  child: Column(
    children: [
      Widget1(),
      SizedBox(height: spacing12),
      Widget2(),
    ],
  ),
)
```

---

## 🧩 Componentes

### 1. **Feedback Card**

Card que muda de cor baseado no status da avaliação.

```dart
class FeedbackCard extends StatelessWidget {
  final String feedback;
  final EvaluationStatus status; // correct, incorrect, warning, pending

  @override
  Widget build(BuildContext context) {
    Color bgColor = _getStatusColor(status);
    Color borderColor = _getStatusBorderColor(status);
    Color textColor = _getStatusTextColor(status);

    return Container(
      padding: EdgeInsets.all(spacing16),
      decoration: BoxDecoration(
        color: bgColor,
        border: Border.all(color: borderColor, width: 2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        feedback,
        style: TextStyle(
          color: textColor,
          fontSize: fontSizeBody,
          fontWeight: fontWeightMedium,
        ),
      ),
    );
  }

  Color _getStatusColor(EvaluationStatus status) {
    switch (status) {
      case EvaluationStatus.correct:
        return statusCorrectBg;
      case EvaluationStatus.incorrect:
        return statusIncorrectBg;
      case EvaluationStatus.warning:
        return statusWarningBg;
      default:
        return statusPendingBg;
    }
  }
  
  // ... outros métodos
}
```

### 2. **Pose Selector**

Lista de poses selecionáveis.

```dart
class PoseSelector extends StatelessWidget {
  final String selectedPose;
  final Function(String) onPoseSelected;

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemCount: poses.length,
      itemBuilder: (context, index) {
        final pose = poses[index];
        final isSelected = pose.mode == selectedPose;

        return InkWell(
          onTap: () => onPoseSelected(pose.mode),
          child: Container(
            padding: EdgeInsets.all(spacing12),
            margin: EdgeInsets.symmetric(vertical: spacing4),
            decoration: BoxDecoration(
              color: isSelected ? primaryColor.withOpacity(0.2) : cardDark,
              border: Border.all(
                color: isSelected ? primaryColor : Colors.transparent,
                width: 2,
              ),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                Container(
                  width: 24,
                  height: 24,
                  decoration: BoxDecoration(
                    color: isSelected ? primaryColor : statusPending,
                    shape: BoxShape.circle,
                  ),
                  child: Center(
                    child: Text(
                      '${index + 1}',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: fontSizeBodySmall,
                        fontWeight: fontWeightBold,
                      ),
                    ),
                  ),
                ),
                SizedBox(width: spacing12),
                Text(
                  pose.name,
                  style: TextStyle(
                    color: isSelected ? primaryColor : textPrimary,
                    fontSize: fontSizeBody,
                    fontWeight: isSelected ? fontWeightBold : fontWeightRegular,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
```

### 3. **Skeleton Overlay**

Overlay do esqueleto corporal sobre a câmera.

```dart
class SkeletonOverlay extends CustomPainter {
  final List<LandmarkPoint> landmarks;
  final EvaluationStatus status;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = _getSkeletonColor(status)
      ..strokeWidth = 2.0
      ..style = PaintingStyle.stroke;

    final pointPaint = Paint()
      ..color = _getPointColor(status)
      ..style = PaintingStyle.fill;

    // Desenha conexões do esqueleto
    _drawConnections(canvas, paint);

    // Desenha pontos (landmarks)
    _drawLandmarks(canvas, pointPaint);
  }

  Color _getSkeletonColor(EvaluationStatus status) {
    switch (status) {
      case EvaluationStatus.correct:
        return skeletonLineCorrect;
      case EvaluationStatus.incorrect:
        return skeletonLineIncorrect;
      default:
        return skeletonLine;
    }
  }

  void _drawConnections(Canvas canvas, Paint paint) {
    // Conexões do MediaPipe POSE_CONNECTIONS
    // ... implementação
  }

  void _drawLandmarks(Canvas canvas, Paint paint) {
    for (final landmark in landmarks) {
      canvas.drawCircle(
        Offset(landmark.x, landmark.y),
        4.0, // raio
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(SkeletonOverlay oldDelegate) {
    return landmarks != oldDelegate.landmarks || status != oldDelegate.status;
  }
}
```

### 4. **Metric Card**

Card para exibir métricas numéricas.

```dart
class MetricCard extends StatelessWidget {
  final String label;
  final double value;
  final String unit;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(spacing16),
      decoration: BoxDecoration(
        color: cardDark,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: TextStyle(
              color: textSecondary,
              fontSize: fontSizeCaption,
            ),
          ),
          SizedBox(height: spacing4),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                value.toStringAsFixed(1),
                style: TextStyle(
                  color: color ?? textPrimary,
                  fontSize: fontSizeH3,
                  fontWeight: fontWeightBold,
                ),
              ),
              if (unit.isNotEmpty) ...[
                SizedBox(width: spacing4),
                Padding(
                  padding: EdgeInsets.only(bottom: 4),
                  child: Text(
                    unit,
                    style: TextStyle(
                      color: textSecondary,
                      fontSize: fontSizeBodySmall,
                    ),
                  ),
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }
}
```

### 5. **FPS Indicator**

Indicador de FPS discreto.

```dart
class FPSIndicator extends StatelessWidget {
  final int fps;

  @override
  Widget build(BuildContext context) {
    final color = fps >= 28 ? statusCorrect : (fps >= 20 ? statusWarning : statusIncorrect);

    return Container(
      padding: EdgeInsets.symmetric(horizontal: spacing8, vertical: spacing4),
      decoration: BoxDecoration(
        color: backgroundDark.withOpacity(0.8),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        'FPS: $fps',
        style: TextStyle(
          color: color,
          fontSize: fontSizeCaption,
          fontWeight: fontWeightMedium,
          fontFeatures: [FontFeature.tabularFigures()], // Números monoespaçados
        ),
      ),
    );
  }
}
```

---

## 📱 Layouts

### Layout Principal (Desktop/Tablet)

```
┌─────────────────────────────────────────────────────────┐
│  ┌─────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │             │  │                  │  │            │ │
│  │   POSE      │  │                  │  │ AVALIAÇÃO  │ │
│  │  SELECTOR   │  │   CAMERA FEED    │  │            │ │
│  │             │  │   + Skeleton     │  │ ┌────────┐ │ │
│  │  [1] Pose 1 │  │                  │  │ │Status  │ │ │
│  │  [2] Pose 2 │  │                  │  │ │Card    │ │ │
│  │  [3] Pose 3 │  │   [FPS: 30]      │  │ │(Verde/ │ │ │
│  │  [4] Pose 4 │  │                  │  │ │Vermelho│ │ │
│  │  [5] Pose 5 │  │                  │  │ └────────┘ │ │
│  │             │  │                  │  │            │ │
│  │             │  │                  │  │ Feedback:  │ │
│  │             │  │                  │  │ "Usuário   │ │
│  │             │  │                  │  │  bem       │ │
│  │             │  │                  │  │  centrali- │ │
│  │             │  │                  │  │  zado"     │ │
│  │             │  │                  │  │            │ │
│  │             │  │                  │  │ Métricas:  │ │
│  │             │  │                  │  │ • Simetria │ │
│  │             │  │                  │  │ • Ângulos  │ │
│  └─────────────┘  └──────────────────┘  └────────────┘ │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  INSTRUÇÕES                                       │ │
│  │  [V] POSE CORRETA  |  [X] POSE INCORRETA        │ │
│  └───────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Layout Mobile (Portrait)

```
┌─────────────────────┐
│                     │
│   CAMERA FEED       │
│   + Skeleton        │
│                     │
│   [FPS: 30]         │
│                     │
├─────────────────────┤
│                     │
│  ┌────────────────┐ │
│  │  Status Card   │ │
│  │  (Verde/Verm.) │ │
│  └────────────────┘ │
│                     │
│  Feedback:          │
│  "Usuário bem..."   │
│                     │
├─────────────────────┤
│  POSE SELECTOR      │
│  [1] [2] [3] [4] [5]│
│                     │
├─────────────────────┤
│  MÉTRICAS           │
│  • Simetria: 95%    │
│  • Ângulos: OK      │
│                     │
└─────────────────────┘
```

---

## 🎭 Animações

### Transições de Status

```dart
// Anima suave mudança de cor no feedback card
AnimatedContainer(
  duration: Duration(milliseconds: 300),
  curve: Curves.easeInOut,
  decoration: BoxDecoration(
    color: _getStatusColor(status),
    // ...
  ),
)
```

### Fade In/Out

```dart
// Feedback aparece suavemente
AnimatedOpacity(
  opacity: feedback.isEmpty ? 0.0 : 1.0,
  duration: Duration(milliseconds: 200),
  child: FeedbackCard(feedback: feedback),
)
```

### Skeleton Pulse (quando aguardando)

```dart
// Piscar sutil quando aguardando detecção
AnimatedOpacity(
  opacity: _pulseValue,
  duration: Duration(milliseconds: 1000),
  curve: Curves.easeInOut,
  child: SkeletonOverlay(landmarks: landmarks),
)
```

---

## 📱 Responsividade

### Breakpoints

```dart
// Mobile
const double mobileMaxWidth = 600;

// Tablet
const double tabletMaxWidth = 1200;

// Desktop
const double desktopMinWidth = 1200;
```

### Layout Adaptativo

```dart
LayoutBuilder(
  builder: (context, constraints) {
    if (constraints.maxWidth < mobileMaxWidth) {
      return MobileLayout();
    } else if (constraints.maxWidth < tabletMaxWidth) {
      return TabletLayout();
    } else {
      return DesktopLayout();
    }
  },
)
```

---

## ✅ Checklist de Implementação

- [ ] Definir cores no tema do Flutter
- [ ] Criar componentes base (FeedbackCard, PoseSelector, etc.)
- [ ] Implementar SkeletonOverlay
- [ ] Layout responsivo
- [ ] Animações de transição
- [ ] Testes de contraste (acessibilidade)
- [ ] Testes em diferentes tamanhos de tela
- [ ] Documentação de componentes

---

**Documento v1.0** - Data: 2024
**Status**: Design system proposto para implementação

