#!/bin/bash
# Script para configurar Flutter no PATH

FLUTTER_PATH="$HOME/Desktop/BodyVision/interface/flutter/bin"

echo "🔧 Configurando Flutter no PATH..."
echo ""

# Verifica se Flutter existe
if [ ! -f "$FLUTTER_PATH/flutter" ]; then
    echo "❌ Erro: Flutter não encontrado em: $FLUTTER_PATH"
    exit 1
fi

echo "✅ Flutter encontrado!"

# Verifica se já está no .zshrc
if grep -q "interface/flutter/bin" ~/.zshrc 2>/dev/null; then
    echo "⚠️  Flutter já está configurado no .zshrc"
    echo "   Linha encontrada:"
    grep "interface/flutter/bin" ~/.zshrc
else
    echo "📝 Adicionando Flutter ao .zshrc..."
    
    # Adiciona ao final do .zshrc
    echo "" >> ~/.zshrc
    echo "# Flutter PATH - BodyVision" >> ~/.zshrc
    echo "export PATH=\"\$PATH:$HOME/Desktop/BodyVision/interface/flutter/bin\"" >> ~/.zshrc
    
    echo "✅ Flutter adicionado ao .zshrc!"
fi

echo ""
echo "🔄 Para aplicar, execute no terminal:"
echo "   source ~/.zshrc"
echo ""
echo "📋 OU feche e abra um novo terminal"
echo ""
echo "🧪 Depois teste com:"
echo "   flutter --version"

