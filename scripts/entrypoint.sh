#!/bin/bash
set -ex  # <--- adiciona log de cada comando executado

mkdir -p /app/logs
chmod 777 /app/logs

echo "Aguardando serviços..."
python scripts/init_db.py
python scripts/deploy_contract_ganache.py

echo "Executando migrações..."
alembic upgrade head

echo "Iniciando aplicação..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
