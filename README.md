# 🧩 Wallet System — Arquitectura de Microservicios

Proyecto profesional de alto impacto que implementa un sistema de **Billetera Virtual** modular, diseñado con una arquitectura **orientada a eventos** y principios de **resiliencia y alta disponibilidad**.

---

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Django](https://img.shields.io/badge/django-%23092e20.svg?style=for-the-badge&logo=django&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white)
![Celery](https://img.shields.io/badge/celery-%2337814a.svg?style=for-the-badge&logo=celery&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)

---

## 🏗️ Arquitectura del Sistema

El sistema utiliza un **API Gateway** como punto de entrada único, delegando responsabilidades a microservicios especializados que se comunican de forma tanto sincrónica (HTTP/REST) como asincrónica (RabbitMQ).

```mermaid
graph TD
    User([Usuario]) --> Gateway[API Gateway - FastAPI]
    
    subgraph Microservicios
        Gateway --> Auth[Auth Service - FastAPI + MongoDB]
        Gateway --> Wallet[Wallet Service - Django + SQLite/PG]
        Gateway --> Trans[Transactions Service - Django + PG]
        Gateway --> Payment[Payment Service - FastAPI + Celery]
    end

    subgraph Mensajería
        Auth -- Event: User Registered --> Broker[(RabbitMQ)]
        Broker --> Wallet -- Create Wallet --> Wallet
        Trans -- Transaction Events --> Broker
    end
```

### 🧠 Patrones de Diseño Implementados
- **API Gateway**: Centralización de autenticación JWT y ruteo.
- **Transactional Outbox**: Asegura que los eventos no se pierdan si el broker falla durante una transacción.
- **Saga Pattern (Coreografía)**: Gestión de consistencia eventual entre los servicios de transacciones y billeteras para completar transferencias.
- **Event-Driven**: Comunicación desacoplada mediante RabbitMQ/Celery.

---

## 🚀 Características Principales
- ✅ **Autenticación Robusta**: JWT con expiración y seguridad bcrypt.
- ✅ **Gestión de Billeteras**: Creación automática al registrarse mediante eventos.
- ✅ **Transferencias Seguras**: Lógica de idempontencia para evitar cobros duplicados y validación de saldo atómica.
- ✅ **Resiliencia**: Manejo de eventos pendientes y reintentos automáticos.

---

## 💻 Cómo ejecutar localmente

### Requisitos
- Docker y Docker Compose
- Poetry (opcional para desarrollo local)

### Pasos
1. Clonar el repositorio.
2. Configurar las variables de entorno (puedes usar `.env.example` en cada servicio).
3. Levantar la infraestructura:
   ```bash
   docker-compose up --build
   ```
4. El sistema estará disponible en `http://localhost:8000`.

---

## 📄 Documentación detallada
- [Arquitectura de Eventos](file:///home/matiasdev/wallet-system/ariquitectura_por_eventos.md)
- [API Gateway](file:///home/matiasdev/wallet-system/api-gateway/README.md)
- [Auth Service](file:///home/matiasdev/wallet-system/auth-service/auth-service.md)
