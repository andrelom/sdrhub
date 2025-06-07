#!/bin/bash
set -e

MODEL_PATH="/app/models/silero_vad.jit"

# Verifica e baixa modelo Silero VAD se necessário
if [ ! -f "$MODEL_PATH" ]; then
  echo "[INIT] Baixando modelo Silero VAD..."
  mkdir -p /app/models
  curl -L -o "$MODEL_PATH" https://github.com/snakers4/silero-vad/raw/master/files/silero_vad.jit
else
  echo "[INIT] Modelo Silero VAD já presente."
fi

# Executa aplicação principal
exec python -u app/__main__.py "$@"
