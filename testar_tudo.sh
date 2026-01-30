#!/bin/bash
# Script para testar o projeto completo BodyVision

echo "🧪 Teste Completo do BodyVision"
echo "================================"
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para testar backend
test_backend() {
    echo -e "${YELLOW}📡 Testando Backend...${NC}"
    
    # Verifica se o backend está rodando
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend está rodando${NC}"
        
        # Testa endpoint de seleção
        echo "   Testando seleção de pose..."
        RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/pose/select \
            -H "Content-Type: application/json" \
            -d '{"pose_mode": "side_chest"}')
        
        if echo "$RESPONSE" | grep -q "success"; then
            echo -e "${GREEN}   ✅ Endpoint de seleção funcionando${NC}"
        else
            echo -e "${RED}   ❌ Endpoint de seleção com problema${NC}"
        fi
        
        return 0
    else
        echo -e "${RED}❌ Backend não está rodando${NC}"
        echo "   💡 Execute: cd backend && ./iniciar_backend.sh"
        return 1
    fi
}

# Função para verificar Flutter
test_flutter() {
    echo -e "${YELLOW}📱 Verificando Flutter...${NC}"
    
    if command -v flutter &> /dev/null; then
        echo -e "${GREEN}✅ Flutter instalado${NC}"
        
        # Verifica se está na pasta interface
        if [ -d "interface" ]; then
            cd interface
            
            # Verifica dependências
            if [ -d ".dart_tool" ] || [ -f "pubspec.lock" ]; then
                echo -e "${GREEN}   ✅ Dependências Flutter instaladas${NC}"
            else
                echo -e "${YELLOW}   ⚠️ Execute: flutter pub get${NC}"
            fi
            
            cd ..
        else
            echo -e "${RED}   ❌ Pasta interface não encontrada${NC}"
        fi
    else
        echo -e "${RED}❌ Flutter não encontrado${NC}"
        echo "   💡 Instale Flutter: https://flutter.dev/docs/get-started/install"
    fi
}

# Função para verificar estrutura
test_structure() {
    echo -e "${YELLOW}📁 Verificando estrutura do projeto...${NC}"
    
    DIRS=("backend" "interface" "treinamento" "bodyvision" "poseInfo")
    ALL_OK=true
    
    for dir in "${DIRS[@]}"; do
        if [ -d "$dir" ]; then
            echo -e "${GREEN}   ✅ $dir/${NC}"
        else
            echo -e "${RED}   ❌ $dir/ não encontrado${NC}"
            ALL_OK=false
        fi
    done
    
    if [ "$ALL_OK" = true ]; then
        return 0
    else
        return 1
    fi
}

# Função para obter IP local
get_local_ip() {
    LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ifconfig en0 2>/dev/null | grep "inet " | awk '{print $2}')
    
    if [ -z "$LOCAL_IP" ]; then
        LOCAL_IP="localhost"
    fi
    
    echo "$LOCAL_IP"
}

# Main
echo "1️⃣ Verificando estrutura..."
test_structure
echo ""

echo "2️⃣ Verificando Flutter..."
test_flutter
echo ""

echo "3️⃣ Testando Backend..."
test_backend
BACKEND_OK=$?
echo ""

# Resumo
echo "================================"
echo "📊 Resumo dos Testes"
echo "================================"

if [ $BACKEND_OK -eq 0 ]; then
    LOCAL_IP=$(get_local_ip)
    echo -e "${GREEN}✅ Backend: OK${NC}"
    echo "   🌐 Local: http://localhost:8000"
    echo "   🌐 Rede:  http://${LOCAL_IP}:8000"
    echo "   📚 Docs:  http://localhost:8000/docs"
else
    echo -e "${RED}❌ Backend: Não está rodando${NC}"
fi

echo ""
echo "💡 Próximos passos:"
echo "   1. Se o backend não está rodando:"
echo "      cd backend && ./iniciar_backend.sh"
echo ""
echo "   2. Para iniciar a interface Flutter:"
echo "      cd interface && flutter run"
echo ""
echo "   3. Configure o IP no Flutter:"
echo "      Edite: interface/lib/data/api/api_client.dart"
echo "      Use o IP: ${LOCAL_IP}"
echo ""
echo "📖 Veja COMO_TESTAR_COMPLETO.md para guia detalhado"
