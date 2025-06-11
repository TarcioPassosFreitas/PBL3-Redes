from shared.constants.texts import Texts

class EVChargingException(Exception):
    """Base exception for EV Charging application."""
    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class AuthenticationError(EVChargingException):
    """Raised when there are authentication issues."""
    def __init__(self, message: str = Texts.ERROR_HTTP_UNAUTHORIZED):
        super().__init__(message, "AUTHENTICATION_ERROR")


class InvalidWalletError(EVChargingException):
    """Raised when an invalid wallet address is provided."""
    def __init__(self, message: str = "Invalid wallet address"):
        super().__init__(message, "INVALID_WALLET")


class StationNotFoundError(EVChargingException):
    """Raised when a station is not found."""
    def __init__(self, station_id: int):
        super().__init__(Texts.format(Texts.STATION_NOT_FOUND, str(station_id)), "STATION_NOT_FOUND")


class StationNotAvailableError(EVChargingException):
    """Raised when a station is not available for use."""
    def __init__(self, station_id: int):
        super().__init__(f"Estação {station_id} não está disponível", "STATION_NOT_AVAILABLE")


class StationAlreadyReservedError(EVChargingException):
    """Raised when trying to reserve an already reserved station."""
    def __init__(self, station_id: int, time: str):
        super().__init__(
            Texts.format(Texts.ERROR_STATION_ALREADY_RESERVED, str(station_id), time),
            "STATION_ALREADY_RESERVED"
        )


class SessionNotFoundError(EVChargingException):
    """Raised when a session is not found."""
    def __init__(self, session_id: int):
        super().__init__(Texts.format(Texts.SESSION_NOT_FOUND, str(session_id)), "SESSION_NOT_FOUND")


class SessionAlreadyEndedError(EVChargingException):
    """Raised when trying to end an already ended session."""
    def __init__(self, session_id: int):
        super().__init__(f"Sessão {session_id} já foi encerrada", "SESSION_ALREADY_ENDED")


class SessionNotPaidError(EVChargingException):
    """Raised when trying to end a session that hasn't been paid."""
    def __init__(self, session_id: int):
        super().__init__(Texts.format(Texts.ERROR_SESSION_NOT_PAID, str(session_id)), "SESSION_NOT_PAID")


class InsufficientPaymentError(EVChargingException):
    """Raised when payment amount is insufficient."""
    def __init__(self, required: str, provided: str):
        super().__init__(
            f"Valor do pagamento insuficiente. "
            f"Valor necessário: {required} ETH, "
            f"Valor fornecido: {provided} ETH",
            "INSUFFICIENT_PAYMENT"
        )


class BlockchainError(EVChargingException):
    """Raised when there are blockchain-related errors."""
    def __init__(self, message: str = Texts.BLOCKCHAIN_ERROR):
        super().__init__(message, "BLOCKCHAIN_ERROR")


class BlockchainTransactionError(BlockchainError):
    """Raised when a blockchain transaction fails."""
    def __init__(self, message: str = Texts.BLOCKCHAIN_TX_FAILED):
        super().__init__(message)


class BlockchainNetworkError(BlockchainError):
    """Raised when there are network issues with the blockchain."""
    def __init__(self, message: str = Texts.ERROR_BLOCKCHAIN_NETWORK):
        super().__init__(message)


class BlockchainInsufficientBalanceError(BlockchainError):
    """Raised when there is insufficient balance for a transaction."""
    def __init__(self, message: str = Texts.BLOCKCHAIN_INSUFFICIENT_BALANCE):
        super().__init__(message)


class BlockchainInvalidAddressError(BlockchainError):
    """Raised when an invalid blockchain address is provided."""
    def __init__(self, message: str = Texts.ERROR_BLOCKCHAIN_INVALID_ADDRESS):
        super().__init__(message)


class BlockchainInvalidContractError(BlockchainError):
    """Raised when there are issues with the smart contract."""
    def __init__(self, message: str = Texts.BLOCKCHAIN_INVALID_CONTRACT):
        super().__init__(message)


class BlockchainTimeoutError(BlockchainError):
    """Raised when a blockchain operation times out."""
    def __init__(self, message: str = Texts.ERROR_BLOCKCHAIN_TIMEOUT):
        super().__init__(message)


class CacheError(EVChargingException):
    """Raised when there are cache-related errors."""
    def __init__(self, message: str = Texts.ERROR_CACHE):
        super().__init__(message, "CACHE_ERROR")


