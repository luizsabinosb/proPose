#!/bin/bash
# =============================================================================
# Build ProPosing - Executável completo (Backend + Interface)
# Não altera o código core (backend/app, proposing, treinamento)
# =============================================================================

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DIST_DIR="$PROJECT_DIR/dist"
BUILD_DIR="$PROJECT_DIR/build_app"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║     ProPosing - Build Executável Completo              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "\n${YELLOW}1. Verificando dependências...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 não encontrado${NC}"
    exit 1
fi

if ! command -v flutter &> /dev/null; then
    echo -e "${RED}❌ Flutter não encontrado${NC}"
    exit 1
fi

if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo -e "${YELLOW}   Instalando PyInstaller...${NC}"
    pip3 install pyinstaller
fi

echo -e "${YELLOW}   Instalando dependências do backend (para o bundle)...${NC}"
pip3 install -r "$PROJECT_DIR/backend/requirements.txt" -q

echo -e "\n${YELLOW}2. Empacotando Backend com PyInstaller...${NC}"

cd "$PROJECT_DIR"
rm -rf build dist 2>/dev/null || true
pyinstaller --clean --noconfirm config/proposing_build.spec

if [ ! -f "dist/proposing-backend" ]; then
    echo -e "${RED}❌ Backend não foi gerado${NC}"
    exit 1
fi
echo -e "${GREEN}   ✅ Backend empacotado: dist/proposing-backend${NC}"

echo -e "\n${YELLOW}3. Build da Interface Flutter (macOS)...${NC}"

cd "$PROJECT_DIR/interface"

if [ -f "$SCRIPT_DIR/limpar_flutter_macos.sh" ]; then
    echo -e "${YELLOW}   Limpando build Flutter...${NC}"
    bash "$SCRIPT_DIR/limpar_flutter_macos.sh"
else
    echo -e "${YELLOW}   Limpando resource forks...${NC}"
    flutter clean 2>/dev/null || true
    find . -type f -exec xattr -c {} \; 2>/dev/null || true
fi

flutter pub get
flutter build macos --release

FLUTTER_APP=""
for app in "$PROJECT_DIR/interface/build/macos/Build/Products/Release/"*.app; do
    if [ -d "$app" ]; then
        FLUTTER_APP="$app"
        break
    fi
done

if [ -z "$FLUTTER_APP" ] || [ ! -d "$FLUTTER_APP" ]; then
    echo -e "${RED}❌ Flutter app não encontrado${NC}"
    exit 1
fi

APP_NAME=$(basename "$FLUTTER_APP" .app)
echo -e "${GREEN}   ✅ Interface gerada: $FLUTTER_APP${NC}"

echo -e "\n${YELLOW}4. Montando ProPosing.app unificado...${NC}"

mkdir -p "$BUILD_DIR"
FINAL_APP="$BUILD_DIR/ProPosing.app"
rm -rf "$FINAL_APP" 2>/dev/null || true

cp -R "$FLUTTER_APP" "$FINAL_APP"
MACOS_DIR="$FINAL_APP/Contents/MacOS"

cp "$PROJECT_DIR/dist/proposing-backend" "$MACOS_DIR/"

FLUTTER_BIN=""
for f in "$MACOS_DIR"/*; do
    if [ -f "$f" ] && [ -x "$f" ] && [[ "$(basename "$f")" != "proposing-backend" ]] && [[ "$(basename "$f")" != "proposing-launcher" ]]; then
        FLUTTER_BIN="$f"
        break
    fi
done

if [ -z "$FLUTTER_BIN" ]; then
    FLUTTER_BIN="$MACOS_DIR/$APP_NAME"
fi

FLUTTER_BIN_NAME=$(basename "$FLUTTER_BIN")
mv "$FLUTTER_BIN" "$MACOS_DIR/proposing-flutter"

cat > "$MACOS_DIR/proposing-launcher" << 'LAUNCHER'
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"

"$DIR/proposing-backend" &
BACKEND_PID=$!

for i in {1..20}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        break
    fi
    sleep 0.5
done

cleanup() {
    kill $BACKEND_PID 2>/dev/null || true
}
trap cleanup EXIT

"$DIR/proposing-flutter"
LAUNCHER

chmod +x "$MACOS_DIR/proposing-launcher"
chmod +x "$MACOS_DIR/proposing-backend"

PLIST="$FINAL_APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Set :CFBundleExecutable proposing-launcher" "$PLIST" 2>/dev/null || true
/usr/libexec/PlistBuddy -c "Set :CFBundleName ProPosing" "$PLIST" 2>/dev/null || true

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Build concluído com sucesso!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📦 Aplicativo em: ${FINAL_APP}${NC}"
echo ""
echo -e "${YELLOW}Para executar:${NC}"
echo "   open \"$FINAL_APP\""
echo ""
echo -e "${YELLOW}Para distribuir:${NC}"
echo "   Comprima a pasta: zip -r ProPosing.zip \"$FINAL_APP\""
echo ""
