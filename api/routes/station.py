from fastapi import APIRouter, Request, status, Depends
from fastapi.responses import JSONResponse
from shared.utils.logger import Logger
from shared.constants.texts import Texts
from shared.constants.config import Config
from decimal import Decimal

from adapters.http.flask_adapter import FlaskAdapter
from adapters.database.models import StationORM
from sqlalchemy.ext.asyncio import AsyncSession
from adapters.database.session import get_async_session

# Inicializa logger e blueprint
logger = Logger(__name__)
router = APIRouter()

http_adapter = FlaskAdapter()

@router.get("/", tags=["Estações"], summary="Lista todas as estações")
async def list_stations(session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(
            StationORM.__table__.select()
        )
        def serialize_station(row):
            d = dict(row)
            for key, value in d.items():
                if isinstance(value, Decimal):
                    d[key] = str(value)
            return d
        data = [serialize_station(row) for row in result.mappings().all()]
        return JSONResponse(content={"success": True, "data": data})
    except Exception as e:
        logger.error(f"Erro ao listar estações: {str(e)}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/{station_id}", tags=["Estações"], summary="Obtém detalhes da estação")
async def get_station(station_id: int):
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
        adapter = FlaskAdapter(Request())
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Obtém estação
        use_case = StationUseCase()
        station = use_case.get_station(station_id)
        
        return adapter.create_response(station)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_STATION_GET, str(e)))
        return adapter.handle_error(e)

@router.get("/{station_id}/status", tags=["Estações"], summary="Obtém status da estação")
async def get_station_status(station_id: int):
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
        adapter = FlaskAdapter(Request())
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Obtém status
        use_case = StationUseCase()
        status = use_case.get_station_status(station_id)
        
        return adapter.create_response(status)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_STATION_STATUS, str(e)))
        return adapter.handle_error(e)

@router.get("/{station_id}/availability", tags=["Estações"], summary="Obtém disponibilidade da estação")
async def get_station_availability(station_id: int):
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
        adapter = FlaskAdapter(Request())
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Obtém parâmetros de filtro
        start_date = adapter.parse_date(Request().query.get("start_date"))
        end_date = adapter.parse_date(Request().query.get("end_date"))
        
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

@router.get("/{station_id}/stats", tags=["Estações"], summary="Obtém estatísticas da estação")
async def get_station_stats(station_id: int):
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
        adapter = FlaskAdapter(Request())
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Obtém parâmetros de filtro
        start_date = adapter.parse_date(Request().query.get("start_date"))
        end_date = adapter.parse_date(Request().query.get("end_date"))
        
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