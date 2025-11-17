# Transactions Service — Migration & Next Steps

Resumen y plan corto para continuar el trabajo con `transactions-service`.

Fecha: 17 de Noviembre de 2025

Objetivo:
- Completar la lógica de transferencias (end-to-end) entre billeteras, con consistencia eventual y manejo de errores.
- Preparar la base para un eventual reemplazo parcial o migración a NestJS (si queremos crear `transactions-service1`).

--------

## Lo que hicimos hoy (estado actual)
- API con Django Ninja añadida y montada en `/api/` (`transactions/api.py` y `transactions_service/urls.py`).
- Endpoints implementados:
  - `GET /api/transactions` — lista transacciones (filtro `?user_id=` disponible).
  - `POST /api/transactions/transfer` — crea transacción (manejo básico de idempotencia).
  - `PATCH /api/transactions/{tx_id}/status` — actualiza estado.
  - `GET /api/outbox` — lista events pendientes.
- Esquemas (Pydantic) añadidos: `transactions/schemas.py`.
- Outbox pattern: al crear transacciones y al actualizar estados se crea una fila en `Outbox`.
- Comando de management para publicar outbox a RabbitMQ: `transactions/management/commands/publish_outbox.py` (simula si pika no está instalado).
- Tests añadidos y ejecutados con SQLite en `transactions/tests.py`:
  - Transacción creación
  - Idempotencia
  - Outbox creado
- Settings de test `transactions_service/settings_test.py` que usan sqlite para tests locales.

--------

## Recomendaciones y pasos prioritarios (siguientes acciones)
1) Implementar endpoints `debit` y `credit` en `wallet-service` (DRF):
   - `POST /api/wallets/{user_id}/debit` — intenta debitar un monto (devuelve 200 y nuevo balance, o 400 si insuficiente).
   - `POST /api/wallets/{user_id}/credit` — acredita un monto.
   - Añadir tests para ambos endpoints.
   - Razonamiento: necesitamos que `transactions-service` pueda coordinar el flow debit/credit para completar una transferencia.

2) Integración sincronica para empezar:
   - Actualizar `transactions-service` `POST /transfer` (ya creado) para llamar al API Gateway (o `wallet-service`) y ejecutar `debit` (payer) y `credit` (payee).
   - Si ambos succeed -> actualizar estado `COMPLETED` y crear outbox `transaction.completed`.
   - Si falla -> intentar compensar (ej: si debit succeeded pero credit failed) -> llamar `credit` a payer (reverse) o marcar como `FAILED` y guardar en Outbox.

3) Tests de integración E2E (sin Docker con Gateway):
   - Crear tests que usen la API (o stubs) para simular wallet debit/credit y validar comportamiento end-to-end.

4) Mejorar publicación y consumidor de events:
   - Implementar consumer (o un worker) que consuma de Outbox y publique a RabbitMQ (o que consuma eventos `transaction.created` y ejecute wallet debit/credit asíncrono como Saga).
   - Añadir retries y backoff para publicación y consumo.

5) Diseñar patrón Saga (orquestado o coreografiado):
   - Orquestado: un servicio Saga/Orchestrator administra pasos (debit, credit) y compesaciones.
   - Coreografiado: cada servicio reacciona a eventos y publica la siguiente acción; `transactions-service` se encarga de iniciar/monitorizar.
   - Dejar pruebas con ambos patrones, o al menos un diseño claro para la compensación.

6) Migración a NestJS (opcional):
   - Si queremos mostrar migración: crear `transactions-service1` (NestJS) con la misma API y lógica.
   - Mantener el `transactions-service` en Django hasta que `transactions-service1` esté probado y estable, luego swap y eliminar el viejo.

--------

## Comandos útiles
- Instalar deps e instalar entorno (desde `transactions-service`):
  - `poetry install`
  - `poetry shell` (opcional)

- Ejecutar tests (usar settings de test para evitar Postgres):
  - `poetry run python manage.py test --settings=transactions_service.settings_test`

- Ejecutar publish_outbox (Simulado o real si RabbitMQ y pika instalados):
  - `poetry run python manage.py publish_outbox`

- Correr server (dev):
  - `poetry run python manage.py runserver 0.0.0.0:8003`

- Probar endpoints via curl (ejemplos):
  - Transfer:
    ```bash
    curl -X POST http://localhost:8003/api/transactions/transfer \
      -H "Content-Type: application/json" \
      -d '{"idempotency_key":"abc-123","payer_user_id":"user_a","payee_user_id":"user_b","amount":"10.00","currency":"ars"}'
    ```

--------

## Notas de seguridad y producción
- Asegurar idempotencia para evitar duplicado de transacciones (usamos `idempotency_key`).
- Evitar llamadas sincrónicas críticas entre servicios en producción (ver Saga para resiliencia).
- Asegurar autenticación/autorización en Gateway y microservicios (JWT), y validación de límites y balances.

--------

## Archivos clave y ubicación
- `transactions/api.py` - Endpoints Ninja
- `transactions/schemas.py` - Pydantic schemas
- `transactions/models.py` - Transaction, Outbox models
- `transactions/tests.py` - Tests unitarios agregados
- `transactions/management/commands/publish_outbox.py` - Publisher
- `transactions_service/settings_test.py` - Config tests con sqlite
- `wallet-service` - Implementar debit/credit en `wallets/apis/views.py`

--------

Si querés, mañana arranco con el punto 1 (endpoints `debit` y `credit` en `wallet-service`) y subo tests, luego integramos en `transactions-service`.

Si preferís otro orden, decime y lo adapto.
