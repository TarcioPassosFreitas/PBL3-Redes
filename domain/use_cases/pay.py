from decimal import Decimal
from typing import Optional

from domain.entities.session import Session
from domain.entities.user import User
from domain.exceptions.custom_exceptions import (
    SessionNotFoundError,
    SessionNotPaidError,
    InsufficientPaymentError,
    UserNotFoundError,
    ValidationError
)
from domain.ports.blockchain_port import BlockchainPort
from domain.ports.http_port import HTTPPort
from domain.ports.database_port import DatabasePort
from domain.ports.notification_port import NotificationPort
from shared.utils.logger import Logger
from shared.constants.texts import Texts


class PaymentUseCase:
    """
    Caso de uso para processamento de pagamentos.
    Esta classe implementa a lógica de negócio para pagamentos de sessões.
    """

    def __init__(self, blockchain_port: BlockchainPort, http_port: HTTPPort):
        self.blockchain_port = blockchain_port
        self.http_port = http_port

    async def process_payment(
        self,
        user_address: str,
        session_id: int,
        amount_str: str
    ) -> dict:
        """
        Processa o pagamento de uma sessão de carregamento.
        
        Args:
            user_address: Endereço da carteira do usuário
            session_id: ID da sessão
            amount_str: Valor do pagamento em ETH
            
        Returns:
            dict: Detalhes do pagamento processado
            
        Raises:
            ValidationError: Se os dados de entrada forem inválidos
            UserNotFoundError: Se o usuário não existir
            SessionNotFoundError: Se a sessão não existir
            SessionNotPaidError: Se a sessão não estiver finalizada
            InsufficientPaymentError: Se o valor do pagamento for insuficiente
        """
        # Valida endereço da carteira
        if not await self.http_port.validate_wallet_address(user_address):
            raise ValidationError(Texts.VALIDATION_INVALID_WALLET_ADDRESS)

        # Converte e valida valor
        try:
            amount = await self.http_port.parse_decimal(amount_str)
        except ValueError as e:
            raise ValidationError(Texts.format(Texts.VALIDATION_INVALID_AMOUNT, str(e)))

        # Obtém usuário e sessão
        try:
            user = await self.blockchain_port.get_user(user_address)
            session = await self.blockchain_port.get_session(session_id)
        except UserNotFoundError:
            raise UserNotFoundError(user_address)
        except SessionNotFoundError:
            raise SessionNotFoundError(session_id)

        # Valida propriedade da sessão
        if session.user_address != user_address:
            raise ValidationError(Texts.SESSION_NOT_OWNED)

        # Verifica se sessão está ativa
        if session.is_active:
            raise SessionNotPaidError(session_id)

        # Verifica se sessão já foi paga
        if session.is_paid:
            raise ValidationError(Texts.SESSION_PAYMENT_ALREADY_PAID)

        # Calcula valor do pagamento
        required_amount = self._calculate_payment_amount(session)

        # Valida valor do pagamento
        if amount < required_amount:
            raise InsufficientPaymentError(
                str(required_amount),
                str(amount)
            )

        # Verifica saldo ETH do usuário
        balance = await self.blockchain_port.get_eth_balance(user_address)
        if balance < amount:
            raise InsufficientPaymentError(
                str(amount),
                str(balance)
            )

        # Processa pagamento na blockchain
        await self.blockchain_port.pay_session(
            session_id=session_id,
            amount=amount
        )

        # Obtém detalhes atualizados da sessão
        session = await self.blockchain_port.get_session(session_id)

        # Atualiza total de carregamentos do usuário
        user.add_charge(amount)

        return await self.http_port.format_session_response(session)

    def _calculate_payment_amount(self, session: Session) -> Decimal:
        """
        Calcula o valor do pagamento necessário para uma sessão.
        
        Args:
            session: A sessão para calcular o pagamento
            
        Returns:
            O valor do pagamento necessário em ETH
        """
        if not session.duration:
            raise ValidationError(Texts.VALIDATION_ACTIVE_SESSION_PAYMENT)

        # Taxa base: 0.001 ETH por hora
        base_rate = Decimal('0.001')
        
        # Calcula horas (arredonda para cima para hora mais próxima)
        hours = Decimal(str(session.duration_hours)).quantize(Decimal('1'), rounding='ROUND_CEILING')
        
        return base_rate * hours

    async def get_payment_details(self, user_address: str, session_id: int) -> dict:
        """
        Obtém detalhes do pagamento de uma sessão.
        
        Args:
            user_address: O endereço da carteira do usuário
            session_id: O ID da sessão para obter detalhes do pagamento
            
        Returns:
            Um dicionário com os detalhes do pagamento
            
        Raises:
            ValidationError: Se os dados de entrada forem inválidos
            SessionNotFoundError: Se a sessão não existir
            UserNotFoundError: Se o usuário não existir
        """
        # Valida endereço da carteira
        if not await self.http_port.validate_wallet_address(user_address):
            raise ValidationError(Texts.VALIDATION_INVALID_WALLET_ADDRESS)

        # Obtém usuário e sessão
        try:
            user = await self.blockchain_port.get_user(user_address)
            session = await self.blockchain_port.get_session(session_id)
        except UserNotFoundError:
            raise UserNotFoundError(user_address)
        except SessionNotFoundError:
            raise SessionNotFoundError(session_id)

        # Valida propriedade da sessão
        if session.user_address != user_address:
            raise ValidationError(Texts.SESSION_NOT_OWNED)

        # Calcula valor necessário se sessão estiver finalizada mas não paga
        required_amount = None
        if not session.is_active and not session.is_paid:
            required_amount = str(self._calculate_payment_amount(session))

        # Obtém saldo ETH do usuário
        balance = await self.blockchain_port.get_eth_balance(user_address)

        # Retorna detalhes do pagamento
        return {
            "session_id": session_id,
            "user_address": user_address,
            "status": "paid" if session.is_paid else "pending" if not session.is_active else "active",
            "amount_paid": str(session.amount) if session.amount else None,
            "required_amount": required_amount,
            "user_balance": str(balance),
            "session": await self.http_port.format_session_response(session)
        } 