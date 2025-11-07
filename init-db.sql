-- Crear base de datos y usuario para WALLET y TRANSACTIONS por separado



-- Usuario y DB para WALLET
CREATE ROLE wallet_user WITH LOGIN PASSWORD 'wallet_pass_123';
CREATE DATABASE wallet_db OWNER wallet_user;

-- Usuario y DB para TRANSACTIONS
CREATE ROLE trans_user WITH LOGIN PASSWORD 'trans_pass_123';
CREATE DATABASE transactions_db OWNER trans_user;

-- Permisos básicos en cada DB
\c wallet_db
GRANT ALL ON SCHEMA public TO wallet_user;
CREATE ROLE wallet_user WITH LOGIN PASSWORD 'wallet_pass_123';
CREATE DATABASE wallet_db OWNER wallet_user;

-- Usuario y DB para TRANSACTIONS
CREATE ROLE trans_user WITH LOGIN PASSWORD 'trans_pass_123';
CREATE DATABASE transactions_db OWNER trans_user;

-- Permisos básicos en cada DB
\c wallet_db
GRANT ALL ON SCHEMA public TO wallet_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO wallet_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO wallet_user;

\c transactions_db
GRANT ALL ON SCHEMA public TO trans_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO trans_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO trans_user;
