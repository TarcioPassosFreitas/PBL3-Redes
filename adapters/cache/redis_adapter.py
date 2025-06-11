from typing import Any, Dict, List, Optional, Union
import json
import redis
from domain.ports.cache_port import CachePort
from domain.exceptions.custom_exceptions import CacheError
from shared.utils.logger import Logger
from shared.constants.config import Config
from shared.constants.texts import Texts

class RedisAdapter(CachePort):
    """
    Adaptador Redis que implementa a interface CachePort.
    Responsável por interagir com o cache usando Redis.
    """
    
    def __init__(self):
        """
        Inicializa o adaptador Redis com a conexão ao servidor.
        """
        self.logger = Logger(__name__)
        
        try:
            # Conecta ao Redis
            self.client = redis.Redis(
                host=Config.CACHE_HOST,
                port=Config.CACHE_PORT,
                db=Config.CACHE_DB,
                password=Config.CACHE_PASSWORD,
                decode_responses=True
            )
            
            # Testa conexão
            self.client.ping()
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_REDIS_CONNECT, str(e)))
            raise CacheError(Texts.ERROR_ADAPTER_CONNECTION.format("Redis"))
            
    def get(self, key: str) -> Optional[Any]:
        """
        Obtém um valor do cache.
        
        Args:
            key: Chave do valor
            
        Returns:
            Optional[Any]: Valor armazenado ou None se não encontrado
            
        Raises:
            CacheError: Se houver erro ao obter valor
        """
        try:
            value = self.client.get(key)
            if value is None:
                self.logger.error(Texts.format(Texts.ERROR_REDIS_KEY, key))
                raise CacheError(Texts.format(Texts.ERROR_REDIS_KEY, key))
            self.logger.info(Texts.format(Texts.LOG_REDIS_OPERATION, "get", key))
            return json.loads(value)
        except json.JSONDecodeError as e:
            self.logger.error(Texts.format(Texts.ERROR_CACHE_DECODE, str(e)))
            raise CacheError(Texts.ERROR_CACHE_DECODE_FAILED)
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_REDIS_OPERATION, "get", str(e)))
            raise CacheError(Texts.format(Texts.ERROR_REDIS_OPERATION, "get", str(e)))
            
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        Armazena um valor no cache.
        
        Args:
            key: Chave do valor
            value: Valor a ser armazenado
            ttl: Tempo de vida em segundos (opcional)
            
        Raises:
            CacheError: Se houver erro ao armazenar valor
        """
        try:
            if not isinstance(value, str):
                self.logger.error(Texts.format(Texts.ERROR_REDIS_VALUE, str(value)))
                raise CacheError(Texts.format(Texts.ERROR_REDIS_VALUE, str(value)))
            
            result = self.client.set(key, json.dumps(value), ex=ttl)
            if ttl:
                self.client.expire(key, ttl)
            self.logger.info(Texts.format(Texts.LOG_REDIS_OPERATION, "set", key))
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_REDIS_OPERATION, "set", str(e)))
            raise CacheError(Texts.format(Texts.ERROR_REDIS_OPERATION, "set", str(e)))
            
    def delete(self, key: str) -> None:
        """
        Remove um valor do cache.
        
        Args:
            key: Chave do valor
            
        Raises:
            CacheError: Se houver erro ao remover valor
        """
        try:
            result = self.client.delete(key)
            self.logger.info(Texts.format(Texts.LOG_REDIS_OPERATION, "delete", key))
            if result == 0:
                self.logger.error(Texts.format(Texts.ERROR_REDIS_DELETE, key))
                raise CacheError(Texts.format(Texts.ERROR_REDIS_DELETE, key))
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_REDIS_DELETE, str(e)))
            raise CacheError(Texts.format(Texts.ERROR_REDIS_DELETE, str(e)))
            
    def exists(self, key: str) -> bool:
        """
        Verifica se uma chave existe no cache.
        
        Args:
            key: Chave a ser verificada
            
        Returns:
            bool: True se a chave existir
            
        Raises:
            CacheError: Se houver erro ao verificar chave
        """
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_CACHE_OPERATION, str(e)))
            raise CacheError(Texts.ERROR_ADAPTER_OPERATION.format("Redis"))
            
    def ttl(self, key: str) -> Optional[int]:
        """
        Obtém o tempo de vida restante de uma chave.
        
        Args:
            key: Chave a ser verificada
            
        Returns:
            Optional[int]: Tempo de vida em segundos ou None se não tiver TTL
            
        Raises:
            CacheError: Se houver erro ao obter TTL
        """
        try:
            ttl = self.client.ttl(key)
            return ttl if ttl > 0 else None
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_REDIS_TTL, str(e)))
            raise CacheError(Texts.ERROR_REDIS_TTL_FAILED)
            
    def increment(self, key: str, amount: int = 1) -> int:
        """
        Incrementa o valor de uma chave.
        
        Args:
            key: Chave a ser incrementada
            amount: Quantidade a incrementar
            
        Returns:
            int: Novo valor
            
        Raises:
            CacheError: Se houver erro ao incrementar valor
        """
        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_REDIS_INCREMENT, str(e)))
            raise CacheError(Texts.ERROR_REDIS_INCREMENT_FAILED)
            
    def decrement(self, key: str, amount: int = 1) -> int:
        """
        Decrementa o valor de uma chave.
        
        Args:
            key: Chave a ser decrementada
            amount: Quantidade a decrementar
            
        Returns:
            int: Novo valor
            
        Raises:
            CacheError: Se houver erro ao decrementar valor
        """
        try:
            return self.client.decrby(key, amount)
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_REDIS_DECREMENT, str(e)))
            raise CacheError(Texts.ERROR_REDIS_DECREMENT_FAILED)
            
    def clear(self) -> None:
        """
        Limpa todo o cache.
        
        Raises:
            CacheError: Se houver erro ao limpar cache
        """
        try:
            self.client.flushdb()
            self.logger.info(Texts.format(Texts.LOG_REDIS_OPERATION, "clear", "all"))
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_REDIS_CLEAR, str(e)))
            raise CacheError(Texts.format(Texts.ERROR_REDIS_CLEAR, str(e)))
            
    def close(self) -> None:
        """
        Fecha a conexão com o Redis.
        
        Raises:
            CacheError: Se houver erro ao fechar conexão
        """
        try:
            self.client.close()
            self.logger.info(Texts.LOG_REDIS_DISCONNECTED)
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_REDIS_DISCONNECT, str(e)))
            raise CacheError(Texts.format(Texts.ERROR_REDIS_DISCONNECT, str(e))) 