import os
from typing import Dict, Any
from decimal import Decimal
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class Config:
    """
    Configurações do sistema.
    Todas as configurações sensíveis devem ser definidas via variáveis de ambiente.
    """
    
    # Diretórios
    BASE_DIR = Path(__file__).parent.parent.parent
    CONTRACTS_DIR = BASE_DIR / "contracts"
    CONTRACTS_BUILD_DIR = CONTRACTS_DIR / "build"
    
    # Blockchain (Ganache)
    WEB3_PROVIDER = "ganache"  # Usando Ganache para desenvolvimento
    WEB3_PROVIDER_URL = os.getenv("WEB3_PROVIDER_URL", "http://ganache:8545")
    WEB3_CONTRACT_ADDRESS = os.getenv("WEB3_CONTRACT_ADDRESS")
    WEB3_GAS_LIMIT = 3000000  # Limite de gas para transações
    WEB3_TIMEOUT = 120  # Timeout em segundos para transações
    
    # API
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "5000"))
    API_DEBUG = os.getenv("API_DEBUG", "False").lower() == "true"
    API_SECRET_KEY = os.getenv("API_SECRET_KEY", "dev-secret-key")
    API_JWT_SECRET = os.getenv("API_JWT_SECRET", "dev-jwt-secret")
    API_JWT_ALGORITHM = "HS256"
    API_JWT_EXPIRATION = 3600  # 1 hora
    API_PREFIX = "/api/v1"
    
    # Rate Limiting
    RATE_LIMIT_DEFAULT = "200 per day"
    RATE_LIMIT_STORAGE_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # Cache (Redis)
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
    REDIS_TTL = 3600  # 1 hora
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Database (PostgreSQL - usado apenas como cache/índice)
    DB_HOST = os.getenv("DB_HOST", "postgres")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_NAME = os.getenv("DB_NAME", "evcharging")
    DB_USER = os.getenv("DB_USER", "evcharging")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "evcharging")
    DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Email (opcional)
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SMTP_FROM = os.getenv("SMTP_FROM", "noreply@evcharging.com")
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Swagger
    SWAGGER_TITLE = "EV Charging API"
    SWAGGER_DESCRIPTION = "API para gerenciamento de estações de carregamento de veículos elétricos"
    SWAGGER_VERSION = "1.0.0"
    SWAGGER_UI_URL = "/docs"
    
    VERSION = "1.0.0"
    
    @classmethod
    def get_blockchain_settings(cls) -> dict:
        """
        Retorna as configurações da blockchain.
        """
        return {
            "provider": cls.WEB3_PROVIDER,
            "provider_url": cls.WEB3_PROVIDER_URL,
            "contract_address": cls.WEB3_CONTRACT_ADDRESS,
            "gas_limit": cls.WEB3_GAS_LIMIT,
            "timeout": cls.WEB3_TIMEOUT
        }
    
    @classmethod
    def get_database_settings(cls) -> dict:
        """
        Retorna as configurações do banco de dados.
        """
        return {
            "url": cls.DB_URL,
            "echo": cls.API_DEBUG
        }
    
    @classmethod
    def get_cache_settings(cls) -> dict:
        """
        Retorna as configurações do cache.
        """
        return {
            "url": cls.REDIS_URL,
            "ttl": cls.REDIS_TTL
        }
    
    @classmethod
    def get_email_settings(cls) -> dict:
        """
        Retorna as configurações de email.
        """
        return {
            "host": cls.SMTP_HOST,
            "port": cls.SMTP_PORT,
            "user": cls.SMTP_USER,
            "password": cls.SMTP_PASSWORD,
            "from": cls.SMTP_FROM
        } if cls.SMTP_HOST else None

    # Configurações da aplicação
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = APP_ENV == "development"
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key-here")

    # Configurações do servidor
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    # Configurações de carregamento
    CHARGING_BASE_RATE = Decimal(os.getenv("CHARGING_BASE_RATE", "0.001"))  # ETH por hora
    CHARGING_MIN_DURATION = int(os.getenv("CHARGING_MIN_DURATION", "900"))  # 15 minutos
    CHARGING_MAX_DURATION = int(os.getenv("CHARGING_MAX_DURATION", "86400"))  # 24 horas
    CHARGING_RESERVATION_WINDOW = int(os.getenv("CHARGING_RESERVATION_WINDOW", "604800"))  # 7 dias
    CHARGING_SESSION_TIMEOUT = int(os.getenv("CHARGING_SESSION_TIMEOUT", "300"))  # 5 minutos

    # Configurações de log
    LOG_DATE_FORMAT = os.getenv("LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")

    # Configurações do banco de dados
    DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "5"))
    DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
    DATABASE_POOL_TIMEOUT = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
    DATABASE_POOL_RECYCLE = int(os.getenv("DATABASE_POOL_RECYCLE", "1800"))

    # Configurações de cache
    CACHE_HOST = os.getenv("REDIS_HOST", "localhost")
    CACHE_PORT = int(os.getenv("REDIS_PORT", "6379"))
    CACHE_DB = int(os.getenv("REDIS_DB", "0"))
    CACHE_PASSWORD = os.getenv("REDIS_PASSWORD", None)
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "300"))

    # Configurações de limitação de taxa
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "200/hour")
    RATE_LIMIT_STORAGE_URL = os.getenv("RATE_LIMIT_STORAGE_URL", "memory://")

    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """
        Retorna a configuração do banco de dados.
        """
        return {
            "url": cls.DATABASE_URL,
            "pool_size": cls.DATABASE_POOL_SIZE,
            "max_overflow": cls.DATABASE_MAX_OVERFLOW,
            "pool_timeout": cls.DATABASE_POOL_TIMEOUT,
            "pool_recycle": cls.DATABASE_POOL_RECYCLE
        }

    @classmethod
    def get_cache_config(cls) -> Dict[str, Any]:
        """
        Retorna a configuração do cache.
        """
        return {
            "host": cls.CACHE_HOST,
            "port": cls.CACHE_PORT,
            "db": cls.CACHE_DB,
            "password": cls.CACHE_PASSWORD,
            "default_timeout": cls.CACHE_DEFAULT_TIMEOUT
        }

    @classmethod
    def get_rate_limit_config(cls) -> Dict[str, Any]:
        """
        Retorna a configuração de limitação de taxa.
        """
        return {
            "enabled": cls.RATE_LIMIT_ENABLED,
            "default": cls.RATE_LIMIT_DEFAULT,
            "storage_url": cls.RATE_LIMIT_STORAGE_URL
        } 