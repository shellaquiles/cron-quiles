#!/bin/bash
# Script para servir el sitio localmente

cd "$(dirname "$0")"

echo "🚀 Iniciando servidor local..."
echo "📁 Directorio: $(pwd)"
echo ""
echo "🌐 Abre en tu navegador: http://localhost:8000/index.html"
echo "⏹️  Presiona Ctrl+C para detener"
echo ""

# Intentar usar el servidor Python personalizado primero
if [ -f "serve.py" ]; then
    python3 serve.py
else
    # Fallback al servidor HTTP estándar
    python3 -m http.server 8000
fi
