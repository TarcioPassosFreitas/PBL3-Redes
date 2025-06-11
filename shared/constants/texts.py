class Texts:
    """
    Constantes de texto para mensagens e respostas.
    """

    # Mensagens gerais
    SUCCESS = "Operação concluída com sucesso"
    ERROR = "Ocorreu um erro"
    INVALID_REQUEST = "Requisição inválida"
    UNAUTHORIZED = "Acesso não autorizado"
    FORBIDDEN = "Acesso proibido"
    NOT_FOUND = "Recurso não encontrado"
    VALIDATION_ERROR = "Erro de validação"

    # Mensagens de autenticação
    AUTH_REQUIRED = "Autenticação necessária"
    INVALID_TOKEN = "Token de autenticação inválido"
    TOKEN_EXPIRED = "Token de autenticação expirado"
    INVALID_SIGNATURE = "Assinatura inválida"
    INVALID_WALLET = "Endereço de carteira inválido"

    # Mensagens de sessão
    SESSION_STARTED = "Sessão de carregamento iniciada com sucesso"
    SESSION_ENDED = "Sessão de carregamento finalizada com sucesso"
    SESSION_NOT_FOUND = "Sessão de carregamento não encontrada"
    SESSION_ALREADY_ENDED = "Sessão de carregamento já finalizada"
    SESSION_NOT_ACTIVE = "Sessão de carregamento não está ativa"
    SESSION_NOT_OWNED = "Usuário não é dono desta sessão"
    SESSION_PAYMENT_REQUIRED = "Pagamento necessário para a sessão"
    SESSION_PAYMENT_COMPLETED = "Pagamento concluído com sucesso"
    SESSION_PAYMENT_INSUFFICIENT = "Valor do pagamento insuficiente"
    SESSION_PAYMENT_ALREADY_PAID = "Sessão já paga"
    SESSION_PAYMENT_PENDING = "Pagamento pendente"
    
    # Mensagens de erro de sessão
    ERROR_SESSION_START = "Erro ao iniciar sessão: {}"
    ERROR_SESSION_END = "Erro ao finalizar sessão: {}"
    ERROR_SESSION_GET = "Erro ao obter sessão: {}"
    ERROR_SESSION_LIST_USER = "Erro ao listar sessões do usuário: {}"
    ERROR_SESSION_LIST_STATION = "Erro ao listar sessões da estação: {}"
    ERROR_SESSION_PAYMENT = "Erro ao processar pagamento: {}"

    # Mensagens de estação
    STATION_NOT_FOUND = "Estação de carregamento não encontrada"
    STATION_NOT_AVAILABLE = "Estação de carregamento não está disponível"
    STATION_ALREADY_RESERVED = "Estação de carregamento já reservada"
    STATION_RESERVATION_CREATED = "Reserva de estação criada com sucesso"
    STATION_RESERVATION_CANCELLED = "Reserva de estação cancelada com sucesso"
    STATION_RESERVATION_NOT_FOUND = "Reserva de estação não encontrada"
    STATION_RESERVATION_INVALID_TIME = "Horário de reserva inválido"
    STATION_RESERVATION_TOO_SHORT = "Duração mínima da reserva é de 1 hora"
    STATION_RESERVATION_TOO_LONG = "Duração máxima da reserva é de 24 horas"

    # Mensagens de usuário
    USER_NOT_FOUND = "Usuário não encontrado"
    USER_CREATED = "Usuário criado com sucesso"
    USER_UPDATED = "Usuário atualizado com sucesso"
    USER_DELETED = "Usuário excluído com sucesso"
    USER_ALREADY_EXISTS = "Usuário já existe"

    # Mensagens de blockchain
    BLOCKCHAIN_ERROR = "Operação na blockchain falhou"
    BLOCKCHAIN_TX_FAILED = "Transação na blockchain falhou"
    BLOCKCHAIN_TX_PENDING = "Transação na blockchain pendente"
    BLOCKCHAIN_TX_CONFIRMED = "Transação na blockchain confirmada"
    BLOCKCHAIN_TX_REVERTED = "Transação na blockchain revertida"
    BLOCKCHAIN_INSUFFICIENT_BALANCE = "Saldo insuficiente na blockchain"
    BLOCKCHAIN_INVALID_ADDRESS = "Endereço na blockchain inválido"
    BLOCKCHAIN_INVALID_CONTRACT = "Contrato inteligente inválido"
    BLOCKCHAIN_NETWORK_ERROR = "Erro na rede blockchain"

    # Mensagens de validação
    VALIDATION_INVALID_AMOUNT = "Valor inválido: {}"
    VALIDATION_INVALID_DATETIME = "Data/hora inválida: {}"
    VALIDATION_INVALID_DURATION = "Duração inválida"
    VALIDATION_INVALID_STATION_ID = "ID da estação inválido"
    VALIDATION_INVALID_SESSION_ID = "ID da sessão inválido"
    VALIDATION_INVALID_WALLET_ADDRESS = "Endereço da carteira inválido"
    VALIDATION_INVALID_SIGNATURE = "Assinatura inválida"
    VALIDATION_MISSING_REQUIRED_FIELD = "Campo obrigatório ausente: {}"
    VALIDATION_INVALID_FIELD_TYPE = "Tipo de campo inválido para: {}"
    VALIDATION_FIELD_TOO_SHORT = "Campo muito curto: {}"
    VALIDATION_FIELD_TOO_LONG = "Campo muito longo: {}"
    VALIDATION_FIELD_INVALID_FORMAT = "Formato inválido para o campo: {}"
    VALIDATION_INVALID_STATUS = "Status inválido"
    VALIDATION_INVALID_START_TIME = "Horário de início não pode ser no passado"
    VALIDATION_ACTIVE_SESSION_PAYMENT = "Não é possível calcular pagamento para sessão ativa"
    VALIDATION_NOT_OWNER = "Usuário não é dono desta {}"

    # Mensagens de resposta da API
    API_SUCCESS = "Requisição à API bem-sucedida"
    API_ERROR = "Falha na requisição à API"
    API_INVALID_METHOD = "Método HTTP inválido"
    API_INVALID_ENDPOINT = "Endpoint da API inválido"
    API_RATE_LIMITED = "Limite de requisições à API excedido"
    API_MAINTENANCE = "API em manutenção"
    API_VERSION_DEPRECATED = "Versão da API obsoleta"
    API_VERSION_NOT_SUPPORTED = "Versão da API não suportada"

    # Mensagens de erro
    ERROR_INTERNAL = "Erro interno do servidor"
    ERROR_DATABASE = "Erro no banco de dados"
    ERROR_NETWORK = "Erro de rede"
    ERROR_TIMEOUT = "Tempo limite da requisição excedido"
    ERROR_CONNECTION = "Erro de conexão"
    ERROR_CONFIGURATION = "Erro de configuração"
    ERROR_DEPENDENCY = "Erro de dependência"
    ERROR_UNKNOWN = "Erro desconhecido ocorreu"

    # Mensagens de erro de adaptadores
    ERROR_ADAPTER_INIT = "Erro ao inicializar adaptador: {}"
    ERROR_ADAPTER_CONNECTION = "Erro de conexão no adaptador: {}"
    ERROR_ADAPTER_OPERATION = "Erro na operação do adaptador: {}"

    # Mensagens de erro de Firebase
    ERROR_FIREBASE_INIT = "Erro ao inicializar Firebase: {}"
    ERROR_FIREBASE_API = "Erro da API Firebase: {}"
    ERROR_FIREBASE_NOTIFICATION = "Erro ao enviar notificação: {}"
    ERROR_FIREBASE_SUBSCRIBE = "Erro ao inscrever dispositivos: {}"
    ERROR_FIREBASE_VALIDATE = "Erro ao validar token: {}"

    # Mensagens de erro de Blockchain
    ERROR_BLOCKCHAIN_CONTRACT = "Erro no contrato: {}"
    ERROR_BLOCKCHAIN_RESERVATION = "Erro ao criar reserva: {}"
    ERROR_BLOCKCHAIN_SESSION_START = "Erro ao iniciar sessão: {}"
    ERROR_BLOCKCHAIN_SESSION_END = "Erro ao finalizar sessão: {}"
    ERROR_BLOCKCHAIN_PAYMENT = "Erro ao processar pagamento: {}"
    ERROR_BLOCKCHAIN_SESSION_DETAILS = "Erro ao obter detalhes da sessão: {}"
    ERROR_BLOCKCHAIN_DEPLOY = "Falha na implantação: {}"
    ERROR_BLOCKCHAIN_INVALID_ADDRESS = "Endereço inválido: {}"
    ERROR_BLOCKCHAIN_SIGNATURE = "Erro na verificação de assinatura: {}"
    ERROR_BLOCKCHAIN_SIGNATURE_FAILED = "Falha ao verificar assinatura"
    ERROR_BLOCKCHAIN_TRANSACTION_FAILED = "Transação falhou"
    ERROR_BLOCKCHAIN_TIMEOUT = "Timeout na transação"
    ERROR_BLOCKCHAIN_WAIT = "Falha ao aguardar transação: {}"
    ERROR_BLOCKCHAIN_USER_SESSIONS = "Falha ao obter sessões do usuário: {}"
    ERROR_BLOCKCHAIN_USER_SESSIONS_RETRIEVAL = "Erro ao recuperar sessões do usuário: {}"
    ERROR_BLOCKCHAIN_BALANCE = "Erro ao verificar saldo: {}"
    ERROR_BLOCKCHAIN_BALANCE_FAILED = "Falha ao obter saldo: {}"
    ERROR_BLOCKCHAIN_STATION_DETAILS = "Erro ao obter detalhes da estação: {}"
    ERROR_BLOCKCHAIN_STATION_DETAILS_FAILED = "Falha ao obter detalhes da estação: {}"
    ERROR_BLOCKCHAIN_USER_DETAILS = "Erro ao obter detalhes do usuário: {}"
    ERROR_BLOCKCHAIN_USER_DETAILS_FAILED = "Falha ao obter detalhes do usuário: {}"
    ERROR_BLOCKCHAIN_ADDRESS_VALIDATION = "Erro na validação de endereço: {}"
    ERROR_BLOCKCHAIN_NETWORK = "Não foi possível conectar à rede blockchain"
    ERROR_BLOCKCHAIN_INSUFFICIENT_BALANCE = "Saldo insuficiente para pagamento"

    # Mensagens de erro de JWT
    ERROR_JWT_GENERATE = "Erro ao gerar token: {}"
    ERROR_JWT_VALIDATE = "Erro ao validar token: {}"
    ERROR_JWT_WALLET = "Erro ao obter endereço da carteira: {}"
    ERROR_JWT_EXPIRED = "Token expirado"
    ERROR_JWT_INVALID = "Token inválido"
    ERROR_JWT_REVOKE = "Falha ao revogar token"
    ERROR_JWT_REFRESH = "Falha ao atualizar token"
    ERROR_JWT_SIGNATURE = "Falha ao verificar assinatura"

    # Mensagens de erro de Redis
    ERROR_REDIS_CONNECT = "Erro ao conectar ao Redis: {}"

    # Mensagens de erro de SMTP
    ERROR_SMTP_CONNECT = "Erro ao conectar ao servidor SMTP: {}"

    # Mensagens de erro de HTTP
    ERROR_HTTP_UNAUTHORIZED = "Não autorizado"
    ERROR_HTTP_INVALID_DATA = "Dados inválidos"
    ERROR_HTTP_NOT_FOUND = "Recurso não encontrado"
    ERROR_HTTP_CONFLICT = "Conflito"
    ERROR_HTTP_BLOCKCHAIN = "Erro na blockchain"
    ERROR_HTTP_INTERNAL = "Erro interno"
    ERROR_HTTP_UNEXPECTED = "Ocorreu um erro inesperado"

    # Mensagens de log
    LOG_REQUEST = "Requisição HTTP: {} {} - Status: {} - Duração: {:.2f}s"
    LOG_RESPONSE = "Resposta: {} - {}"
    LOG_BLOCKCHAIN_TX = "Transação Blockchain: {} - Status: {}"
    LOG_SESSION_EVENT = "Evento de sessão {}: {}"
    LOG_STATION_EVENT = "Evento de Estação {}: {}"
    LOG_PAYMENT_EVENT = "Evento de Pagamento (Sessão {}): {} ETH - Status: {}"
    LOG_ERROR = "Erro: {}"
    LOG_ERROR_CONTEXT = "Erro: {} - Contexto: {}"

    # Mensagens de erro de validação
    ERROR_VALIDATION_MISSING_BODY = "Corpo da requisição ausente"
    ERROR_VALIDATION_MISSING_FIELD = "Campo obrigatório ausente: {}"
    ERROR_VALIDATION_INVALID_DATA = "Dados inválidos: {}"
    ERROR_VALIDATION_INVALID_FORMAT = "Formato inválido: {}"

    # Mensagens de erro de cache
    ERROR_CACHE_DECODE = "Erro ao decodificar valor: {}"
    ERROR_CACHE_DECODE_FAILED = "Falha ao decodificar valor do cache"
    ERROR_CACHE_CONNECTION = "Erro ao conectar ao cache: {}"
    ERROR_CACHE_OPERATION = "Erro na operação de cache: {}"

    # Mensagens de erro de banco de dados
    ERROR_DATABASE_CREATE = "Erro ao criar registro: {}"
    ERROR_DATABASE_CREATE_FAILED = "Falha ao criar registro"
    ERROR_DATABASE_READ = "Erro ao ler registro: {}"
    ERROR_DATABASE_UPDATE = "Erro ao atualizar registro: {}"
    ERROR_DATABASE_DELETE = "Erro ao excluir registro: {}"
    ERROR_DATABASE_CONNECTION = "Erro ao conectar ao banco de dados: {}"
    ERROR_DATABASE_OPERATION = "Erro na operação de banco de dados: {}"

    # Mensagens de erro de email
    ERROR_EMAIL_SEND = "Erro ao enviar email: {}"
    ERROR_EMAIL_SEND_FAILED = "Erro ao enviar e-mail"
    ERROR_EMAIL_TEMPLATE = "Erro ao processar template de email: {}"
    ERROR_EMAIL_ATTACHMENT = "Erro ao anexar arquivo: {}"

    # Mensagens de erro de pagamento
    ERROR_PAYMENT_PROCESS = "Erro ao processar pagamento: {}"
    ERROR_PAYMENT_PROCESS_FAILED = "Falha ao processar pagamento"
    ERROR_PAYMENT_REFUND = "Erro ao processar reembolso: {}"
    ERROR_PAYMENT_REFUND_FAILED = "Falha ao processar reembolso"
    ERROR_PAYMENT_INSUFFICIENT = "Saldo insuficiente para pagamento"
    ERROR_PAYMENT_INVALID = "Dados de pagamento inválidos"

    # Mensagens de reserva
    RESERVATION_NOT_OWNED = "Usuário não é dono desta reserva"

    # Mensagens de erro de exceções
    ERROR_STATION_ALREADY_RESERVED = "Estação {} já está reservada às {}"
    ERROR_SESSION_NOT_PAID = "Sessão {} não está paga"
    ERROR_BLOCKCHAIN_INVALID_ADDRESS = "Endereço inválido: {}"
    ERROR_BLOCKCHAIN_TRANSACTION_FAILED = "Transação falhou"
    ERROR_BLOCKCHAIN_NETWORK = "Não foi possível conectar à rede blockchain"
    ERROR_BLOCKCHAIN_DEPLOYER_CONFIG = "Endereço ou chave privada do deployer não configurados"
    ERROR_BLOCKCHAIN_CONTRACT_DEPLOYED = "Contrato implantado com sucesso em: {}"

    # Mensagens de log
    LOG_BLOCKCHAIN_TRANSACTION = "Transação Blockchain: {} - {} - {}"
    LOG_BLOCKCHAIN_RESERVATION = "Reserva Blockchain: {} - {} - {}"
    LOG_BLOCKCHAIN_SESSION = "Sessão Blockchain: {} - {} - {}"
    LOG_BLOCKCHAIN_PAYMENT = "Pagamento Blockchain: {} - {} - {}"
    LOG_BLOCKCHAIN_USER = "Usuário Blockchain: {} - {} - {}"
    LOG_BLOCKCHAIN_STATION = "Estação Blockchain: {} - {} - {}"

    # Adapter Connection Errors
    ERROR_ADAPTER_CONNECTION = "Falha ao conectar ao {}"
    ERROR_ADAPTER_INIT = "Falha ao inicializar adaptador {}"
    ERROR_ADAPTER_OPERATION = "Falha na operação do adaptador {}"

    # Redis Cache Errors
    ERROR_REDIS_CONNECT = "Erro ao conectar ao Redis: {}"
    ERROR_CACHE_DECODE = "Erro ao decodificar valor do cache: {}"
    ERROR_CACHE_DECODE_FAILED = "Falha ao decodificar valor do cache"
    ERROR_CACHE_OPERATION = "Erro na operação do cache: {}"

    # SMTP Email Errors
    ERROR_SMTP_CONNECT = "Erro ao conectar ao servidor SMTP: {}"

    # JWT Authentication Errors
    ERROR_JWT_GENERATE = "Falha ao gerar token JWT"
    ERROR_JWT_EXPIRED = "Token JWT expirado"
    ERROR_JWT_INVALID = "Token JWT inválido"
    ERROR_JWT_VALIDATE = "Erro ao validar token JWT: {}"
    ERROR_JWT_WALLET = "Falha ao obter endereço da carteira do token"
    ERROR_JWT_REFRESH = "Falha ao atualizar token JWT"

    # Firebase Notification Errors
    ERROR_FIREBASE_INIT = "Erro ao inicializar Firebase: {}"
    ERROR_FIREBASE_API = "Erro na API do Firebase: {}"
    ERROR_FIREBASE_VALIDATE = "Falha ao validar token do Firebase"

    # Blockchain Logging
    LOG_BLOCKCHAIN_RESERVATION = "Reserva {}: tx={}, data={}"
    LOG_BLOCKCHAIN_SESSION = "Sessão {}: tx={}, data={}"
    LOG_BLOCKCHAIN_PAYMENT = "Pagamento: tx={}, data={}"
    LOG_ERROR = "Erro: {}"

    # Blockchain Errors
    ERROR_BLOCKCHAIN_ADDRESS_VALIDATION = "Erro ao validar endereço: {}"
    ERROR_BLOCKCHAIN_INVALID_ADDRESS = "Endereço inválido: {}"
    ERROR_BLOCKCHAIN_BALANCE = "Erro ao consultar saldo: {}"
    ERROR_BLOCKCHAIN_BALANCE_FAILED = "Falha ao consultar saldo"
    ERROR_BLOCKCHAIN_CONTRACT = "Erro no contrato: {}"
    ERROR_BLOCKCHAIN_RESERVATION = "Erro na reserva: {}"
    ERROR_BLOCKCHAIN_SESSION_START = "Erro ao iniciar sessão: {}"
    ERROR_BLOCKCHAIN_SESSION_END = "Erro ao encerrar sessão: {}"
    ERROR_BLOCKCHAIN_PAYMENT = "Erro no pagamento: {}"
    ERROR_BLOCKCHAIN_SESSION_DETAILS = "Erro ao obter detalhes da sessão: {}"
    ERROR_BLOCKCHAIN_STATION_DETAILS = "Erro ao obter detalhes da estação: {}"
    ERROR_BLOCKCHAIN_STATION_DETAILS_FAILED = "Falha ao obter detalhes da estação"
    ERROR_BLOCKCHAIN_USER_DETAILS = "Erro ao obter detalhes do usuário: {}"
    ERROR_BLOCKCHAIN_USER_DETAILS_FAILED = "Falha ao obter detalhes do usuário"
    ERROR_BLOCKCHAIN_USER_SESSIONS_RETRIEVAL = "Erro ao obter sessões do usuário: {}"
    ERROR_BLOCKCHAIN_USER_SESSIONS = "Falha ao obter sessões do usuário"
    ERROR_BLOCKCHAIN_WAIT = "Erro ao aguardar transação: {}"
    ERROR_BLOCKCHAIN_TIMEOUT = "Timeout ao aguardar transação"
    ERROR_BLOCKCHAIN_INSUFFICIENT_BALANCE = "Saldo insuficiente para realizar a operação"
    ERROR_BLOCKCHAIN_TRANSACTION_FAILED = "Transação falhou"

    # HTTP Response Errors
    ERROR_HTTP_UNAUTHORIZED = "Não autorizado"
    ERROR_HTTP_INVALID_DATA = "Dados inválidos"
    ERROR_HTTP_NOT_FOUND = "Recurso não encontrado"
    ERROR_HTTP_CONFLICT = "Conflito"
    ERROR_HTTP_BLOCKCHAIN = "Erro na blockchain"
    ERROR_HTTP_INTERNAL = "Erro interno"
    ERROR_HTTP_UNEXPECTED = "Erro inesperado"

    # Database Errors
    ERROR_DATABASE_COMMIT = "Erro ao confirmar transação: {}"
    ERROR_DATABASE_COMMIT_FAILED = "Falha ao confirmar transação"
    ERROR_DATABASE_ROLLBACK = "Erro ao reverter transação: {}"
    ERROR_DATABASE_ROLLBACK_FAILED = "Falha ao reverter transação"

    # Reservation Logging
    LOG_RESERVATION_EVENT = "Evento de reserva {}: {}"

    # Reservation Errors
    ERROR_RESERVATION_CREATE = "Erro ao criar reserva: {}"
    ERROR_RESERVATION_CANCEL = "Erro ao cancelar reserva: {}"
    ERROR_RESERVATION_GET = "Erro ao obter reserva: {}"
    ERROR_RESERVATION_LIST_USER = "Erro ao listar reservas do usuário: {}"

    # User Errors
    ERROR_USER_PROFILE = "Erro ao obter perfil do usuário: {}"
    ERROR_USER_BALANCE = "Erro ao obter saldo do usuário: {}"
    ERROR_USER_STATS = "Erro ao obter estatísticas do usuário: {}"
    ERROR_USER_HISTORY = "Erro ao obter histórico do usuário: {}"

    # Station Errors
    ERROR_STATION_LIST = "Erro ao listar estações: {}"
    ERROR_STATION_GET = "Erro ao obter estação: {}"
    ERROR_STATION_STATUS = "Erro ao obter status da estação: {}"
    ERROR_STATION_AVAILABILITY = "Erro ao obter disponibilidade da estação: {}"
    ERROR_STATION_STATS = "Erro ao obter estatísticas da estação: {}"

    # Payment Logging
    LOG_PAYMENT_EVENT = "Evento de pagamento {}: {}"

    # Payment Errors
    ERROR_PAYMENT_PROCESS = "Erro ao processar pagamento: {}"
    ERROR_PAYMENT_LIST_STATION = "Erro ao listar pagamentos da estação: {}"

    # Deploy de Contrato
    LOG_CONTRACT_COMPILED = "Contrato compilado com sucesso"
    LOG_CONTRACT_DEPLOYED = "Contrato implantado com sucesso em: {}"
    LOG_CONTRACT_COMPILATION_COMPLETE = "Compilação concluída"
    LOG_CONTRACT_DEPLOYMENT_COMPLETE = "Implantaçao concluída. Endereço do contrato: {}"
    
    ERROR_CONTRACT_COMPILE = "Erro ao compilar contrato: {}"
    ERROR_CONTRACT_COMPILE_UNEXPECTED = "Erro inesperado ao compilar contrato: {}"
    ERROR_CONTRACT_DEPLOY = "Erro ao implantar contrato: {}"
    ERROR_CONTRACT_DEPLOYMENT_FAILED = "Falha na implantação: {}"
    ERROR_CONTRACT_NETWORK = "Não foi possível conectar à rede Sepolia"
    ERROR_CONTRACT_DEPLOYER_CONFIG = "Endereço ou chave privada do deployer não configurados"

    # Adapters - Web3
    LOG_WEB3_CONNECTED = "Conectado à rede blockchain"
    LOG_WEB3_DISCONNECTED = "Desconectado da rede blockchain"
    LOG_WEB3_TRANSACTION = "Transação enviada: {}"
    LOG_WEB3_CONFIRMATION = "Transação confirmada: {}"
    LOG_WEB3_RESERVATION = "Reserva {} {}: estação {}, usuário {}, horário {}"
    LOG_WEB3_SESSION = "Sessão {} {}: estação {}, usuário {}, horário {}"
    LOG_WEB3_PAYMENT = "Pagamento {} {}: sessão {}, usuário {}, valor {}"
    
    ERROR_WEB3_CONNECT = "Erro ao conectar à rede blockchain: {}"
    ERROR_WEB3_DISCONNECT = "Erro ao desconectar da rede blockchain: {}"
    ERROR_WEB3_TRANSACTION = "Erro ao enviar transação: {}"
    ERROR_WEB3_CONFIRMATION = "Erro ao confirmar transação: {}"
    ERROR_WEB3_CONTRACT = "Erro ao interagir com contrato: {}"
    ERROR_WEB3_ADDRESS = "Endereço inválido: {}"
    ERROR_WEB3_BALANCE = "Saldo insuficiente: {}"
    ERROR_WEB3_GAS = "Erro ao estimar gas: {}"
    ERROR_WEB3_NONCE = "Erro ao obter nonce: {}"
    ERROR_WEB3_SIGN = "Erro ao assinar transação: {}"
    ERROR_WEB3_SEND = "Erro ao enviar transação: {}"
    ERROR_WEB3_RECEIPT = "Erro ao obter recibo da transação: {}"
    ERROR_WEB3_EVENT = "Erro ao processar evento: {}"
    ERROR_WEB3_CALL = "Erro ao chamar método do contrato: {}"

    # Adapters - Redis
    LOG_REDIS_CONNECTED = "Conectado ao Redis"
    LOG_REDIS_DISCONNECTED = "Desconectado do Redis"
    LOG_REDIS_OPERATION = "Operação Redis {}: {}"
    
    ERROR_REDIS_CONNECT = "Erro ao conectar ao Redis: {}"
    ERROR_REDIS_DISCONNECT = "Erro ao desconectar do Redis: {}"
    ERROR_REDIS_OPERATION = "Erro na operação Redis {}: {}"
    ERROR_REDIS_KEY = "Chave não encontrada: {}"
    ERROR_REDIS_VALUE = "Valor inválido: {}"
    ERROR_REDIS_EXPIRE = "Erro ao definir expiração: {}"
    ERROR_REDIS_DELETE = "Erro ao deletar chave: {}"
    ERROR_REDIS_CLEAR = "Erro ao limpar cache: {}"
    ERROR_REDIS_TTL = "Erro ao obter TTL: {}"
    ERROR_REDIS_TTL_FAILED = "Falha ao obter TTL do cache"
    ERROR_REDIS_INCREMENT = "Erro ao incrementar valor: {}"
    ERROR_REDIS_INCREMENT_FAILED = "Falha ao incrementar valor no cache"
    ERROR_REDIS_DECREMENT = "Erro ao decrementar valor: {}"
    ERROR_REDIS_DECREMENT_FAILED = "Falha ao decrementar valor no cache"

    # Adapters - SMTP
    LOG_SMTP_CONNECTED = "Conectado ao servidor SMTP"
    LOG_SMTP_DISCONNECTED = "Desconectado do servidor SMTP"
    LOG_SMTP_EMAIL = "Email enviado: {}"
    
    ERROR_SMTP_CONNECT = "Erro ao conectar ao servidor SMTP: {}"
    ERROR_SMTP_DISCONNECT = "Erro ao desconectar do servidor SMTP: {}"
    ERROR_SMTP_SEND = "Erro ao enviar email: {}"
    ERROR_SMTP_AUTH = "Erro de autenticação SMTP: {}"
    ERROR_SMTP_TEMPLATE = "Erro ao processar template de email: {}"
    ERROR_SMTP_ATTACHMENT = "Erro ao anexar arquivo: {}"
    ERROR_SMTP_TEMPLATE_SEND = "Erro ao enviar email com template: {}"
    ERROR_SMTP_TEMPLATE_SEND_FAILED = "Falha ao enviar email com template"
    ERROR_SMTP_BULK_SEND = "Erro ao enviar emails em lote: {}"
    ERROR_SMTP_BULK_SEND_FAILED = "Falha ao enviar emails em lote"

    # Adapters - Flask
    LOG_FLASK_REQUEST = "Requisição {} {}: {}"
    LOG_FLASK_RESPONSE = "Resposta {} {}: {}"
    LOG_FLASK_AUTH = "Autenticação {}: {}"
    
    ERROR_FLASK_REQUEST = "Erro na requisição {} {}: {}"
    ERROR_FLASK_RESPONSE = "Erro na resposta {} {}: {}"
    ERROR_FLASK_AUTH = "Erro de autenticação: {}"
    ERROR_FLASK_VALIDATION = "Erro de validação: {}"
    ERROR_FLASK_RATE_LIMIT = "Limite de requisições excedido: {}"
    ERROR_FLASK_CORS = "Erro de CORS: {}"
    ERROR_FLASK_JSON = "Erro ao processar JSON: {}"
    ERROR_FLASK_PARAMS = "Parâmetros inválidos: {}"
    ERROR_FLASK_HEADERS = "Headers inválidos: {}"
    ERROR_FLASK_COOKIES = "Cookies inválidos: {}"
    ERROR_FLASK_FILES = "Erro ao processar arquivos: {}"

    # Adapters - Firebase
    LOG_FIREBASE_INIT = "Firebase inicializado"
    LOG_FIREBASE_TOKEN = "Token Firebase gerado: {}"
    LOG_FIREBASE_NOTIFICATION = "Notificação enviada: {}"
    
    ERROR_FIREBASE_INIT = "Erro ao inicializar Firebase: {}"
    ERROR_FIREBASE_TOKEN = "Erro ao gerar token Firebase: {}"
    ERROR_FIREBASE_NOTIFICATION = "Erro ao enviar notificação: {}"
    ERROR_FIREBASE_TOPIC = "Erro ao gerenciar tópico: {}"
    ERROR_FIREBASE_DEVICE = "Erro ao gerenciar dispositivo: {}"
    ERROR_FIREBASE_MESSAGE = "Erro ao processar mensagem: {}"
    ERROR_FIREBASE_CONFIG = "Erro na configuração do Firebase: {}"
    ERROR_FIREBASE_AUTH = "Erro de autenticação Firebase: {}"

    ERROR_CACHE = "Erro de cache"
    ERROR_EMAIL_SEND_FAILED = "Erro ao enviar e-mail"
    ERROR_NOTIFICATION = "Erro de notificação"

    LOG_BLOCKCHAIN_CONNECTED = "Conectado à blockchain com sucesso"

    @classmethod
    def format(cls, message: str, *args) -> str:
        """
        Formata uma mensagem com argumentos.
        """
        return message.format(*args)

    @classmethod
    def get_error_message(cls, error_code: str) -> str:
        """
        Obtém uma mensagem de erro pelo código.
        """
        return getattr(cls, error_code, cls.ERROR_UNKNOWN)

    @classmethod
    def get_success_message(cls, success_code: str) -> str:
        """
        Obtém uma mensagem de sucesso pelo código.
        """
        return getattr(cls, success_code, cls.SUCCESS) 