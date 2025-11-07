# Documentación de APIs - Microservicios

Este documento lista los endpoints principales y responsabilidades de cada microservicio del sistema.

---

## 1. API Gateway
- **URL:** http://localhost:8000
- **Responsabilidad:** Entrada centralizada para servicios internos (auth, wallet, transactions).
- **Endpoints expuestos:**
  - `/auth/*` → Proxy a Auth Service
  - `/wallet/*` → Proxy a Wallet Service
  - `/transactions/*` → Proxy a Transactions Service

## 2. Auth Service
- **URL interna:** http://auth-service:8001
- **Responsabilidad:** Registro, login, autenticación de usuarios.
- **Endpoints típicos:**
  - `/register` (POST)
  - `/login` (POST)
  - `/me` (GET)

## 3. Wallet Service
- **URL interna:** http://wallet-service:8002
- **Responsabilidad:** Gestión de cuentas y saldos de usuario.
- **Endpoints típicos:**
  - `/wallets/` (GET, POST)
  - `/wallets/{id}/` (GET, PATCH)
  - `/wallets/{id}/balance/` (GET)

## 4. Transactions Service
- **URL interna:** http://transactions-service:8003
- **Responsabilidad:** Registro y consulta de transferencias entre cuentas.
- **Endpoints típicos:**
  - `/transactions/` (GET, POST)
  - `/transactions/{id}/` (GET)

## 5. Payment Service (externo)
- **URL pública:** http://localhost:8004
- **Responsabilidad:** Recepción de depósitos externos (carga de dinero, pagos de terceros).
- **Endpoints típicos:**
  - `/payments/deposit/` (POST)
  - `/payments/status/{id}/` (GET)

---

> Actualiza este documento cuando agregues, modifiques o elimines endpoints.
