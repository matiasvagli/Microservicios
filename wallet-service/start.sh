#!/bin/bash
# start.sh — inicia Django + consumer RabbitMQ

echo "🚀 Iniciando Wallet Service y RabbitMQ consumer..."

# Arranca Django en segundo plano
poetry run python manage.py runserver 0.0.0.0:8002 &


# Espera unos segundos para asegurar que RabbitMQ esté listo
sleep 10

# Arranca el consumer en segundo plano
export PYTHONPATH=/app
poetry run python wallets/services/consumer.py &

# Espera a que ambos procesos terminen
wait
