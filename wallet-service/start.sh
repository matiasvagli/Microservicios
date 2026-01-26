#!/bin/bash
# start.sh — inicia Django + consumer RabbitMQ

echo "🚀 Iniciando Wallet Service y RabbitMQ consumer..."

# Configurar PYTHONPATH al inicio
export PYTHONPATH=/app


# Variables para rastrear los PID de los consumers
CONSUMER_PID=""
PAYMENT_CONSUMER_PID=""
TRANSACTION_CONSUMER_PID=""


# Función para iniciar el consumer principal
start_consumer() {
    if [ ! -z "$CONSUMER_PID" ]; then
        kill $CONSUMER_PID 2>/dev/null || true
    fi
    echo "📥 Iniciando RabbitMQ consumer..."
    PYTHONPATH=/app DJANGO_SETTINGS_MODULE=wallet_service.settings \
    python -u wallets/services/consumer.py 2>&1 | tee /app/consumer.log &
    CONSUMER_PID=$!
    echo "Consumer iniciado con PID: $CONSUMER_PID"
}

# Función para iniciar el payment consumer
start_payment_consumer() {
    if [ ! -z "$PAYMENT_CONSUMER_PID" ]; then
        kill $PAYMENT_CONSUMER_PID 2>/dev/null || true
    fi
    echo "💳 Iniciando Payment Consumer..."
    PYTHONPATH=/app DJANGO_SETTINGS_MODULE=wallet_service.settings \
    python -u wallets/services/payment_consumer.py 2>&1 | tee /app/payment_consumer.log &
    PAYMENT_CONSUMER_PID=$!
    echo "PaymentConsumer iniciado con PID: $PAYMENT_CONSUMER_PID"
}

# Función para iniciar el transaction consumer
start_transaction_consumer() {
    if [ ! -z "$TRANSACTION_CONSUMER_PID" ]; then
        kill $TRANSACTION_CONSUMER_PID 2>/dev/null || true
    fi
    echo "💸 Iniciando Transaction Consumer..."
    PYTHONPATH=/app DJANGO_SETTINGS_MODULE=wallet_service.settings \
    python -u wallets/services/transaction_consumer.py 2>&1 | tee /app/transaction_consumer.log &
    TRANSACTION_CONSUMER_PID=$!
    echo "TransactionConsumer iniciado con PID: $TRANSACTION_CONSUMER_PID"
}


# Función para monitorear y reiniciar los consumers si fallan
monitor_consumers() {
    while true; do
        if [ ! -z "$CONSUMER_PID" ] && ! kill -0 $CONSUMER_PID 2>/dev/null; then
            echo "⚠️ Consumer no está corriendo. Reiniciando..."
            start_consumer
        fi
        if [ ! -z "$PAYMENT_CONSUMER_PID" ] && ! kill -0 $PAYMENT_CONSUMER_PID 2>/dev/null; then
            echo "⚠️ PaymentConsumer no está corriendo. Reiniciando..."
            start_payment_consumer
        fi
        if [ ! -z "$TRANSACTION_CONSUMER_PID" ] && ! kill -0 $TRANSACTION_CONSUMER_PID 2>/dev/null; then
            echo "⚠️ TransactionConsumer no está corriendo. Reiniciando..."
            start_transaction_consumer
        fi
        sleep 5
    done
}


# Función para manejar señales de terminación
cleanup() {
    echo "🛑 Recibida señal de terminación..."
    kill $DJANGO_PID 2>/dev/null || true
    kill $CONSUMER_PID 2>/dev/null || true
    kill $PAYMENT_CONSUMER_PID 2>/dev/null || true
    kill $TRANSACTION_CONSUMER_PID 2>/dev/null || true
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


# Inicia los consumers
start_consumer
start_payment_consumer
start_transaction_consumer

# Inicia el monitor de consumers en segundo plano
monitor_consumers &
MONITOR_PID=$!

# Mantener el script corriendo y esperar por señales
while true; do
    # Verifica si Django sigue corriendo
    if ! kill -0 $DJANGO_PID 2>/dev/null; then
        echo "❌ Django se detuvo inesperadamente"
        cleanup
    fi
    sleep 1
done
