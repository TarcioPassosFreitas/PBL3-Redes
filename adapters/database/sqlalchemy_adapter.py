from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Numeric, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.exc import SQLAlchemyError
from domain.ports.database_port import DatabasePort
from domain.exceptions.custom_exceptions import DatabaseError
from shared.utils.logger import Logger
from shared.constants.config import Config
from shared.constants.texts import Texts

# Tipo genérico para entidades
T = TypeVar("T")

# Base para modelos SQLAlchemy
Base = declarative_base()

class SQLAlchemyAdapter(DatabasePort, Generic[T]):
    """
    Adaptador SQLAlchemy que implementa a interface DatabasePort.
    Responsável por interagir com o banco de dados usando SQLAlchemy ORM.
    """
    
    def __init__(self, model_class: Type[T]):
        """
        Inicializa o adaptador com a classe do modelo.
        
        Args:
            model_class: Classe do modelo SQLAlchemy
        """
        self.logger = Logger(__name__)
        self.model_class = model_class
        
        # Cria engine e sessão
        self.engine = create_engine(Config.DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        
        # Cria tabelas
        Base.metadata.create_all(self.engine)
        
    def create(self, data: Dict[str, Any]) -> T:
        """
        Cria um novo registro no banco de dados.
        
        Args:
            data: Dados do registro
            
        Returns:
            T: Instância do modelo criada
            
        Raises:
            DatabaseError: Se houver erro ao criar registro
        """
        try:
            # Cria instância do modelo
            instance = self.model_class(**data)
            
            # Salva no banco
            session = self.Session()
            session.add(instance)
            session.commit()
            session.refresh(instance)
            session.close()
            
            return instance
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_DATABASE_CREATE, str(e)))
            raise DatabaseError(Texts.ERROR_DATABASE_CREATE_FAILED)
            
    def get_by_id(self, id: int) -> Optional[T]:
        """
        Obtém um registro pelo ID.
        
        Args:
            id: ID do registro
            
        Returns:
            Optional[T]: Instância do modelo ou None se não encontrado
            
        Raises:
            DatabaseError: Se houver erro ao consultar registro
        """
        try:
            session = self.Session()
            instance = session.query(self.model_class).get(id)
            session.close()
            return instance
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_DATABASE_GET, str(e)))
            raise DatabaseError(Texts.ERROR_DATABASE_GET_FAILED)
            
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """
        Obtém todos os registros com filtros opcionais.
        
        Args:
            filters: Filtros a serem aplicados
            
        Returns:
            List[T]: Lista de instâncias do modelo
            
        Raises:
            DatabaseError: Se houver erro ao consultar registros
        """
        try:
            session = self.Session()
            query = session.query(self.model_class)
            
            # Aplica filtros
            if filters:
                for key, value in filters.items():
                    query = query.filter(getattr(self.model_class, key) == value)
                    
            instances = query.all()
            session.close()
            return instances
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_DATABASE_LIST, str(e)))
            raise DatabaseError(Texts.ERROR_DATABASE_LIST_FAILED)
            
    def update(self, id: int, data: Dict[str, Any]) -> Optional[T]:
        """
        Atualiza um registro existente.
        
        Args:
            id: ID do registro
            data: Novos dados do registro
            
        Returns:
            Optional[T]: Instância atualizada ou None se não encontrado
            
        Raises:
            DatabaseError: Se houver erro ao atualizar registro
        """
        try:
            session = self.Session()
            instance = session.query(self.model_class).get(id)
            
            if not instance:
                session.close()
                return None
                
            # Atualiza atributos
            for key, value in data.items():
                setattr(instance, key, value)
                
            session.commit()
            session.refresh(instance)
            session.close()
            return instance
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_DATABASE_UPDATE, str(e)))
            raise DatabaseError(Texts.ERROR_DATABASE_UPDATE_FAILED)
            
    def delete(self, id: int) -> bool:
        """
        Remove um registro do banco de dados.
        
        Args:
            id: ID do registro
            
        Returns:
            bool: True se removido com sucesso
            
        Raises:
            DatabaseError: Se houver erro ao remover registro
        """
        try:
            session = self.Session()
            instance = session.query(self.model_class).get(id)
            
            if not instance:
                session.close()
                return False
                
            session.delete(instance)
            session.commit()
            session.close()
            return True
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_DATABASE_DELETE, str(e)))
            raise DatabaseError(Texts.ERROR_DATABASE_DELETE_FAILED)
            
    def begin_transaction(self) -> Session:
        """
        Inicia uma transação no banco de dados.
        
        Returns:
            Session: Sessão da transação
            
        Raises:
            DatabaseError: Se houver erro ao iniciar transação
        """
        try:
            return self.Session()
        except Exception as e:
            self.logger.error(f"Erro ao iniciar transação: {str(e)}")
            raise DatabaseError("Falha ao iniciar transação")
            
    def commit_transaction(self, session: Session) -> None:
        """
        Confirma uma transação.
        
        Args:
            session: Sessão da transação
            
        Raises:
            DatabaseError: Se houver erro ao confirmar transação
        """
        try:
            session.commit()
            session.close()
        except Exception as e:
            session.rollback()
            session.close()
            self.logger.error(Texts.format(Texts.ERROR_DATABASE_COMMIT, str(e)))
            raise DatabaseError(Texts.ERROR_DATABASE_COMMIT_FAILED)
            
    def rollback_transaction(self, session: Session) -> None:
        """
        Reverte uma transação.
        
        Args:
            session: Sessão da transação
            
        Raises:
            DatabaseError: Se houver erro ao reverter transação
        """
        try:
            session.rollback()
            session.close()
        except Exception as e:
            session.close()
            self.logger.error(Texts.format(Texts.ERROR_DATABASE_ROLLBACK, str(e)))
            raise DatabaseError(Texts.ERROR_DATABASE_ROLLBACK_FAILED) 