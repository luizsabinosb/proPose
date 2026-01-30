#!/bin/bash

# Script para remover arquivo .app problemático antes do build

echo "🧹 Removendo arquivo .app problemático..."

# Remove o arquivo .app específico que está causando problemas
rm -rf build/macos/Build/Products/Debug/ProPosing.app 2>/dev/null
rm -rf build/macos/Build/Products/Debug/bodyvision.app 2>/dev/null

# Remove todos os .app no diretório build
find build -type d -name "*.app" -exec rm -rf {} + 2>/dev/null || true

# Limpa atributos estendidos
if [ -d "build" ]; then
    find build -type f -exec xattr -c {} \; 2>/dev/null || true
    find build -type d -exec xattr -c {} \; 2>/dev/null || true
fi

echo "✅ Limpeza concluída"
