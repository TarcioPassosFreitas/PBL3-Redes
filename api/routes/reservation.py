from flask import Blueprint, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from adapters.http.flask_adapter import FlaskAdapter
from domain.use_cases.reserve import ReserveUseCase
from shared.constants.texts import Texts
from shared.utils.logger import Logger

# Inicializa logger e blueprint
logger = Logger(__name__)
reservation_bp = Blueprint("reservation", __name__, url_prefix="/reservations")

# Configura rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize adapters and use cases
http_adapter = FlaskAdapter()
reserve_use_case = None  # Será inicializado no app.py

@reservation_bp.route("", methods=["POST"])
@limiter.limit("10 per minute")
def create_reservation():
    """
    Cria uma nova reserva de estação de carregamento.
    
    ---
    tags:
      - Reservas
    summary: Cria uma nova reserva
    description: Cria uma nova reserva para uma estação de carregamento em um horário específico
    security:
      - bearerAuth: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - station_id
            - start_time
            - duration
          properties:
            station_id:
              type: integer
              description: ID da estação de carregamento
            start_time:
              type: string
              format: date-time
              description: Data e hora de início da reserva
            duration:
              type: integer
              description: Duração da reserva em minutos
    responses:
      201:
        description: Reserva criada com sucesso
      400:
        description: Dados inválidos
      401:
        description: Não autorizado
      404:
        description: Estação não encontrada
      409:
        description: Estação indisponível no horário solicitado
    """
    try:
        # Obtém dados da requisição
        data = request.get_json()
        adapter = http_adapter
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Cria reserva
        use_case = reserve_use_case
        reservation = use_case.create_reservation(
            station_id=data["station_id"],
            user_address=adapter.get_user_address(),
            start_time=adapter.parse_datetime(data["start_time"]),
            duration=data["duration"]
        )
        
        # Registra evento
        logger.info(Texts.format(Texts.LOG_RESERVATION_EVENT, "create", {
            "reservation_id": reservation.id,
            "station_id": reservation.station_id,
            "user_address": reservation.user_address
        }))
        
        return adapter.create_response(reservation, 201)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_RESERVATION_CREATE, str(e)))
        return adapter.handle_error(e)

@reservation_bp.route("/<int:reservation_id>", methods=["DELETE"])
@limiter.limit("10 per minute")
def cancel_reservation(reservation_id):
    """
    Cancela uma reserva existente.
    
    ---
    tags:
      - Reservas
    summary: Cancela uma reserva
    description: Cancela uma reserva de estação de carregamento existente
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: reservation_id
        required: true
        type: integer
        description: ID da reserva a ser cancelada
    responses:
      200:
        description: Reserva cancelada com sucesso
      401:
        description: Não autorizado
      403:
        description: Não autorizado a cancelar esta reserva
      404:
        description: Reserva não encontrada
    """
    try:
        adapter = http_adapter
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Cancela reserva
        use_case = reserve_use_case
        reservation = use_case.cancel_reservation(
            reservation_id=reservation_id,
            user_address=adapter.get_user_address()
        )
        
        # Registra evento
        logger.info(Texts.format(Texts.LOG_RESERVATION_EVENT, "cancel", {
            "reservation_id": reservation.id,
            "station_id": reservation.station_id,
            "user_address": reservation.user_address
        }))
        
        return adapter.create_response(reservation)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_RESERVATION_CANCEL, str(e)))
        return adapter.handle_error(e)

@reservation_bp.route("/<int:reservation_id>", methods=["GET"])
@limiter.limit("30 per minute")
def get_reservation(reservation_id):
    """
    Obtém detalhes de uma reserva específica.
    
    ---
    tags:
      - Reservas
    summary: Obtém detalhes da reserva
    description: Retorna os detalhes completos de uma reserva específica
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: reservation_id
        required: true
        type: integer
        description: ID da reserva
    responses:
      200:
        description: Detalhes da reserva
      401:
        description: Não autorizado
      404:
        description: Reserva não encontrada
    """
    try:
        adapter = http_adapter
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Obtém reserva
        use_case = reserve_use_case
        reservation = use_case.get_reservation(
            reservation_id=reservation_id,
            user_address=adapter.get_user_address()
        )
        
        return adapter.create_response(reservation)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_RESERVATION_GET, str(e)))
        return adapter.handle_error(e)

@reservation_bp.route("/user", methods=["GET"])
@limiter.limit("30 per minute")
def get_user_reservations():
    """
    Lista todas as reservas do usuário autenticado.
    
    ---
    tags:
      - Reservas
    summary: Lista reservas do usuário
    description: Retorna todas as reservas do usuário autenticado
    security:
      - bearerAuth: []
    parameters:
      - in: query
        name: status
        type: string
        enum: [pending, active, completed, cancelled]
        description: Filtra reservas por status
      - in: query
        name: start_date
        type: string
        format: date
        description: Filtra reservas a partir desta data
      - in: query
        name: end_date
        type: string
        format: date
        description: Filtra reservas até esta data
    responses:
      200:
        description: Lista de reservas do usuário
      401:
        description: Não autorizado
    """
    try:
        adapter = http_adapter
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Obtém parâmetros de filtro
        status = request.args.get("status")
        start_date = adapter.parse_date(request.args.get("start_date"))
        end_date = adapter.parse_date(request.args.get("end_date"))
        
        # Lista reservas
        use_case = reserve_use_case
        reservations = use_case.get_user_reservations(
            user_address=adapter.get_user_address(),
            status=status,
            start_date=start_date,
            end_date=end_date
        )
        
        return adapter.create_response(reservations)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_RESERVATION_LIST_USER, str(e)))
        logger.error(f"Erro ao listar reservas do usuário: {str(e)}")
        return adapter.handle_error(e) 