class EmailError(EVChargingException):
    """Raised when there are email-related errors."""
    def __init__(self, message: str = Texts.ERROR_EMAIL_SEND_FAILED):
        super().__init__(message, "EMAIL_ERROR")


class NotificationError(EVChargingException):
    """Raised when there are notification-related errors."""
    def __init__(self, message: str = Texts.ERROR_NOTIFICATION):
        super().__init__(message, "NOTIFICATION_ERROR")


class InvalidReservationTimeError(EVChargingException):
    """Raised when reservation time is invalid."""
    def __init__(self, message: str = Texts.STATION_RESERVATION_INVALID_TIME):
        super().__init__(message, "INVALID_RESERVATION_TIME")


class UserNotFoundError(EVChargingException):
    """Raised when a user is not found."""
    def __init__(self, wallet_address: str):
        super().__init__(
            Texts.format(Texts.USER_NOT_FOUND, wallet_address),
            "USER_NOT_FOUND"
        )


class ValidationError(EVChargingException):
    """Raised when there are validation issues."""
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class ResourceNotFoundError(EVChargingException):
    """Raised when a requested resource is not found."""
    def __init__(self, message: str = Texts.NOT_FOUND):
        super().__init__(message, "RESOURCE_NOT_FOUND")


class ResourceConflictError(EVChargingException):
    """Raised when there is a conflict with a resource."""
    def __init__(self, message: str):
        super().__init__(message, "RESOURCE_CONFLICT")


class StationInUseError(ResourceConflictError):
    """
    Exceção lançada quando uma estação está em uso.
    """

    def __init__(self, station_id: int):
        super().__init__(
            Texts.format(Texts.STATION_NOT_AVAILABLE, str(station_id))
        )


class StationNotReservedError(ResourceConflictError):
    """
    Exceção lançada quando uma estação não está reservada.
    """

    def __init__(self, station_id: int):
        super().__init__(
            Texts.format(Texts.STATION_RESERVATION_NOT_FOUND, str(station_id))
        )


class SessionNotActiveError(ResourceConflictError):
    """
    Exceção lançada quando uma sessão não está ativa.
    """

    def __init__(self, session_id: int):
        super().__init__(
            Texts.format(Texts.SESSION_NOT_ACTIVE, str(session_id))
        )


class SessionAlreadyActiveError(ResourceConflictError):
    """
    Exceção lançada quando uma sessão já está ativa.
    """

    def __init__(self, session_id: int):
        super().__init__(
            Texts.format(Texts.SESSION_ALREADY_ENDED, str(session_id))
        )


class SessionAlreadyPaidError(ResourceConflictError):
    """
    Exceção lançada quando uma sessão já está paga.
    """

    def __init__(self, session_id: int):
        super().__init__(
            str(session_id),
            "Sessão já está paga"
        )


class ReservationExpiredError(ResourceConflictError):
    """
    Exceção lançada quando uma reserva expirou.
    """

    def __init__(self, reservation_id: int):
        super().__init__(
            Texts.format(Texts.STATION_RESERVATION_INVALID_TIME, str(reservation_id)),
            "RESERVATION_EXPIRED"
        )


class ReservationCancelledError(ResourceConflictError):
    """
    Exceção lançada quando uma reserva está cancelada.
    """

    def __init__(self, reservation_id: int):
        super().__init__(
            str(reservation_id),
            "Reserva está cancelada"
        )


class ReservationNotFoundError(ResourceNotFoundError):
    """Raised when a reservation is not found."""
    def __init__(self, reservation_id: int):
        super().__init__(Texts.format(Texts.STATION_RESERVATION_NOT_FOUND, str(reservation_id)))


class BlockchainContractError(EVChargingException):
    """Raised when there is a contract error on the blockchain."""
    def __init__(self, message: str = Texts.ERROR_BLOCKCHAIN_CONTRACT):
        super().__init__(message, "BLOCKCHAIN_CONTRACT_ERROR")


class DatabaseError(EVChargingException):
    """Raised when there are database-related errors."""
    def __init__(self, message: str = Texts.ERROR_DATABASE):
        super().__init__(message, "DATABASE_ERROR")


class PaymentError(EVChargingException):
    """Raised when there are payment-related errors."""
    def __init__(self, message: str = Texts.ERROR_PAYMENT_PROCESS):
        super().__init__(message, "PAYMENT_ERROR") 