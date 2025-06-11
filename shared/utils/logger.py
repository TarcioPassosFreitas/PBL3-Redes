import logging
import sys
from datetime import datetime
from typing import Optional

from shared.constants.colors import Colors
from shared.constants.texts import Texts


class CustomFormatter(logging.Formatter):
    """
    Formatador personalizado para logs com cores e timestamps.
    """

    def __init__(self):
        super().__init__()
        self.colors = {
            logging.DEBUG: Colors.LOG_DEBUG,
            logging.INFO: Colors.LOG_INFO,
            logging.WARNING: Colors.LOG_WARNING,
            logging.ERROR: Colors.LOG_ERROR,
            logging.CRITICAL: Colors.LOG_CRITICAL
        }

    def format(self, record):
        """
        Formata o registro de log com cores e timestamp.
        """
        # Adiciona cor ao nível do log
        levelname = record.levelname
        if levelname in self.colors:
            record.levelname = f"{self.colors[levelname]}{levelname}{Colors.RESET}"

        # Adiciona timestamp
        record.asctime = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")

        return super().format(record)


class Logger:
    """
    Utilitário de logging centralizado para a aplicação.
    Implementa o padrão Singleton para garantir uma única instância do logger.
    """

    _instance = None

    def __new__(cls, name: str):
        """
        Implementa o padrão Singleton.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(name)
        return cls._instance

    def _initialize(self, name: str):
        """
        Inicializa o logger com handlers para console e arquivo.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(CustomFormatter())
        self.logger.addHandler(console_handler)

        # Handler para arquivo
        log_file = f"logs/ev_charging_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(CustomFormatter())
        self.logger.addHandler(file_handler)

    def log_request(self, method: str, endpoint: str, status: int, duration: float):
        """
        Registra uma requisição HTTP.
        """
        self.logger.info(
            Texts.format(Texts.LOG_REQUEST, method, endpoint, status, duration)
        )

    def log_blockchain_transaction(self, tx_hash: str, status: str, details: Optional[dict] = None):
        """
        Registra uma transação na blockchain.
        """
        message = Texts.format(Texts.LOG_BLOCKCHAIN_TX, tx_hash, status)
        if details:
            message += f" - Detalhes: {details}"
        self.logger.info(message)

    def log_error(self, error: Exception, context: Optional[dict] = None):
        """
        Registra um erro com contexto opcional.
        """
        if context:
            self.logger.error(Texts.format(Texts.LOG_ERROR_CONTEXT, str(error), context))
        else:
            self.logger.error(Texts.format(Texts.LOG_ERROR, str(error)))

    def log_session_event(self, session_id: int, event: str, details: Optional[dict] = None):
        """
        Registra um evento de sessão de carregamento.
        """
        message = Texts.format(Texts.LOG_SESSION_EVENT, session_id, event)
        if details:
            message += f" - Detalhes: {details}"
        self.logger.info(message)

    def log_station_event(self, station_id: int, event: str, details: Optional[dict] = None):
        """
        Registra um evento de estação de carregamento.
        """
        message = Texts.format(Texts.LOG_STATION_EVENT, station_id, event)
        if details:
            message += f" - Detalhes: {details}"
        self.logger.info(message)

    def log_payment_event(self, session_id: int, amount: float, status: str, details: Optional[dict] = None):
        """
        Registra um evento de pagamento.
        """
        message = Texts.format(Texts.LOG_PAYMENT_EVENT, session_id, amount, status)
        if details:
            message += f" - Detalhes: {details}"
        self.logger.info(message)

    def info(self, msg):
        self.logger.info(msg)

    def error(self, msg):
        self.logger.error(msg) 