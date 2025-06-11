#!/bin/bash
set -e

# Espera o PostgreSQL estar pronto
echo "Aguardando PostgreSQL..."
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "PostgreSQL está pronto!"

# Executa o script de seed
echo "Iniciando seed do banco de dados..."
python scripts/seed_db.py

echo "Seed concluído com sucesso!" 