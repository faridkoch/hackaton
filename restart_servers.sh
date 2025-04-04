#!/bin/bash

# Папка, где находятся скрипты
SCRIPT_DIR="./"

# Имена скриптов
WS_SCRIPT="server_websocket.py"
REST_SCRIPT="server_rest.py"

# Убить старые процессы
echo "Stopping existing servers..."
pkill -f $WS_SCRIPT
pkill -f $REST_SCRIPT

# Подождать немного
sleep 1

# Запуск WebSocket сервера
echo "Starting $WS_SCRIPT..."
nohup python3 "$SCRIPT_DIR/$WS_SCRIPT" > "$SCRIPT_DIR/websocket.log" 2>&1 &

# Запуск REST сервера
echo "Starting $REST_SCRIPT..."
nohup python3 "$SCRIPT_DIR/$REST_SCRIPT" > "$SCRIPT_DIR/rest.log" 2>&1 &

echo "✅ Servers restarted."