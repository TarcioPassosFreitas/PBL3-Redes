from abc import ABC, abstractmethod

class DatabasePort(ABC):
    """Porta de abstração para operações de banco de dados."""
    @abstractmethod
    def connect(self):
        pass 