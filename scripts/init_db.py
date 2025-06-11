#!/usr/bin/env python3
"""
Script para inicializar o banco de dados.
Este script deve ser executado após o PostgreSQL estar rodando.
"""

import time
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from shared.constants.texts import Texts
from shared.utils.logger import Logger
import os

logger = Logger(__name__)

def wait_for_postgres():
    """Aguarda o PostgreSQL estar pronto."""
    max_retries = 30
    retry_interval = 2
    db_host = os.getenv('DB_HOST', 'postgres')
    db_user = os.getenv('DB_USER', 'evcharging')
    db_password = os.getenv('DB_PASSWORD', 'evcharging')
    db_name = os.getenv('DB_NAME', 'evcharging')
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name
            )
            conn.close()
            return True
        except psycopg2.OperationalError:
            if i == max_retries - 1:
                raise Exception("Timeout aguardando PostgreSQL")
            logger.info(f"Aguardando PostgreSQL... ({i+1}/{max_retries})")
            time.sleep(retry_interval)

def init_database():
    """Inicializa o banco de dados."""
    try:
        # Aguarda PostgreSQL estar pronto
        wait_for_postgres()

        # Conecta ao PostgreSQL
        db_host = os.getenv('DB_HOST', 'postgres')
        db_user = os.getenv('DB_USER', 'evcharging')
        db_password = os.getenv('DB_PASSWORD', 'evcharging')
        db_name = os.getenv('DB_NAME', 'evcharging')
        conn = psycopg2.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Cria banco de dados se não existir
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {db_name}")
            logger.info(f"Banco de dados '{db_name}' criado")

        # Cria usuário se não existir
        cur.execute(f"SELECT 1 FROM pg_roles WHERE rolname = '{db_user}'")
        if not cur.fetchone():
            cur.execute(f"CREATE USER {db_user} WITH PASSWORD '{db_password}'")
            logger.info(f"Usuário '{db_user}' criado")

        # Concede privilégios
        cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user}")
        logger.info(f"Privilégios concedidos ao usuário '{db_user}'")

        cur.close()
        conn.close()

        logger.info("Banco de dados inicializado com sucesso!")

    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")
        raise

if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        logger.error(f"Falha ao inicializar banco de dados: {e}")
        exit(1) 