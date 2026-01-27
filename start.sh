#!/bin/bash
# 🚀 Wallet System - Saga Pattern MVP
# Simple one-liner setup

set -e

echo "🚀 Wallet System - Saga Pattern MVP"
echo "===================================="
echo ""

cd /home/matiasdev/wallet-system

echo "📦 Building and starting all services..."
docker compose up -d

echo ""
echo "✅ All services started!"
echo ""
echo "📋 Status:"
docker compose ps --services

echo ""
echo "🔗 Access points:"
echo "  - API Gateway: http://localhost:8000"
echo "  - Auth Service: http://localhost:8001"
echo "  - Wallet Service: http://localhost:8002"
echo "  - Transactions Service: http://localhost:8003 (with Saga Pattern)"
echo "  - Payment Service: http://localhost:8004"
echo "  - RabbitMQ Admin: http://localhost:15672 (guest/guest)"
echo ""
echo "🧪 Test Saga (after 3s for DB migrations):"
echo ""
echo "   curl -X POST http://localhost:8003/api/transactions/transfer \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"idempotency_key\":\"test-1\",\"payer_user_id\":\"user_a\",\"payee_user_id\":\"user_b\",\"amount\":\"100.00\"}'"
echo ""
echo "📖 Read README.md for full documentation"
echo ""
echo "🛑 Stop: docker compose down -v"
echo ""
