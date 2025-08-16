#!/bin/bash

# Script para iniciar o bot monitor de compras

echo "🤖 Bot Monitor de Compras do Telegram"
echo "===================================="
echo ""

# Verifica se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo "❌ Arquivo .env não encontrado!"
    echo "📝 Copiando .env.example para .env..."
    cp .env.example .env
    echo "✅ Arquivo .env criado!"
    echo ""
    echo "⚠️  IMPORTANTE: Edite o arquivo .env com suas configurações antes de continuar:"
    echo "   - BOT_TOKEN (obrigatório)"
    echo "   - ADMIN_IDS (obrigatório)"
    echo "   - GRUPO_ID (opcional)"
    echo "   - THRESHOLD_COMPRAS (opcional, padrão: 10)"
    echo ""
    echo "Para editar: nano .env"
    exit 1
fi

# Verifica se as dependências estão instaladas
echo "📦 Verificando dependências..."
python3 -c "import telegram, dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Dependências não encontradas! Instalando..."
    pip install -r requirements.txt
    echo "✅ Dependências instaladas!"
fi

echo ""
echo "🚀 Iniciando bot..."
echo "📱 Use Ctrl+C para parar o bot"
echo ""

# Inicia o bot
python3 bot.py
