#!/bin/bash
# Script para limpiar caché y reiniciar la aplicación web

echo "🧹 Limpiando caché de Python..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

echo "✓ Caché limpiado"
echo ""
echo "🚀 Iniciando aplicación web..."
echo "   Presiona Ctrl+C para detener"
echo ""

streamlit run interfaces/web_app.py --server.headless true
