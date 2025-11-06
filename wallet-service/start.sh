#!/bin/bash
# start.sh — inicia Django + consumer RabbitMQ

echo "🚀 Iniciando Wallet Service y RabbitMQ consumer..."

# Configurar PYTHONPATH al inicio
export PYTHONPATH=/app

# Variable para rastrear el PID del consumer
CONSUMER_PID=""

# Función para iniciar el consumer
start_consumer() {
    if [ ! -z "$CONSUMER_PID" ]; then
        kill $CONSUMER_PID 2>/dev/null || true
    fi
    echo "📥 Iniciando RabbitMQ consumer..."
    
    # Ejecutar el consumer directamente con la configuración del entorno
    PYTHONPATH=/app DJANGO_SETTINGS_MODULE=wallet_service.settings \
    python -u wallets/services/consumer.py 2>&1 | tee /app/consumer.log &
    
    CONSUMER_PID=$!
    echo "Consumer iniciado con PID: $CONSUMER_PID"
}

# Función para monitorear y reiniciar el consumer si falla
monitor_consumer() {
    while true; do
        if [ ! -z "$CONSUMER_PID" ] && ! kill -0 $CONSUMER_PID 2>/dev/null; then
            echo "⚠️ Consumer no está corriendo. Reiniciando..."
            start_consumer
        fi
        sleep 5
    done
}

# Función para manejar señales de terminación
cleanup() {
    echo "🛑 Recibida señal de terminación..."
    kill $DJANGO_PID 2>/dev/null || true
    kill $CONSUMER_PID 2>/dev/null || true
    kill $MONITOR_PID 2>/dev/null || true
    exit 0
}

# Registra el handler para señales
trap cleanup SIGTERM SIGINT

# Arranca Django en segundo plano
echo "🌐 Iniciando Django server..."
poetry run python manage.py runserver 0.0.0.0:8002 &
DJANGO_PID=$!
echo "Django iniciado con PID: $DJANGO_PID"

# Espera unos segundos para asegurar que RabbitMQ esté listo
echo "⏳ Esperando a que RabbitMQ esté listo..."
sleep 10

# Inicia el monitor del consumer en segundo plano
monitor_consumer &
MONITOR_PID=$!

# Inicia el consumer inicial
start_consumer

# Mantener el script corriendo y esperar por señales
while true; do
    # Verifica si Django sigue corriendo
    if ! kill -0 $DJANGO_PID 2>/dev/null; then
        echo "❌ Django se detuvo inesperadamente"
        cleanup
    fi
    sleep 1
done
