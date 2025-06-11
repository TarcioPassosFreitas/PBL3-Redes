from fastapi import APIRouter, Request, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from shared.utils.logger import Logger
from shared.constants.texts import Texts
from shared.constants.config import Config
from decimal import Decimal

from adapters.database.models import StationORM
from sqlalchemy.ext.asyncio import AsyncSession
from adapters.database.session import get_async_session

# Inicializa logger e blueprint
logger = Logger(__name__)
router = APIRouter()

# Função utilitária para serializar uma estação
def serialize_station(station):
    if isinstance(station, dict):
        d = dict(station)
    else:
        d = station.__dict__ if hasattr(station, "__dict__") else dict(station)
    for key, value in d.items():
        if isinstance(value, Decimal):
            d[key] = str(value)
    d.pop("_sa_instance_state", None)
    return d

@router.get("/", tags=["Estações"], summary="Lista todas as estações")
async def list_stations(session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(StationORM.__table__.select())
        data = [serialize_station(row) for row in result.mappings().all()]
        return JSONResponse(content={"success": True, "data": data})
    except Exception as e:
        logger.error(f"Erro ao listar estações: {str(e)}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/{station_id}", tags=["Estações"], summary="Obtém detalhes da estação")
async def get_station(station_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(StationORM.__table__.select().where(StationORM.id == station_id))
        row = result.mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="Estação não encontrada")
        return JSONResponse(content={"success": True, "data": serialize_station(row)})
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Erro ao obter estação: {str(e)}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/{station_id}/status", tags=["Estações"], summary="Obtém status da estação")
async def get_station_status(station_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(StationORM.__table__.select().where(StationORM.id == station_id))
        row = result.mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="Estação não encontrada")
        # Exemplo: status pode ser apenas o campo is_available
        status_data = {"id": row["id"], "is_available": row["is_available"]}
        return JSONResponse(content={"success": True, "data": status_data})
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Erro ao obter status da estação: {str(e)}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/{station_id}/availability", tags=["Estações"], summary="Obtém disponibilidade da estação")
async def get_station_availability(station_id: int, request: Request, session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(StationORM.__table__.select().where(StationORM.id == station_id))
        row = result.mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="Estação não encontrada")
        # Exemplo: disponibilidade pode ser baseada em reservas (campo reservations)
        availability = row.get("reservations", "{}")
        return JSONResponse(content={"success": True, "data": {"id": row["id"], "availability": availability}})
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Erro ao obter disponibilidade da estação: {str(e)}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/{station_id}/stats", tags=["Estações"], summary="Obtém estatísticas da estação")
async def get_station_stats(station_id: int, request: Request, session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(StationORM.__table__.select().where(StationORM.id == station_id))
        row = result.mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="Estação não encontrada")
        # Exemplo: estatísticas podem ser total_sessions e total_revenue
        stats = {
            "id": row["id"],
            "total_sessions": row.get("total_sessions", 0),
            "total_revenue": str(row.get("total_revenue", "0.0")),
        }
        return JSONResponse(content={"success": True, "data": stats})
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas da estação: {str(e)}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)}) 