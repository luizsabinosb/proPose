#!/bin/bash

# Script para limpar completamente o build do Flutter macOS

INTERFACE_DIR="interface"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧹 Limpando build do Flutter macOS...${NC}"

cd "$INTERFACE_DIR" || exit 1

# Limpar build do Flutter
echo -e "${YELLOW}Removendo build do Flutter...${NC}"
flutter clean

# Remover pasta build completamente
echo -e "${YELLOW}Removendo pasta build...${NC}"
rm -rf build/macos
rm -rf build

# Remover arquivo .app específico se existir
echo -e "${YELLOW}Removendo arquivos .app...${NC}"
find . -type d -name "*.app" -exec rm -rf {} + 2>/dev/null || true

# Remover resource forks e metadados
echo -e "${YELLOW}Removendo resource forks e metadados...${NC}"
find . -type f -name "._*" -delete 2>/dev/null || true
find . -type f -name ".DS_Store" -delete 2>/dev/null || true

# Limpar atributos estendidos
echo -e "${YELLOW}Limpando atributos estendidos...${NC}"
if [ -d "build" ]; then
    find build -type f -exec xattr -c {} \; 2>/dev/null || true
    find build -type d -exec xattr -c {} \; 2>/dev/null || true
fi

# Limpar pods (opcional - descomente se necessário)
# echo -e "${YELLOW}Removendo pods...${NC}"
# cd macos
# rm -rf Pods Podfile.lock
# cd ..

echo -e "${GREEN}✅ Limpeza concluída!${NC}"
echo ""
echo "Agora você pode executar: ./rodar_macos.sh"
