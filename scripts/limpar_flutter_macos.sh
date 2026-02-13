#!/bin/bash
# Script unificado de limpeza para build Flutter macOS
# Resolve problemas de CodeSign (resource fork, atributos estendidos)
# Uso: ./scripts/limpar_flutter_macos.sh  (a partir da raiz do projeto)

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
INTERFACE_DIR="$PROJECT_DIR/interface"

cd "$INTERFACE_DIR" || exit 1

echo -e "${BLUE}🧹 Limpeza Flutter macOS...${NC}"
echo ""

echo -e "${YELLOW}[1/5] flutter clean...${NC}"
flutter clean 2>/dev/null || true

echo -e "${YELLOW}[2/5] Removendo pastas de build...${NC}"
rm -rf build .dart_tool/build .flutter-plugins-dependencies .dart_tool/package_config.json .packages 2>/dev/null || true

echo -e "${YELLOW}[3/5] Removendo arquivos .app...${NC}"
find . -type d -name "*.app" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.app" -delete 2>/dev/null || true

echo -e "${YELLOW}[4/5] Removendo resource forks e .DS_Store...${NC}"
find . -type f -name "._*" -delete 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true

echo -e "${YELLOW}[5/5] Limpando atributos estendidos (xattr)...${NC}"
find . -type f -exec xattr -c {} \; 2>/dev/null || true
find . -type d -exec xattr -c {} \; 2>/dev/null || true

echo ""
echo -e "${GREEN}✅ Limpeza concluída!${NC}"
echo ""
echo "Próximos passos (execute a partir da raiz do projeto):"
echo "  ./scripts/rodar_macos.sh       # Rodar app macOS"
echo "  ./scripts/build_executable.sh  # Build executável completo"
echo ""
