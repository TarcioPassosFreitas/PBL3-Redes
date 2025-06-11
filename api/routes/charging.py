from flask import Blueprint, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from adapters.http.flask_adapter import FlaskAdapter
from domain.use_cases.charge import ChargeUseCase
from shared.constants.texts import Texts
from shared.utils.logger import Logger

# Inicializa logger e blueprint
logger = Logger(__name__)
charging_bp = Blueprint("charging", __name__, url_prefix="/sessions")

# Configura rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize adapters
http_adapter = FlaskAdapter()

@charging_bp.route("", methods=["POST"])
@limiter.limit("10 per minute")
def start_session():
    """
    Inicia uma nova sessão de carregamento.
    
    ---
    tags:
      - Sessões
    summary: Inicia sessão de carregamento
    description: Inicia uma nova sessão de carregamento em uma estação específica
    security:
      - bearerAuth: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - station_id
          properties:
            station_id:
              type: integer
              description: ID da estação de carregamento
            reservation_id:
              type: integer
              description: ID da reserva (opcional)
    responses:
      201:
        description: Sessão iniciada com sucesso
      400:
        description: Dados inválidos
      401:
        description: Não autorizado
      404:
        description: Estação não encontrada
      409:
        description: Estação indisponível ou em uso
    """
    try:
        # Obtém dados da requisição
        data = request.get_json()
        adapter = FlaskAdapter(request)
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Inicia sessão
        session = charging_bp.charge_use_case.start_session(
            station_id=data["station_id"],
            user_address=adapter.get_user_address(),
            reservation_id=data.get("reservation_id")
        )
        
        # Registra evento
        logger.info(Texts.format(Texts.LOG_SESSION_EVENT, "start", {
            "session_id": session.id,
            "station_id": session.station_id,
            "user_address": session.user_address
        }))
        
        return adapter.create_response(session, 201)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_SESSION_START, str(e)))
        return adapter.handle_error(e)

@charging_bp.route("/<int:session_id>", methods=["PUT"])
@limiter.limit("10 per minute")
def end_session(session_id):
    """
    Finaliza uma sessão de carregamento.
    
    ---
    tags:
      - Sessões
    summary: Finaliza sessão de carregamento
    description: Finaliza uma sessão de carregamento ativa
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: session_id
        required: true
        type: integer
        description: ID da sessão
    responses:
      200:
        description: Sessão finalizada com sucesso
      401:
        description: Não autorizado
      403:
        description: Não autorizado a finalizar esta sessão
      404:
        description: Sessão não encontrada
    """
    try:
        adapter = FlaskAdapter(request)
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Finaliza sessão
        session = charging_bp.charge_use_case.end_session(
            session_id=session_id,
            user_address=adapter.get_user_address()
        )
        
        # Registra evento
        logger.info(Texts.format(Texts.LOG_SESSION_EVENT, "end", {
            "session_id": session.id,
            "station_id": session.station_id,
            "user_address": session.user_address
        }))
        
        return adapter.create_response(session)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_SESSION_END, str(e)))
        return adapter.handle_error(e)

@charging_bp.route("/<int:session_id>", methods=["GET"])
@limiter.limit("30 per minute")
def get_session(session_id):
    """
    Obtém detalhes de uma sessão específica.
    
    ---
    tags:
      - Sessões
    summary: Obtém detalhes da sessão
    description: Retorna os detalhes completos de uma sessão de carregamento
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: session_id
        required: true
        type: integer
        description: ID da sessão
    responses:
      200:
        description: Detalhes da sessão
      401:
        description: Não autorizado
      404:
        description: Sessão não encontrada
    """
    try:
        adapter = FlaskAdapter(request)
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Obtém sessão
        session = charging_bp.charge_use_case.get_session(
            session_id=session_id,
            user_address=adapter.get_user_address()
        )
        
        return adapter.create_response(session)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_SESSION_GET, str(e)))
        return adapter.handle_error(e)

@charging_bp.route("/user", methods=["GET"])
@limiter.limit("30 per minute")
def get_user_sessions():
    """
    Lista todas as sessões do usuário autenticado.
    
    ---
    tags:
      - Sessões
    summary: Lista sessões do usuário
    description: Retorna todas as sessões de carregamento do usuário autenticado
    security:
      - bearerAuth: []
    parameters:
      - in: query
        name: status
        type: string
        enum: [active, completed, cancelled]
        description: Filtra sessões por status
      - in: query
        name: start_date
        type: string
        format: date
        description: Filtra sessões a partir desta data
      - in: query
        name: end_date
        type: string
        format: date
        description: Filtra sessões até esta data
    responses:
      200:
        description: Lista de sessões do usuário
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
        
        # Lista sessões
        sessions = charging_bp.charge_use_case.get_user_sessions(
            user_address=adapter.get_user_address(),
            status=status,
            start_date=start_date,
            end_date=end_date
        )
        
        return adapter.create_response(sessions)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_SESSION_LIST_USER, str(e)))
        return adapter.handle_error(e)

@charging_bp.route("/station/<int:station_id>", methods=["GET"])
@limiter.limit("30 per minute")
def get_station_sessions():
    """
    Lista todas as sessões de uma estação específica.
    
    ---
    tags:
      - Sessões
    summary: Lista sessões da estação
    description: Retorna todas as sessões de carregamento de uma estação específica
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
        enum: [active, completed, cancelled]
        description: Filtra sessões por status
      - in: query
        name: start_date
        type: string
        format: date
        description: Filtra sessões a partir desta data
      - in: query
        name: end_date
        type: string
        format: date
        description: Filtra sessões até esta data
    responses:
      200:
        description: Lista de sessões da estação
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
        
        # Lista sessões
        sessions = charging_bp.charge_use_case.get_station_sessions(
            station_id=station_id,
            status=status,
            start_date=start_date,
            end_date=end_date
        )
        
        return adapter.create_response(sessions)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_SESSION_LIST_STATION, str(e)))
        return adapter.handle_error(e) 