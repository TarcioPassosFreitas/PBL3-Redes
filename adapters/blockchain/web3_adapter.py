import json
import time
from typing import Dict, Any, Optional, List, Tuple
from decimal import Decimal
from datetime import datetime
from web3 import Web3
from web3.exceptions import ContractLogicError, TimeExhausted
from eth_account.messages import encode_defunct
from eth_typing import Address
from eth_utils import to_checksum_address
from web3.contract import Contract
from pathlib import Path

from domain.ports.blockchain_port import BlockchainPort
from domain.entities.session import Session
from domain.entities.station import Station
from domain.entities.user import User
from domain.exceptions.custom_exceptions import (
    BlockchainError,
    BlockchainTransactionError,
    BlockchainNetworkError,
    BlockchainInsufficientBalanceError,
    BlockchainInvalidAddressError,
    BlockchainInvalidContractError,
    BlockchainTimeoutError,
    BlockchainContractError
)
from shared.constants.config import Config
from shared.utils.logger import Logger
from shared.constants.texts import Texts

class Web3Adapter(BlockchainPort):
    """
    Adaptador Web3 que implementa a interface BlockchainPort.
    Responsável por interagir com a blockchain Ethereum usando Web3.py.
    Este adaptador é a fonte da verdade para todas as transações do sistema.
    """

    def __init__(self):
        """
        Inicializa o adaptador Web3 com a conexão à blockchain.
        """
        self.logger = Logger(__name__)
        
        try:
            # Inicializa conexão Web3
            if Config.WEB3_PROVIDER == "ganache":
                self.w3 = Web3(Web3.HTTPProvider(Config.WEB3_PROVIDER_URL))
            else:
                raise BlockchainError(Texts.ERROR_BLOCKCHAIN_PROVIDER)
            
            # Verifica conexão
            if not self.w3.is_connected():
                raise BlockchainNetworkError(Texts.ERROR_BLOCKCHAIN_NETWORK)
            
            # Carrega contrato
            self._load_contract()
            
            self.logger.info(Texts.LOG_BLOCKCHAIN_CONNECTED)
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_BLOCKCHAIN_CONTRACT, str(e)))
            raise BlockchainError(Texts.format(Texts.ERROR_BLOCKCHAIN_CONTRACT, str(e)))

    def _load_contract(self) -> None:
        """
        Carrega o contrato EVCharging da blockchain.
        """
        try:
            # Tenta carregar do build do Ganache primeiro
            build_path = Path("contracts/build/EVCharging.json")
            if not build_path.exists():
                build_path = Path("contracts/EVCharging.json")
            
            with open(build_path) as f:
                contract_data = json.load(f)
            
            self.contract_address = Config.WEB3_CONTRACT_ADDRESS or contract_data.get("address")
            if not self.contract_address:
                raise BlockchainInvalidContractError(Texts.ERROR_BLOCKCHAIN_CONTRACT_ADDRESS)
            
            self.contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(self.contract_address),
                abi=contract_data["abi"]
            )
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_BLOCKCHAIN_CONTRACT_LOAD, str(e)))
            raise BlockchainInvalidContractError(Texts.format(Texts.ERROR_BLOCKCHAIN_CONTRACT_LOAD, str(e)))

    def get_session(self, session_id: int) -> Dict[str, Any]:
        """
        Obtém os detalhes de uma sessão diretamente da blockchain.
        """
        try:
            session = self.contract.functions.getSession(session_id).call()
            return {
                "id": session[0],
                "station_id": session[1],
                "user_address": session[2],
                "start_time": datetime.fromtimestamp(session[3]),
                "end_time": datetime.fromtimestamp(session[4]) if session[4] > 0 else None,
                "status": session[5],
                "amount": Decimal(session[6]) / Decimal(10**18),  # Converter de Wei para ETH
                "paid": session[7]
            }
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_BLOCKCHAIN_SESSION_GET, str(e)))
            raise BlockchainError(Texts.format(Texts.ERROR_BLOCKCHAIN_SESSION_GET, str(e)))

    def get_station(self, station_id: int) -> Dict[str, Any]:
        """
        Obtém os detalhes de uma estação diretamente da blockchain.
        """
        try:
            station = self.contract.functions.getStation(station_id).call()
            return {
                "id": station[0],
                "location": station[1],
                "status": station[2],
                "current_session": station[3],
                "reserved_until": datetime.fromtimestamp(station[4]) if station[4] > 0 else None,
                "reserved_by": station[5] if station[5] != "0x0000000000000000000000000000000000000000" else None
            }
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_BLOCKCHAIN_STATION_GET, str(e)))
            raise BlockchainError(Texts.format(Texts.ERROR_BLOCKCHAIN_STATION_GET, str(e)))

    def get_user_sessions(self, user_address: str) -> List[Dict[str, Any]]:
        """
        Obtém todas as sessões de um usuário diretamente da blockchain.
        """
        try:
            # Obtém IDs das sessões do usuário
            session_ids = self.contract.functions.getUserSessions(
                self.w3.to_checksum_address(user_address)
            ).call()
            
            # Obtém detalhes de cada sessão
            sessions = []
            for session_id in session_ids:
                sessions.append(self.get_session(session_id))
            
            return sessions
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_BLOCKCHAIN_USER_SESSIONS, str(e)))
            raise BlockchainError(Texts.format(Texts.ERROR_BLOCKCHAIN_USER_SESSIONS, str(e)))

    def get_station_sessions(self, station_id: int) -> List[Dict[str, Any]]:
        """
        Obtém todas as sessões de uma estação diretamente da blockchain.
        """
        try:
            # Obtém IDs das sessões da estação
            session_ids = self.contract.functions.getStationSessions(station_id).call()
            
            # Obtém detalhes de cada sessão
            sessions = []
            for session_id in session_ids:
                sessions.append(self.get_session(session_id))
            
            return sessions
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_BLOCKCHAIN_STATION_SESSIONS, str(e)))
            raise BlockchainError(Texts.format(Texts.ERROR_BLOCKCHAIN_STATION_SESSIONS, str(e)))

    def start_session(self, station_id: int, user_address: str) -> Dict[str, Any]:
        """
        Inicia uma nova sessão de carregamento na blockchain.
        """
        try:
            # Prepara transação
            tx = self.contract.functions.startSession(
                station_id,
                self.w3.to_checksum_address(user_address)
            ).build_transaction({
                "from": self.w3.to_checksum_address(user_address),
                "gas": Config.WEB3_GAS_LIMIT,
                "nonce": self.w3.eth.get_transaction_count(user_address)
            })
            
            # Envia transação
            tx_hash = self.w3.eth.send_transaction(tx)
            
            # Aguarda confirmação
            receipt = self.w3.eth.wait_for_transaction_receipt(
                tx_hash,
                timeout=Config.WEB3_TIMEOUT
            )
            
            # Obtém evento de sessão iniciada
            session_started = self.contract.events.SessionStarted().process_receipt(receipt)[0]
            session_id = session_started["args"]["sessionId"]
            
            # Retorna detalhes da sessão
            return self.get_session(session_id)
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_BLOCKCHAIN_SESSION_START, str(e)))
            raise BlockchainTransactionError(Texts.format(Texts.ERROR_BLOCKCHAIN_SESSION_START, str(e)))

    def end_session(self, session_id: int, user_address: str) -> Dict[str, Any]:
        """
        Finaliza uma sessão de carregamento na blockchain.
        """
        try:
            # Prepara transação
            tx = self.contract.functions.endSession(session_id).build_transaction({
                "from": self.w3.to_checksum_address(user_address),
                "gas": Config.WEB3_GAS_LIMIT,
                "nonce": self.w3.eth.get_transaction_count(user_address)
            })
            
            # Envia transação
            tx_hash = self.w3.eth.send_transaction(tx)
            
            # Aguarda confirmação
            receipt = self.w3.eth.wait_for_transaction_receipt(
                tx_hash,
                timeout=Config.WEB3_TIMEOUT
            )
            
            # Obtém evento de sessão finalizada
            session_ended = self.contract.events.SessionEnded().process_receipt(receipt)[0]
            
            # Retorna detalhes da sessão
            return self.get_session(session_id)
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_BLOCKCHAIN_SESSION_END, str(e)))
            raise BlockchainTransactionError(Texts.format(Texts.ERROR_BLOCKCHAIN_SESSION_END, str(e)))

    def reserve_station(self, station_id: int, user_address: str, start_time: datetime) -> Dict[str, Any]:
        """
        Reserva uma estação na blockchain.
        """
        try:
            # Prepara transação
            tx = self.contract.functions.reserveStation(
                station_id,
                int(start_time.timestamp())
            ).build_transaction({
                "from": self.w3.to_checksum_address(user_address),
                "gas": Config.WEB3_GAS_LIMIT,
                "nonce": self.w3.eth.get_transaction_count(user_address)
            })
            
            # Envia transação
            tx_hash = self.w3.eth.send_transaction(tx)
            
            # Aguarda confirmação
            receipt = self.w3.eth.wait_for_transaction_receipt(
                tx_hash,
                timeout=Config.WEB3_TIMEOUT
            )
            
            # Obtém evento de reserva criada
            reservation_created = self.contract.events.ReservationCreated().process_receipt(receipt)[0]
            
            # Retorna detalhes da estação
            return self.get_station(station_id)
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_BLOCKCHAIN_RESERVATION_CREATE, str(e)))
            raise BlockchainTransactionError(Texts.format(Texts.ERROR_BLOCKCHAIN_RESERVATION_CREATE, str(e)))

    def cancel_reservation(self, station_id: int, user_address: str) -> Dict[str, Any]:
        """
        Cancela uma reserva na blockchain.
        """
        try:
            # Prepara transação
            tx = self.contract.functions.cancelReservation(station_id).build_transaction({
                "from": self.w3.to_checksum_address(user_address),
                "gas": Config.WEB3_GAS_LIMIT,
                "nonce": self.w3.eth.get_transaction_count(user_address)
            })
            
            # Envia transação
            tx_hash = self.w3.eth.send_transaction(tx)
            
            # Aguarda confirmação
            receipt = self.w3.eth.wait_for_transaction_receipt(
                tx_hash,
                timeout=Config.WEB3_TIMEOUT
            )
            
            # Obtém evento de reserva cancelada
            reservation_cancelled = self.contract.events.ReservationCancelled().process_receipt(receipt)[0]
            
            # Retorna detalhes da estação
            return self.get_station(station_id)
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_BLOCKCHAIN_RESERVATION_CANCEL, str(e)))
            raise BlockchainTransactionError(Texts.format(Texts.ERROR_BLOCKCHAIN_RESERVATION_CANCEL, str(e)))

    def process_payment(self, session_id: int, user_address: str, amount: Decimal) -> Dict[str, Any]:
        """
        Processa um pagamento na blockchain.
        """
        try:
            # Converte ETH para Wei
            amount_wei = int(amount * Decimal(10**18))
            
            # Prepara transação
            tx = self.contract.functions.paySession(session_id).build_transaction({
                "from": self.w3.to_checksum_address(user_address),
                "value": amount_wei,
                "gas": Config.WEB3_GAS_LIMIT,
                "nonce": self.w3.eth.get_transaction_count(user_address)
            })
            
            # Envia transação
            tx_hash = self.w3.eth.send_transaction(tx)
            
            # Aguarda confirmação
            receipt = self.w3.eth.wait_for_transaction_receipt(
                tx_hash,
                timeout=Config.WEB3_TIMEOUT
            )
            
            # Obtém evento de pagamento processado
            payment_processed = self.contract.events.PaymentProcessed().process_receipt(receipt)[0]
            
            # Retorna detalhes da sessão
            return self.get_session(session_id)
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_BLOCKCHAIN_PAYMENT_PROCESS, str(e)))
            raise BlockchainTransactionError(Texts.format(Texts.ERROR_BLOCKCHAIN_PAYMENT_PROCESS, str(e)))

    def validate_address(self, address: str) -> bool:
        """
        Validate an Ethereum address.
        """
        try:
            return self.w3.is_address(address) and self.w3.is_checksum_address(address)
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_BLOCKCHAIN_ADDRESS_VALIDATION, str(e)))
            return False

    def get_balance(self, address: str) -> Decimal:
        """
        Obtém o saldo de tokens de um endereço.
        
        Args:
            address: Endereço da carteira
            
        Returns:
            Decimal: Saldo em tokens
            
        Raises:
            BlockchainError: Se houver erro ao consultar o saldo
        """
        try:
            if not self.validate_address(address):
                raise BlockchainInvalidAddressError(Texts.format(Texts.ERROR_BLOCKCHAIN_INVALID_ADDRESS, address))

            balance_wei = self.w3.eth.get_balance(self.w3.to_checksum_address(address))
            balance_eth = self.w3.from_wei(balance_wei, "ether")
            return Decimal(str(balance_eth))
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_BLOCKCHAIN_BALANCE, str(e)))
            raise BlockchainError(Texts.format(Texts.ERROR_BLOCKCHAIN_BALANCE_FAILED, str(e)))

    def verify_signature(self, message: str, signature: str, address: str) -> bool:
        """
        Verifica uma assinatura Ethereum.
        
        Args:
            message: Mensagem original
            signature: Assinatura a ser verificada
            address: Endereço da carteira que assinou
            
        Returns:
            bool: True se a assinatura for válida
            
        Raises:
            BlockchainError: Se houver erro na verificação
        """
        try:
            if not self.validate_address(address):
                raise BlockchainInvalidAddressError(Texts.format(Texts.ERROR_BLOCKCHAIN_INVALID_ADDRESS, address))

            message_hash = encode_defunct(text=message)
            recovered_address = self.w3.eth.account.recover_message(message_hash, signature=signature)
            return recovered_address.lower() == address.lower()
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_BLOCKCHAIN_SIGNATURE, str(e)))
            raise BlockchainError(Texts.ERROR_BLOCKCHAIN_SIGNATURE_FAILED)

    def get_session_details(self, session_id: int) -> Dict[str, Any]:
        """
        Get details of a charging session from the blockchain.
        """
        try:
            session_data = self.contract.functions.getSession(session_id).call()
            return {
                "session_id": session_id,
                "station_id": session_data[0],
                "user_address": to_checksum_address(session_data[1]),
                "start_time": datetime.fromtimestamp(session_data[2]),
                "end_time": datetime.fromtimestamp(session_data[3]) if session_data[3] > 0 else None,
                "energy_consumed": Decimal(str(self.w3.from_wei(session_data[4], "ether"))),
                "amount_paid": Decimal(str(self.w3.from_wei(session_data[5], "ether"))),
                "status": session_data[6]
            }
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_BLOCKCHAIN_SESSION_DETAILS, str(e)))
            raise BlockchainError(Texts.format(Texts.ERROR_BLOCKCHAIN_SESSION_DETAILS, str(e)))

    def get_station_details(self, station_id: int) -> Dict[str, Any]:
        """
        Get details of a charging station from the blockchain.
        """
        try:
            station_data = self.contract.functions.getStation(station_id).call()
            return {
                "station_id": station_id,
                "location": station_data[0],
                "status": station_data[1],
                "current_session_id": station_data[2],
                "total_sessions": station_data[3],
                "total_energy": Decimal(str(self.w3.from_wei(station_data[4], "ether"))),
                "total_revenue": Decimal(str(self.w3.from_wei(station_data[5], "ether")))
            }
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_BLOCKCHAIN_STATION_DETAILS, str(e)))
            raise BlockchainError(Texts.format(Texts.ERROR_BLOCKCHAIN_STATION_DETAILS_FAILED, str(e)))

    def get_user_details(self, user_address: str) -> Dict[str, Any]:
        """
        Get details of a user from the blockchain.
        """
        try:
            if not self.validate_address(user_address):
                raise BlockchainInvalidAddressError(Texts.format(Texts.ERROR_BLOCKCHAIN_INVALID_ADDRESS, user_address))

            user_data = self.contract.functions.getUser(user_address).call()
            return {
                "user_address": to_checksum_address(user_address),
                "total_sessions": user_data[0],
                "total_energy": Decimal(str(self.w3.from_wei(user_data[1], "ether"))),
                "total_spent": Decimal(str(self.w3.from_wei(user_data[2], "ether"))),
                "last_session_id": user_data[3]
            }
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_BLOCKCHAIN_USER_DETAILS, str(e)))
            raise BlockchainError(Texts.format(Texts.ERROR_BLOCKCHAIN_USER_DETAILS_FAILED, str(e)))

    def connect(self):
        """Conecta à rede blockchain."""
        try:
            self.w3 = Web3(Web3.HTTPProvider(Config.WEB3_PROVIDER_URL))
            if not self.w3.is_connected():
                raise BlockchainNetworkError(Texts.ERROR_WEB3_CONNECT_FAILED)
            self.logger.info(Texts.LOG_WEB3_CONNECTED)
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_WEB3_CONNECT, str(e)))
            raise BlockchainNetworkError(Texts.ERROR_WEB3_CONNECT_FAILED)

    def disconnect(self):
        """Desconecta da rede blockchain."""
        try:
            if self.w3:
                self.w3 = None
                self.logger.info(Texts.LOG_WEB3_DISCONNECTED)
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_WEB3_DISCONNECT, str(e)))
            raise BlockchainNetworkError(Texts.ERROR_WEB3_DISCONNECT_FAILED)

    def _validate_address(self, address: str) -> str:
        """Valida um endereço Ethereum."""
        try:
            if not Web3.is_address(address):
                raise BlockchainInvalidAddressError(Texts.format(Texts.ERROR_WEB3_ADDRESS, address))
            return Web3.to_checksum_address(address)
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_WEB3_ADDRESS, str(e)))
            raise BlockchainInvalidAddressError(Texts.ERROR_WEB3_ADDRESS_FAILED)

    def _get_nonce(self, address: str) -> int:
        """Obtém o nonce da conta."""
        try:
            return self.w3.eth.get_transaction_count(address)
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_WEB3_NONCE, str(e)))
            raise BlockchainError(Texts.ERROR_WEB3_NONCE_FAILED)

    def _estimate_gas(self, transaction: dict) -> int:
        """Estima o gas necessário para a transação."""
        try:
            return self.w3.eth.estimate_gas(transaction)
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_WEB3_GAS, str(e)))
            raise BlockchainError(Texts.ERROR_WEB3_GAS_FAILED)

    def _sign_transaction(self, transaction: dict, private_key: str) -> bytes:
        """Assina uma transação."""
        try:
            return self.w3.eth.account.sign_transaction(transaction, private_key).rawTransaction
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_WEB3_SIGN, str(e)))
            raise BlockchainError(Texts.ERROR_WEB3_SIGN_FAILED)

    def _send_transaction(self, signed_txn: bytes) -> str:
        """Envia uma transação assinada."""
        try:
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn)
            self.logger.info(Texts.format(Texts.LOG_WEB3_TRANSACTION, tx_hash.hex()))
            return tx_hash.hex()
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_WEB3_SEND, str(e)))
            raise BlockchainTransactionError(Texts.ERROR_WEB3_SEND_FAILED)

    def _wait_for_transaction(self, tx_hash: str) -> dict:
        """Aguarda a confirmação de uma transação."""
        try:
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            self.logger.info(Texts.format(Texts.LOG_WEB3_CONFIRMATION, tx_hash))
            return receipt
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_WEB3_RECEIPT, str(e)))
            raise BlockchainTransactionError(Texts.ERROR_WEB3_RECEIPT_FAILED)

    # Métodos obrigatórios da interface BlockchainPort (não implementados)
    async def get_user(self, address: str):
        raise NotImplementedError("get_user não implementado")

    async def get_station(self, station_id: int):
        raise NotImplementedError("get_station não implementado")

    async def get_session(self, session_id: int):
        raise NotImplementedError("get_session não implementado")

    async def get_reservation(self, reservation_id: int):
        raise NotImplementedError("get_reservation não implementado")

    async def get_user_sessions(self, user_address: str, status=None):
        raise NotImplementedError("get_user_sessions não implementado")

    async def get_user_reservations(self, user_address: str, status=None):
        raise NotImplementedError("get_user_reservations não implementado")

    async def get_station_sessions(self, station_id: int, status=None):
        raise NotImplementedError("get_station_sessions não implementado")

    async def get_station_reservations(self, station_id: int, status=None):
        raise NotImplementedError("get_station_reservations não implementado")

    async def start_session(self, user_address: str, station_id: int):
        raise NotImplementedError("start_session não implementado")

    async def end_session(self, session_id: int):
        raise NotImplementedError("end_session não implementado")

    async def pay_session(self, session_id: int, amount):
        raise NotImplementedError("pay_session não implementado")

    async def reserve_station(self, user_address: str, station_id: int, start_time, duration_hours):
        raise NotImplementedError("reserve_station não implementado")

    async def cancel_reservation(self, reservation_id: int):
        raise NotImplementedError("cancel_reservation não implementado")

    async def is_station_reserved_for_user(self, station_id: int, user_address: str):
        raise NotImplementedError("is_station_reserved_for_user não implementado")

    async def is_station_reserved_in_period(self, station_id: int, start_time, end_time):
        raise NotImplementedError("is_station_reserved_in_period não implementado")

    async def get_eth_balance(self, address: str):
        raise NotImplementedError("get_eth_balance não implementado")

    async def verify_signature(self, message: str, signature: str, address: str):
        raise NotImplementedError("verify_signature não implementado") 