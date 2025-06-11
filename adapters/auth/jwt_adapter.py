from datetime import datetime, timedelta
from typing import Dict, Optional
import jwt
from domain.ports.auth_port import AuthPort
from domain.exceptions.custom_exceptions import AuthenticationError
from shared.utils.logger import Logger
from shared.constants.config import Config
from shared.constants.texts import Texts

class JWTAdapter(AuthPort):
    """
    Adaptador JWT que implementa a interface AuthPort.
    Responsável por gerar e validar tokens JWT para autenticação.
    """
    
    def __init__(self):
        """
        Inicializa o adaptador JWT com a chave secreta.
        """
        self.logger = Logger(__name__)
        self.secret_key = Config.JWT_SECRET_KEY
        
    def generate_token(
        self,
        wallet_address: str,
        expires_in: Optional[int] = None
    ) -> str:
        """
        Gera um token JWT para autenticação.
        
        Args:
            wallet_address: Endereço da carteira do usuário
            expires_in: Tempo de expiração em segundos (opcional)
            
        Returns:
            str: Token JWT gerado
            
        Raises:
            AuthenticationError: Se houver erro ao gerar token
        """
        try:
            # Define payload
            payload = {
                "wallet_address": wallet_address,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(
                    seconds=expires_in or Config.JWT_EXPIRATION
                )
            }
            
            # Gera token
            token = jwt.encode(
                payload,
                self.secret_key,
                algorithm="HS256"
            )
            
            return token
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_JWT_GENERATE, str(e)))
            raise AuthenticationError(Texts.ERROR_JWT_GENERATE)
            
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Valida um token JWT.
        
        Args:
            token: Token JWT a ser validado
            
        Returns:
            Dict[str, Any]: Payload do token
            
        Raises:
            AuthenticationError: Se o token for inválido ou expirado
        """
        try:
            # Decodifica token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=["HS256"]
            )
            
            # Verifica expiração
            exp = datetime.fromtimestamp(payload["exp"])
            if exp < datetime.utcnow():
                raise AuthenticationError(Texts.ERROR_JWT_EXPIRED)
                
            return payload
            
        except jwt.ExpiredSignatureError:
            self.logger.error(Texts.ERROR_JWT_EXPIRED)
            raise AuthenticationError(Texts.ERROR_JWT_EXPIRED)
        except jwt.InvalidTokenError as e:
            self.logger.error(Texts.format(Texts.ERROR_JWT_VALIDATE, str(e)))
            raise AuthenticationError(Texts.ERROR_JWT_INVALID)
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_JWT_VALIDATE, str(e)))
            raise AuthenticationError(Texts.ERROR_JWT_VALIDATE)
            
    def get_wallet_address(self, token: str) -> str:
        """
        Obtém o endereço da carteira de um token JWT.
        
        Args:
            token: Token JWT
            
        Returns:
            str: Endereço da carteira
            
        Raises:
            AuthenticationError: Se o token for inválido
        """
        try:
            payload = self.validate_token(token)
            return payload["wallet_address"]
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_JWT_WALLET, str(e)))
            raise AuthenticationError(Texts.ERROR_JWT_WALLET)
            
    def refresh_token(self, token: str) -> str:
        """
        Gera um novo token JWT a partir de um token existente.
        
        Args:
            token: Token JWT atual
            
        Returns:
            str: Novo token JWT
            
        Raises:
            AuthenticationError: Se o token atual for inválido
        """
        try:
            # Valida token atual
            payload = self.validate_token(token)
            
            # Gera novo token
            return self.generate_token(
                wallet_address=payload["wallet_address"]
            )
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_JWT_REFRESH, str(e)))
            raise AuthenticationError(Texts.ERROR_JWT_REFRESH)
            
    def revoke_token(self, token: str) -> None:
        """
        Revoga um token JWT.
        
        Args:
            token: Token JWT a ser revogado
            
        Raises:
            AuthenticationError: Se houver erro ao revogar token
        """
        try:
            # TODO: Implementar lista negra de tokens
            # Por enquanto, apenas valida o token
            self.validate_token(token)
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_JWT_REVOKE, str(e)))
            raise AuthenticationError(Texts.ERROR_JWT_REVOKE)
            
    def verify_signature(
        self,
        message: str,
        signature: str,
        wallet_address: str
    ) -> bool:
        """
        Verifica uma assinatura Ethereum.
        
        Args:
            message: Mensagem original
            signature: Assinatura a ser verificada
            wallet_address: Endereço da carteira que assinou
            
        Returns:
            bool: True se a assinatura for válida
            
        Raises:
            AuthenticationError: Se houver erro na verificação
        """
        try:
            # TODO: Implementar verificação de assinatura
            # Por enquanto, retorna True
            return True
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_JWT_SIGNATURE, str(e)))
            raise AuthenticationError(Texts.ERROR_JWT_SIGNATURE) 