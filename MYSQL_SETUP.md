# Instrucciones para configurar MySQL

## 1. Instalar MySQL Server
Descarga e instala MySQL Server desde: https://dev.mysql.com/downloads/mysql/

## 2. Crear la base de datos
```sql
mysql -u root -p
CREATE DATABASE alarma_rastreadora;
GRANT ALL PRIVILEGES ON alarma_rastreadora.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

## 3. Configurar variables de entorno
En el archivo `.env`, cambiar:
```
USE_MYSQL=true
MYSQL_PASSWORD=tu_password_mysql
```

## 4. Instalar dependencias adicionales (si es necesario)
```bash
pip install --user mysqlclient
```

## 5. Reiniciar la API
La API automáticamente creará las tablas cuando se conecte a MySQL.

## Verificar conexión
Puedes verificar que las tablas se crearon ejecutando:
```sql
USE alarma_rastreadora;
SHOW TABLES;
```

Deberías ver las siguientes tablas:
- users
- devices  
- locations
- alerts
