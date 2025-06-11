from flask import Blueprint, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from adapters.http.flask_adapter import FlaskAdapter
from domain.use_cases.pay import PaymentUseCase
from shared.constants.texts import Texts
from shared.utils.logger import Logger

# Inicializa logger e blueprint
logger = Logger(__name__)
payment_bp = Blueprint("payment", __name__, url_prefix="/payments")

# Configura rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize adapters and use cases
http_adapter = FlaskAdapter()
payment_use_case = None  # Will be initialized in app.py

@payment_bp.route("", methods=["POST"])
@limiter.limit("10 per minute")
def process_payment():
    """
    Processa um novo pagamento.
    
    ---
    tags:
      - Pagamentos
    summary: Processa pagamento
    description: Processa um novo pagamento para uma sessão de carregamento
    security:
      - bearerAuth: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - session_id
            - amount
          properties:
            session_id:
              type: integer
              description: ID da sessão de carregamento
            amount:
              type: string
              description: Valor do pagamento em ETH
    responses:
      201:
        description: Pagamento processado com sucesso
      400:
        description: Dados inválidos
      401:
        description: Não autorizado
      404:
        description: Sessão não encontrada
      409:
        description: Pagamento já realizado
    """
    try:
        # Obtém dados da requisição
        data = request.get_json()
        adapter = FlaskAdapter(request)
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Processa pagamento
        use_case = PaymentUseCase()
        payment = use_case.process_payment(
            session_id=data["session_id"],
            user_address=adapter.get_user_address(),
            amount=adapter.parse_decimal(data["amount"])
        )
        
        # Registra evento
        logger.info(Texts.format(Texts.LOG_PAYMENT_EVENT, "process", {
            "payment_id": payment.id,
            "session_id": payment.session_id,
            "user_address": payment.user_address
        }))
        
        return adapter.create_response(payment, 201)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_PAYMENT_PROCESS, str(e)))
        return adapter.handle_error(e)

@payment_bp.route("/<int:payment_id>", methods=["GET"])
@limiter.limit("30 per minute")
def get_payment_details(payment_id):
    """
    Obtém detalhes de um pagamento específico.
    
    ---
    tags:
      - Pagamentos
    summary: Obtém detalhes do pagamento
    description: Retorna os detalhes completos de um pagamento específico
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: payment_id
        required: true
        type: integer
        description: ID do pagamento
    responses:
      200:
        description: Detalhes do pagamento
      401:
        description: Não autorizado
      404:
        description: Pagamento não encontrado
    """
    try:
        adapter = FlaskAdapter(request)
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Obtém pagamento
        use_case = PaymentUseCase()
        payment = use_case.get_payment(
            payment_id=payment_id,
            user_address=adapter.get_user_address()
        )
        
        return adapter.create_response(payment)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_PAYMENT_GET, str(e)))
        return adapter.handle_error(e)

@payment_bp.route("/user", methods=["GET"])
@limiter.limit("30 per minute")
def get_user_payments():
    """
    Lista todos os pagamentos do usuário autenticado.
    
    ---
    tags:
      - Pagamentos
    summary: Lista pagamentos do usuário
    description: Retorna todos os pagamentos do usuário autenticado
    security:
      - bearerAuth: []
    parameters:
      - in: query
        name: status
        type: string
        enum: [pending, completed, failed]
        description: Filtra pagamentos por status
      - in: query
        name: start_date
        type: string
        format: date
        description: Filtra pagamentos a partir desta data
      - in: query
        name: end_date
        type: string
        format: date
        description: Filtra pagamentos até esta data
    responses:
      200:
        description: Lista de pagamentos do usuário
      401:
        description: Não autorizado
    """
    try:
        adapter = FlaskAdapter(request)
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Obtém parâmetros de filtro
        status = request.args.get("status")
        start_date = adapter.parse_date(request.args.get("start_date"))
        end_date = adapter.parse_date(request.args.get("end_date"))
        
        # Lista pagamentos
        use_case = PaymentUseCase()
        payments = use_case.get_user_payments(
            user_address=adapter.get_user_address(),
            status=status,
            start_date=start_date,
            end_date=end_date
        )
        
        return adapter.create_response(payments)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_PAYMENT_LIST_USER, str(e)))
        return adapter.handle_error(e)

@payment_bp.route("/station/<int:station_id>", methods=["GET"])
@limiter.limit("30 per minute")
def get_station_payments():
    """
    Lista todos os pagamentos de uma estação específica.
    
    ---
    tags:
      - Pagamentos
    summary: Lista pagamentos da estação
    description: Retorna todos os pagamentos realizados em uma estação específica
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: station_id
        required: true
        type: integer
        description: ID da estação
      - in: query
        name: status
        type: string
        enum: [pending, completed, failed]
        description: Filtra pagamentos por status
      - in: query
        name: start_date
        type: string
        format: date
        description: Filtra pagamentos a partir desta data
      - in: query
        name: end_date
        type: string
        format: date
        description: Filtra pagamentos até esta data
    responses:
      200:
        description: Lista de pagamentos da estação
      401:
        description: Não autorizado
      404:
        description: Estação não encontrada
    """
    try:
        adapter = FlaskAdapter(request)
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Obtém parâmetros de filtro
        station_id = request.view_args["station_id"]
        status = request.args.get("status")
        start_date = adapter.parse_date(request.args.get("start_date"))
        end_date = adapter.parse_date(request.args.get("end_date"))
        
        # Lista pagamentos
        use_case = PaymentUseCase()
        payments = use_case.get_station_payments(
            station_id=station_id,
            status=status,
            start_date=start_date,
            end_date=end_date
        )
        
        return adapter.create_response(payments)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_PAYMENT_LIST_STATION, str(e)))
        return adapter.handle_error(e) 