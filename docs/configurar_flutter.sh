#!/bin/bash
# Script para configurar Flutter no PATH

FLUTTER_PATH="$HOME/Desktop/BodyVision/interface/flutter"

echo "🔍 Verificando instalação do Flutter..."

# Verifica se Flutter existe no caminho
if [ ! -d "$FLUTTER_PATH" ]; then
    echo "❌ Flutter não encontrado em: $FLUTTER_PATH"
    echo "   Verifique onde você clonou o Flutter"
    exit 1
fi

echo "✅ Flutter encontrado em: $FLUTTER_PATH"

# Verifica se já está no PATH
if grep -q "flutter/bin" ~/.zshrc 2>/dev/null; then
    echo "⚠️  Flutter já parece estar configurado no .zshrc"
    echo "   Verificando configuração atual..."
else
    echo "📝 Adicionando Flutter ao PATH..."
    
    # Adiciona ao .zshrc
    cat >> ~/.zshrc << EOF

# Flutter PATH
export PATH="\$PATH:$FLUTTER_PATH/bin"
EOF
    
    echo "✅ Flutter adicionado ao .zshrc"
fi

echo ""
echo "🔄 Para aplicar as mudanças, execute:"
echo "   source ~/.zshrc"
echo ""
echo "📋 Ou feche e abra um novo terminal"
echo ""
echo "🧪 Depois, teste com:"
echo "   flutter doctor"

