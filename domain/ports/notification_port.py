from abc import ABC, abstractmethod

class NotificationPort(ABC):
    """Porta de abstração para notificações."""
    @abstractmethod
    def notify(self, message):
        pass 