#!/bin/bash
# Script para testar conexão com o backend

echo "🧪 Testando conexão com Backend BodyVision..."
echo ""

# Descobre o IP local
LOCAL_IP=$(ipconfig getifaddr en0 2>/dev/null || ifconfig en0 2>/dev/null | grep "inet " | awk '{print $2}')

if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="192.168.0.134"
    echo "⚠️  Não foi possível detectar IP automaticamente"
    echo "   Usando IP padrão: $LOCAL_IP"
    echo "   Se não funcionar, verifique manualmente com: ifconfig"
    echo ""
fi

echo "📍 Testando conexões..."
echo ""

# Testa localhost
echo "1️⃣  Testando localhost:8000..."
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ localhost funciona!"
    curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/health
else
    echo "   ❌ localhost NÃO está respondendo"
    echo "   ⚠️  Certifique-se de que o backend está rodando!"
fi

echo ""

# Testa IP local
echo "2️⃣  Testando ${LOCAL_IP}:8000..."
if curl -s -f http://${LOCAL_IP}:8000/health > /dev/null 2>&1; then
    echo "   ✅ ${LOCAL_IP} funciona!"
    curl -s http://${LOCAL_IP}:8000/health | python3 -m json.tool 2>/dev/null || curl -s http://${LOCAL_IP}:8000/health
else
    echo "   ❌ ${LOCAL_IP} NÃO está respondendo"
    echo "   💡 Dicas:"
    echo "      - Verifique se o backend está rodando com: ./backend/iniciar_backend.sh"
    echo "      - Verifique se está usando --host 0.0.0.0"
    echo "      - Verifique o firewall do Mac"
fi

echo ""
echo "📝 Para iniciar o backend, execute:"
echo "   cd backend && ./iniciar_backend.sh"
echo ""

