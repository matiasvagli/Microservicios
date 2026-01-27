# 🚀 Wallet System - Saga Pattern MVP

Sistema de transacciones distribuidas con **Saga Pattern Orquestado**, compensaciones automáticas e idempotencia completa.

## 📋 Quick Links

- [Quick Start (Docker)](#-quick-start-docker)
- [Arquitectura](#-arquitectura)
- [Saga Pattern](#-saga-pattern)
- [API](#-api)
- [Testing](#-testing)

---

## 🐳 Quick Start (Docker)

### Requisitos
- Docker & Docker Compose
- 8GB RAM mínimo

### Levantar TODO

```bash
cd /home/matiasdev/wallet-system
docker-compose up -d
docker-compose ps
```

✅ **Todo funciona junto. Sin terminales separadas.**

### Parar

```bash
docker-compose down -v
```

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    API Gateway (8000)                   │
└─────────────┬───────────────────────────────────────────┘
              │
    ┌─────────┼──────────┬──────────┐
    │         │          │          │
┌───▼──┐  ┌──▼────┐ ┌──▼────┐ ┌──▼────┐
│Auth  │  │Wallet │ │Trans. │ │Paym.  │
│8001  │  │8002   │ │8003   │ │8004   │
└──────┘  └───┬───┘ └───┬───┘ └───────┘
              │         │
          ┌───▼──────┐ ┌┴───────────────────┐
          │Postgres  │ │ SAGA ORCHESTRATOR  │
          │  Wallet  │ │ (Celery + Redis)   │
          └──────────┘ └──┬───────┬─────────┘
                          │       │
                    ┌─────▼─┐    │
                    │ Redis │    │
                    │Celery │    │
                    └───────┘    │
                           ┌─────▼──────┐
                           │ RabbitMQ   │
                           │ (Events)   │
                           └────────────┘
```

---

## 🔄 Saga Pattern

### Flujo de Transferencia

```
POST /transactions/transfer
    ↓ (status: PENDING)
    ↓ (Celery detecta evento ~1s)
    ↓
Saga Orchestrator ejecuta:
  ├─ DEBITING: wallet.debit(payer) ✅
  ├─ CREDITING: wallet.credit(payee)
  │   ├─ ✅ → COMPLETED ✅
  │   └─ ❌ → COMPENSATING: reversa debit ✅ → FAILED ✅
  └─ Si compensación falla → CRITICAL 🚨 (manual review)
```

### Idempotencia (Triple Layer)

**Resultado:** Puedes reintentar ∞ veces sin duplicar

| Layer | Propósito |
|-------|-----------|
| `Transaction.idempotency_key` | No duplicar transfers |
| `debit_idempotency_key` | No duplicar debits |
| `credit_idempotency_key` | No duplicar credits |

### Reintentos (Backoff Exponencial)

```
Intento 1: Inmediato
Intento 2: 60 segundos
Intento 3: 120 segundos
Intento 4: 240 segundos
Intento 5: Dead Letter Queue 🚨
```

---

## 📡 API

### Crear Transferencia

```bash
curl -X POST http://localhost:8003/api/transactions/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "idempotency_key": "test-001",
    "payer_user_id": "user_a",
    "payee_user_id": "user_b",
    "amount": "100.00"
  }'
```

### Ver Transferencia

```bash
curl http://localhost:8003/api/transactions/{id}
```

(Espera 2s → status: COMPLETED ✅)

### Debitar Wallet

```bash
curl -X POST http://localhost:8002/api/wallets/user_a/debit \
  -H "Content-Type: application/json" \
  -d '{"amount": "50.00", "idempotency_key": "debit-001"}'
```

### Acreditar Wallet

```bash
curl -X POST http://localhost:8002/api/wallets/user_b/credit \
  -H "Content-Type: application/json" \
  -d '{"amount": "50.00", "idempotency_key": "credit-001"}'
```

---

## 🧪 Testing

### Tests Saga (7 cases)

```bash
docker-compose exec transactions-service \
  poetry run python manage.py test transactions.test_saga \
  --settings=transactions_service.settings_test -v 2
```

**Esperado:** `Ran 7 tests - OK ✅`

### Tests Wallet (9 cases)

```bash
docker-compose exec wallet-service \
  poetry run python manage.py test wallets.test_operations -v 2
```

**Esperado:** `Ran 9 tests - OK ✅`

### Test End-to-End

```bash
# 1. Crear transfer
curl -X POST http://localhost:8003/api/transactions/transfer \
  -H "Content-Type: application/json" \
  -d '{"idempotency_key":"test-1","payer_user_id":"user_a","payee_user_id":"user_b","amount":"100.00"}'

# 2. Esperar 2s
sleep 2

# 3. Verificar
curl http://localhost:8003/api/transactions | jq '.[] | {status, saga_step}'
# Esperado: {"status": "COMPLETED", "saga_step": "COMPLETED"}
```

---

## 📊 Servicios & Puertos

| Servicio | Puerto | Status |
|----------|--------|--------|
| API Gateway | 8000 | 🟢 |
| Auth Service | 8001 | 🟢 |
| Wallet Service | 8002 | 🟢 |
| **Transactions Service** | **8003** | **🟢 + SAGA** |
| Payment Service | 8004 | 🟢 |
| RabbitMQ | 5672 | 🟢 |
| RabbitMQ Admin | 15672 | 🟢 |
| **Redis (Celery)** | **6379** | **🟢** |
| Postgres (Wallet) | 5544 | 🟢 |
| Postgres (Trans.) | 5545 | 🟢 |
| MongoDB | 27018 | 🟢 |

---

## 🔍 Monitoreo

### RabbitMQ Admin
```
http://localhost:15672
guest / guest
```

### Logs en Tiempo Real

```bash
# Saga processor
docker-compose logs -f transactions-worker

# Scheduler
docker-compose logs -f transactions-beat

# Todos
docker-compose logs -f
```

### Base de Datos

```bash
# Conectar a Transactions DB
psql -h localhost -p 5545 -U trans_user -d transactions_db

# Ver transacciones
SELECT id, status, saga_step FROM transactions_transaction;

# Ver eventos
SELECT topic, created_at, published_at FROM transactions_outbox;
```

---

## ⚙️ Configuración

**Automático en docker-compose.yml**

Variables más importantes:
- `WALLET_SERVICE_URL=http://wallet-service:8002`
- `CELERY_BROKER_URL=redis://redis:6379/0`
- `DB_HOST=transactions-db`

---

## 🆘 Troubleshooting

### "transactions-service no levanta"
```bash
docker-compose logs transactions-service
docker-compose exec transactions-service \
  poetry run python manage.py migrate --settings=transactions_service.settings
```

### "Celery no procesa"
```bash
docker-compose exec redis redis-cli ping
# Respuesta: PONG
docker-compose logs transactions-worker
```

### Reset completo
```bash
docker-compose down -v && docker-compose up -d
```

---

## ✨ Características

✅ Saga Pattern Orquestado
✅ Compensaciones Automáticas
✅ Idempotencia Triple-Layer
✅ Reintentos Exponenciales
✅ Dead Letter Queue
✅ 16+ Tests Completos
✅ Docker Compose Ready
✅ Documentación

---


**Última actualización:** 26 Enero 2026

