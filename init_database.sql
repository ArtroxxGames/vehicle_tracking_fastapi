-- Script para crear la base de datos de la alarma rastreadora
-- Ejecutar en MySQL antes de iniciar la aplicación

CREATE DATABASE IF NOT EXISTS alarma_rastreadora;
USE alarma_rastreadora;

-- Las tablas se crearán automáticamente con SQLAlchemy
-- Este script es solo para crear la base de datos principal

-- Verificar que la base de datos fue creada
SHOW TABLES;
