#!/bin/bash

# --- Script para rodar ProPosing como aplicativo macOS ---

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
INTERFACE_DIR="$PROJECT_DIR/interface"
BACKEND_LOG="$PROJECT_DIR/.backend_macos.log"
BACKEND_PID_FILE="$PROJECT_DIR/.backend_macos_pid"
FLUTTER_PID_FILE="$PROJECT_DIR/.flutter_macos_pid"

# --- Cores para output ---
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# --- Funções Auxiliares ---

log_message() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "Comando '$1' não encontrado. Por favor, instale-o."
        exit 1
    fi
}

check_backend_health() {
    if curl -s http://localhost:8000/health &> /dev/null; then
        return 0
    else
        return 1
    fi
}

start_backend() {
    log_message "Iniciando backend..."

    (
        cd "$BACKEND_DIR" || exit 1

        log_message "Verificando dependências..."
        pip3 install -q -r requirements.txt 2>/dev/null || true

        log_message "Iniciando servidor FastAPI..."
        python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$BACKEND_LOG" 2>&1 &
        echo $! > "$BACKEND_PID_FILE"

        log_success "Backend iniciado (PID: $(cat "$BACKEND_PID_FILE"))"
    )

    log_message "Aguardando backend iniciar..."
    for i in {1..30}; do
        if check_backend_health; then
            log_success "Backend está respondendo!"
            return 0
        fi
        sleep 1
    done

    log_error "Backend não respondeu após 30 segundos"
    return 1
}

stop_backend() {
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        log_message "Encerrando backend (PID: $BACKEND_PID)..."
        kill "$BACKEND_PID" 2>/dev/null
        rm -f "$BACKEND_PID_FILE"
        log_success "Backend encerrado"
    fi
}

cleanup() {
    log_message "🧹 Encerrando processos..."
    stop_backend

    if [ -f "$FLUTTER_PID_FILE" ]; then
        FLUTTER_PID=$(cat "$FLUTTER_PID_FILE")
        log_message "Encerrando Flutter (PID: $FLUTTER_PID)..."
        kill "$FLUTTER_PID" 2>/dev/null
        rm -f "$FLUTTER_PID_FILE"
    fi

    log_success "Limpeza concluída"
    exit 0
}

trap cleanup SIGINT SIGTERM

# --- Início do Script ---
clear
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "                    🚀 ProPosing - Aplicativo macOS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

log_message "Verificando dependências..."
check_command "python3"
check_command "flutter"

log_message "Verificando CocoaPods..."
if ! command -v pod &> /dev/null; then
    log_warning "CocoaPods não encontrado. Instalando..."
    if command -v gem &> /dev/null; then
        sudo gem install cocoapods
        if [ $? -eq 0 ]; then
            log_success "CocoaPods instalado"
        else
            log_error "Falha ao instalar CocoaPods. Instale manualmente: sudo gem install cocoapods"
            exit 1
        fi
    else
        log_error "Ruby/gem não encontrado. Instale CocoaPods manualmente: sudo gem install cocoapods"
        exit 1
    fi
else
    log_success "CocoaPods encontrado"
fi

log_message "Verificando suporte para macOS..."
if ! flutter config --enable-macos-desktop 2>/dev/null; then
    log_warning "Não foi possível habilitar macOS desktop automaticamente"
fi

log_message "Verificando backend..."
if check_backend_health; then
    log_success "Backend já está rodando"
else
    if ! start_backend; then
        log_error "Falha ao iniciar backend. Verifique o log: $BACKEND_LOG"
        exit 1
    fi
fi

log_message "Preparando aplicativo macOS..."
cd "$INTERFACE_DIR" || exit 1

log_message "Verificando dependências do Flutter..."
flutter pub get

if [ -f "$SCRIPT_DIR/limpar_flutter_macos.sh" ]; then
    log_message "Limpando builds anteriores..."
    bash "$SCRIPT_DIR/limpar_flutter_macos.sh"
else
    log_message "Limpando builds anteriores..."
    flutter clean
    rm -rf build .dart_tool/build .flutter-plugins-dependencies
    find . -type f -exec xattr -c {} \; 2>/dev/null || true
fi

log_message "Configurando dependências nativas (CocoaPods)..."
cd macos
if [ ! -d "Pods" ] || [ ! -f "Podfile.lock" ]; then
    log_message "Instalando pods..."
    pod install
    if [ $? -ne 0 ]; then
        log_error "Falha ao instalar pods. Tente manualmente: cd macos && pod install"
        exit 1
    fi
else
    log_success "Pods já instalados"
fi
cd ..

log_message "Limpeza final antes do build..."
if [ -d "build/macos/Build/Products/Debug" ]; then
    rm -rf build/macos/Build/Products/Debug/*.app 2>/dev/null || true
    find build/macos/Build/Products/Debug -type f -exec xattr -c {} \; 2>/dev/null || true
fi

log_message "Executando aplicativo no macOS..."
log_warning "O aplicativo será aberto em uma nova janela"
echo ""

flutter run -d macos &
FLUTTER_PID=$!
echo $FLUTTER_PID > "$FLUTTER_PID_FILE"

sleep 3

if ps -p $FLUTTER_PID > /dev/null; then
    log_success "Aplicativo macOS iniciado (PID: $FLUTTER_PID)"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    log_success "✅ ProPosing está rodando!"
    echo ""
    echo "📱 Aplicativo: Abrindo em uma nova janela do macOS"
    echo "🔧 Backend: http://localhost:8000"
    echo "📚 Docs: http://localhost:8000/docs"
    echo ""
    echo "💡 Para parar o aplicativo, pressione Ctrl+C neste terminal"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    wait $FLUTTER_PID
    FLUTTER_EXIT_CODE=$?

    if [ $FLUTTER_EXIT_CODE -ne 0 ]; then
        log_error "Aplicativo encerrado com erro (código: $FLUTTER_EXIT_CODE)"
    else
        log_success "Aplicativo encerrado normalmente"
    fi
else
    log_error "Falha ao iniciar aplicativo Flutter"
    cleanup
    exit 1
fi

cleanup
