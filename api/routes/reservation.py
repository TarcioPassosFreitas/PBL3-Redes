from fastapi import APIRouter, Request, status, Depends
from fastapi.responses import JSONResponse
from shared.utils.logger import Logger
from shared.constants.texts import Texts
from shared.constants.config import Config

from adapters.http.flask_adapter import FlaskAdapter
from domain.use_cases.reserve import ReserveUseCase
from adapters.blockchain.web3_adapter import Web3Adapter
from decimal import Decimal

# Inicializa logger e blueprint
logger = Logger(__name__)
router = APIRouter()

# Initialize adapters and use cases
http_adapter = FlaskAdapter()
reserve_use_case = None  # Será inicializado no app.py

@router.get("/", tags=["Reservas"], summary="Lista todas as reservas")
async def list_reservations():
    try:
        blockchain = Web3Adapter()
        # Supondo que há um método para listar todas as reservas na blockchain
        reservations = blockchain.contract.functions.getAllReservations().call()
        def serialize_reservation(res):
            return {
                "reservation_id": res[0],
                "station_id": res[1],
                "user_address": res[2],
                "start_time": str(res[3]),
                "end_time": str(res[4]),
                "status": res[5]
            }
        data = [serialize_reservation(r) for r in reservations]
        return JSONResponse(content={"success": True, "data": data})
    except Exception as e:
        logger.error(f"Erro ao listar reservas: {str(e)}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.post("", tags=["Reservas"], summary="Cria uma nova reserva", status_code=status.HTTP_201_CREATED)
async def create_reservation(request: Request):
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
        data = await request.json()
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

@router.delete("/{reservation_id}", tags=["Reservas"], summary="Cancela uma reserva", status_code=status.HTTP_200_OK)
async def cancel_reservation(reservation_id: int):
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

@router.get("/{reservation_id}", tags=["Reservas"], summary="Obtém detalhes da reserva", status_code=status.HTTP_200_OK)
async def get_reservation(reservation_id: int):
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

@router.get("/user", tags=["Reservas"], summary="Lista reservas do usuário", status_code=status.HTTP_200_OK)
async def get_user_reservations(request: Request):
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
        status = request.query_params.get("status")
        start_date = adapter.parse_date(request.query_params.get("start_date"))
        end_date = adapter.parse_date(request.query_params.get("end_date"))
        
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