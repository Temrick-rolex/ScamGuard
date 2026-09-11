-- ScamGuard - creation de la base PostgreSQL 18
-- A executer une seule fois, connecte en superutilisateur postgres :
--   psql -U postgres -f database/01_creation_base.sql

CREATE ROLE scamguard_app WITH LOGIN PASSWORD 'changez_ce_mot_de_passe';

CREATE DATABASE scamguard
    WITH OWNER = scamguard_app
    ENCODING = 'UTF8'
    LC_COLLATE = 'fr_FR.UTF-8'
    LC_CTYPE = 'fr_FR.UTF-8'
    TEMPLATE = template0;

COMMENT ON DATABASE scamguard IS
    'ScamGuard - detection des fraudes numeriques au Cameroun';

\connect scamguard

CREATE SCHEMA IF NOT EXISTS dw AUTHORIZATION scamguard_app;

COMMENT ON SCHEMA dw IS
    'Entrepot de donnees en etoile alimente par l ETL';

CREATE EXTENSION IF NOT EXISTS pg_trgm;

GRANT ALL PRIVILEGES ON DATABASE scamguard TO scamguard_app;
GRANT ALL ON SCHEMA public TO scamguard_app;
GRANT ALL ON SCHEMA dw TO scamguard_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT ALL ON TABLES TO scamguard_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA dw
    GRANT ALL ON TABLES TO scamguard_app;
