#!/bin/bash
# Setup script para transactions-service con Saga Pattern

set -e

echo "🚀 Initializing Transactions Service with Saga Pattern..."

# 1. Install dependencies
echo "📦 Installing dependencies..."
poetry install

# 2. Create database tables
echo "🗄️  Running migrations..."
poetry run python manage.py migrate --settings=transactions_service.settings

# 3. Info
echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo ""
echo "1. Start Redis (if not running):"
echo "   docker run -d -p 6379:6379 redis:latest"
echo ""
echo "2. Start Celery worker (Terminal 1):"
echo "   poetry run celery -A tasks.saga_tasks worker --loglevel=info --beat"
echo ""
echo "3. Start Django server (Terminal 2):"
echo "   poetry run python manage.py runserver 0.0.0.0:8003"
echo ""
echo "4. Run tests (Terminal 3):"
echo "   poetry run python manage.py test transactions.test_saga --settings=transactions_service.settings_test -v 2"
echo ""
echo "5. Test Saga with cURL:"
echo "   curl -X POST http://localhost:8003/api/transactions/transfer \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"idempotency_key\":\"test-001\",\"payer_user_id\":\"user_a\",\"payee_user_id\":\"user_b\",\"amount\":\"100.00\"}'"
echo ""
