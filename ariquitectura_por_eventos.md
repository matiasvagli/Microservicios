# 🧩 Event Architecture — Wallet System

## ⚙️ Resumen General

El sistema implementa una arquitectura **asíncrona y resiliente** basada en **RabbitMQ + Celery**, diseñada para garantizar la continuidad operativa incluso si uno o más microservicios están fuera de línea.

---

## 🪢 Broker (RabbitMQ)

RabbitMQ actúa como **bus de eventos** entre los microservicios (`auth_service`, `wallet_service`, `transactions_service`, etc.).

Cada evento se encola y permanece en el broker hasta que el *consumer* correspondiente lo procese.  
De esta forma, se evita la pérdida de información ante caídas temporales.

**Colas principales:**
- `user_registered` → creación de wallets al registrarse un usuario.  
- `user_events` / `pending_events` → flujo de eventos pendientes o no confirmados.  
- `celery` y `celeryev*` → colas internas usadas por Celery para control y monitoreo.

---

## 🔄 Consumers (Workers)

Se utilizan **dos consumers** distintos, con responsabilidades separadas:

### 1. Consumer principal (en vivo)
Procesa los eventos **en tiempo real**.  
Ejemplo: al recibir `user_registered`, crea la wallet del usuario inmediatamente.

```python
@app.task(name="process_user_event")
def process_user_event(event):
    # Procesamiento normal en tiempo real
    ...
2. Consumer de respaldo (eventos caídos)

Escucha eventos fallidos o pendientes desde la base de datos.
Se ejecuta de forma periódica (via Celery Beat o cron) para reintentar procesar lo que quedó en estado PENDING.

@app.task(name="retry_failed_events")
def retry_failed_events():
    pending = PendingEvent.objects.all()
    for event in pending:
        try:
            process_user_event(event.payload)
            event.mark_as_processed()
        except Exception:
            event.increment_retry_count()
🧠 Estrategia de Resiliencia

Los eventos no críticos (notificaciones, auditorías, emails) se manejan de forma asíncrona.
Si un servicio no crítico está caído, los eventos quedan encolados y se procesan luego.

Los eventos críticos (transferencias, débitos, créditos) se manejan sincrónicamente, garantizando consistencia inmediata.

Los fallos temporales se detectan y registran en la tabla pending_events, evitando pérdida de datos.

Un job periódico se encarga de reintentar los eventos fallidos hasta que se confirmen o se marquen como irrecuperables.

💡 Beneficios

✅ Sistema tolerante a fallos (fault-tolerant).
✅ Ningún evento se pierde, aun si un servicio está offline.
✅ Escalable: se pueden agregar más workers o colas específicas por tipo de evento.
✅ Mantenible: separación clara entre lógica de negocio y manejo de eventos.
✅ Preparado para aplicar patrones de consistencia eventual o SAGA pattern a futuro.

Estado actual:

El sistema puede seguir operando incluso con servicios no críticos caídos, gracias a la persistencia de eventos y el manejo dual de consumers.            