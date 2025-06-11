from typing import List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from domain.ports.email_port import EmailPort
from domain.exceptions.custom_exceptions import EmailError
from shared.utils.logger import Logger
from shared.constants.config import Config
from shared.constants.texts import Texts

class SMTPAdapter(EmailPort):
    """
    Adaptador SMTP que implementa a interface EmailPort.
    Responsável por enviar emails usando o protocolo SMTP.
    """
    
    def __init__(self):
        """
        Inicializa o adaptador SMTP com as configurações do servidor.
        """
        self.logger = Logger(__name__)
        
        # Configurações do servidor
        self.host = Config.SMTP_HOST
        self.port = Config.SMTP_PORT
        self.username = Config.SMTP_USERNAME
        self.password = Config.SMTP_PASSWORD
        self.use_tls = Config.SMTP_USE_TLS
        
        # Testa conexão
        self._test_connection()
        
    def _test_connection(self) -> None:
        """
        Testa a conexão com o servidor SMTP.
        
        Raises:
            EmailError: Se houver erro ao conectar
        """
        try:
            # Conecta ao servidor
            self.server = smtplib.SMTP(self.host, self.port)
            
            # Inicia TLS se configurado
            if self.use_tls:
                self.server.starttls()
                
            # Autentica
            self.server.login(self.username, self.password)
            
            self.logger.info(Texts.LOG_SMTP_CONNECTED)
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_SMTP_CONNECT, str(e)))
            raise EmailError(Texts.format(Texts.ERROR_SMTP_CONNECT, str(e)))
            
    def connect(self):
        """Conecta ao servidor SMTP."""
        try:
            self.server = smtplib.SMTP(self.host, self.port)
            self.server.starttls()
            self.server.login(self.username, self.password)
            self.logger.info(Texts.LOG_SMTP_CONNECTED)
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_SMTP_CONNECT, str(e)))
            raise EmailError(Texts.format(Texts.ERROR_SMTP_CONNECT, str(e)))

    def disconnect(self):
        """Desconecta do servidor SMTP."""
        try:
            if self.server:
                self.server.quit()
                self.server = None
                self.logger.info(Texts.LOG_SMTP_DISCONNECTED)
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_SMTP_DISCONNECT, str(e)))
            raise EmailError(Texts.format(Texts.ERROR_SMTP_DISCONNECT, str(e)))

    def send_email(self, to: str, subject: str, body: str, html: str = None) -> bool:
        """Envia um email."""
        try:
            # Cria mensagem
            msg = MIMEMultipart()
            msg["From"] = self.username
            msg["To"] = to
            msg["Subject"] = subject
            
            # Adiciona corpo do email
            msg.attach(MIMEText(body, "plain"))
            if html:
                msg.attach(MIMEText(html, "html"))
            
            # Envia email
            self.server.send_message(msg)
            self.logger.info(Texts.format(Texts.LOG_SMTP_EMAIL, to))
            return True
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_SMTP_SEND, str(e)))
            raise EmailError(Texts.format(Texts.ERROR_SMTP_SEND, str(e)))

    def send_template(self, to: str, template: str, data: dict) -> bool:
        """Envia um email usando um template."""
        try:
            # Carrega template
            template_path = f"templates/email/{template}.html"
            with open(template_path, "r") as f:
                html = f.read()
            
            # Substitui variáveis
            for key, value in data.items():
                html = html.replace(f"{{{{{key}}}}}", str(value))
            
            # Envia email
            return self.send_email(
                to=to,
                subject=data.get("subject", "Notificação"),
                body=data.get("text", ""),
                html=html
            )
            
        except FileNotFoundError:
            self.logger.error(Texts.format(Texts.ERROR_SMTP_TEMPLATE, f"Template não encontrado: {template}"))
            raise EmailError(Texts.format(Texts.ERROR_SMTP_TEMPLATE, f"Template não encontrado: {template}"))
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_SMTP_TEMPLATE, str(e)))
            raise EmailError(Texts.format(Texts.ERROR_SMTP_TEMPLATE, str(e)))

    def send_template_email(
        self,
        to_addresses: List[str],
        template_name: str,
        template_data: dict,
        subject: Optional[str] = None,
        cc_addresses: Optional[List[str]] = None,
        bcc_addresses: Optional[List[str]] = None
    ) -> None:
        """
        Envia um email usando um template.
        
        Args:
            to_addresses: Lista de endereços de destino
            template_name: Nome do template a ser usado
            template_data: Dados para preencher o template
            subject: Assunto do email (opcional)
            cc_addresses: Lista de endereços em cópia (opcional)
            bcc_addresses: Lista de endereços em cópia oculta (opcional)
            
        Raises:
            EmailError: Se houver erro ao enviar email
        """
        try:
            # TODO: Implementar renderização de template
            # Por enquanto, usa dados brutos
            body = str(template_data)
            html_body = f"<html><body>{body}</body></html>"
            
            # Envia email
            self.send_email(
                to=to_addresses[0],
                subject=subject or template_name,
                body=body,
                html=html_body
            )
            
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_SMTP_TEMPLATE_SEND, str(e)))
            raise EmailError(Texts.ERROR_SMTP_TEMPLATE_SEND_FAILED)
            
    def send_bulk_emails(
        self,
        email_list: List[dict],
        template_name: Optional[str] = None
    ) -> None:
        """
        Envia emails em lote.
        
        Args:
            email_list: Lista de dicionários com dados dos emails
            template_name: Nome do template a ser usado (opcional)
            
        Raises:
            EmailError: Se houver erro ao enviar emails
        """
        try:
            for email_data in email_list:
                if template_name:
                    self.send_template_email(
                        to_addresses=email_data["to_addresses"],
                        template_name=template_name,
                        template_data=email_data["template_data"],
                        subject=email_data.get("subject"),
                        cc_addresses=email_data.get("cc_addresses"),
                        bcc_addresses=email_data.get("bcc_addresses")
                    )
                else:
                    self.send_email(
                        to=email_data["to_addresses"][0],
                        subject=email_data["subject"],
                        body=email_data["body"],
                        html=email_data.get("html_body")
                    )
                    
        except Exception as e:
            self.logger.error(Texts.format(Texts.ERROR_SMTP_BULK_SEND, str(e)))
            raise EmailError(Texts.ERROR_SMTP_BULK_SEND_FAILED) 