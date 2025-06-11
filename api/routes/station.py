from flask import Blueprint, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from adapters.http.flask_adapter import FlaskAdapter
from domain.use_cases.station import StationUseCase
from shared.constants.texts import Texts
from shared.utils.logger import Logger

# Inicializa logger e blueprint
logger = Logger(__name__)
station_bp = Blueprint("station", __name__, url_prefix="/stations")

# Configura rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@station_bp.route("", methods=["GET"])
@limiter.limit("30 per minute")
def get_stations():
    """
    Lista todas as estações de carregamento.
    
    ---
    tags:
      - Estações
    summary: Lista estações
    description: Retorna todas as estações de carregamento disponíveis
    security:
      - bearerAuth: []
    parameters:
      - in: query
        name: status
        type: string
        enum: [available, busy, offline, maintenance]
        description: Filtra estações por status
      - in: query
        name: location
        type: string
        description: Filtra estações por localização (cidade, bairro, etc)
    responses:
      200:
        description: Lista de estações
      401:
        description: Não autorizado
    """
    try:
        adapter = FlaskAdapter(request)
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Obtém parâmetros de filtro
        status = request.args.get("status")
        location = request.args.get("location")
        
        # Lista estações
        use_case = StationUseCase()
        stations = use_case.get_stations(
            status=status,
            location=location
        )
        
        return adapter.create_response(stations)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_STATION_LIST, str(e)))
        return adapter.handle_error(e)

@station_bp.route("/<int:station_id>", methods=["GET"])
@limiter.limit("30 per minute")
def get_station(station_id):
    """
    Obtém detalhes de uma estação específica.
    
    ---
    tags:
      - Estações
    summary: Obtém detalhes da estação
    description: Retorna os detalhes completos de uma estação de carregamento
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: station_id
        required: true
        type: integer
        description: ID da estação
    responses:
      200:
        description: Detalhes da estação
      401:
        description: Não autorizado
      404:
        description: Estação não encontrada
    """
    try:
        adapter = FlaskAdapter(request)
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Obtém estação
        use_case = StationUseCase()
        station = use_case.get_station(station_id)
        
        return adapter.create_response(station)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_STATION_GET, str(e)))
        return adapter.handle_error(e)

@station_bp.route("/<int:station_id>/status", methods=["GET"])
@limiter.limit("30 per minute")
def get_station_status(station_id):
    """
    Obtém o status atual de uma estação.
    
    ---
    tags:
      - Estações
    summary: Obtém status da estação
    description: Retorna o status atual de uma estação de carregamento
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: station_id
        required: true
        type: integer
        description: ID da estação
    responses:
      200:
        description: Status da estação
      401:
        description: Não autorizado
      404:
        description: Estação não encontrada
    """
    try:
        adapter = FlaskAdapter(request)
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Obtém status
        use_case = StationUseCase()
        status = use_case.get_station_status(station_id)
        
        return adapter.create_response(status)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_STATION_STATUS, str(e)))
        return adapter.handle_error(e)

@station_bp.route("/<int:station_id>/availability", methods=["GET"])
@limiter.limit("30 per minute")
def get_station_availability(station_id):
    """
    Obtém a disponibilidade de uma estação.
    
    ---
    tags:
      - Estações
    summary: Obtém disponibilidade da estação
    description: Retorna o calendário de disponibilidade de uma estação
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: station_id
        required: true
        type: integer
        description: ID da estação
      - in: query
        name: start_date
        type: string
        format: date
        description: Data inicial do período
      - in: query
        name: end_date
        type: string
        format: date
        description: Data final do período
    responses:
      200:
        description: Disponibilidade da estação
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
        start_date = adapter.parse_date(request.args.get("start_date"))
        end_date = adapter.parse_date(request.args.get("end_date"))
        
        # Obtém disponibilidade
        use_case = StationUseCase()
        availability = use_case.get_station_availability(
            station_id=station_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return adapter.create_response(availability)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_STATION_AVAILABILITY, str(e)))
        return adapter.handle_error(e)

@station_bp.route("/<int:station_id>/stats", methods=["GET"])
@limiter.limit("30 per minute")
def get_station_stats(station_id):
    """
    Obtém estatísticas de uma estação.
    
    ---
    tags:
      - Estações
    summary: Obtém estatísticas da estação
    description: Retorna estatísticas de uso de uma estação
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: station_id
        required: true
        type: integer
        description: ID da estação
      - in: query
        name: start_date
        type: string
        format: date
        description: Data inicial do período
      - in: query
        name: end_date
        type: string
        format: date
        description: Data final do período
    responses:
      200:
        description: Estatísticas da estação
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
        start_date = adapter.parse_date(request.args.get("start_date"))
        end_date = adapter.parse_date(request.args.get("end_date"))
        
        # Obtém estatísticas
        use_case = StationUseCase()
        stats = use_case.get_station_stats(
            station_id=station_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return adapter.create_response(stats)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_STATION_STATS, str(e)))
        return adapter.handle_error(e) 