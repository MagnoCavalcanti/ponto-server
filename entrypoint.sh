#!/bin/bash

# Espera o banco de dados estar pronto
echo "Aguardando o banco de dados..."
sleep 5

# Executa as migrações
echo "Aplicando migrações..."
alembic upgrade head

# Inicia a aplicação
echo "Iniciando o servidor..."
uvicorn backend.main:app --host=0.0.0.0 --port=8000
