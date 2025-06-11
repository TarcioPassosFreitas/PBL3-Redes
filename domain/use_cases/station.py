from adapters.database.models import StationORM
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from domain.exceptions.custom_exceptions import StationNotFoundError
from decimal import Decimal

class StationUseCase:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_station(self, station_id: int):
        result = await self.session.execute(select(StationORM).where(StationORM.id == station_id))
        station = result.scalars().first()
        if not station:
            raise StationNotFoundError(station_id)
        return {
            "id": station.id,
            "location": station.location,
            "power_output": str(station.power_output),
            "price_per_hour": str(station.price_per_hour),
            "is_available": station.is_available,
            "current_session_id": station.current_session_id,
            "reservations": station.reservations,
            "total_sessions": station.total_sessions,
            "total_revenue": str(station.total_revenue)
        }

    async def get_station_status(self, station_id: int):
        result = await self.session.execute(select(StationORM).where(StationORM.id == station_id))
        station = result.scalars().first()
        if not station:
            raise StationNotFoundError(station_id)
        return {
            "id": station.id,
            "is_available": station.is_available,
            "current_session_id": station.current_session_id
        }

    async def get_station_availability(self, station_id: int, start_date=None, end_date=None):
        result = await self.session.execute(select(StationORM).where(StationORM.id == station_id))
        station = result.scalars().first()
        if not station:
            raise StationNotFoundError(station_id)
        # Aqui você pode filtrar as reservas pelo período, se necessário
        return {
            "id": station.id,
            "reservations": station.reservations
        }

    async def get_station_stats(self, station_id: int, start_date=None, end_date=None):
        result = await self.session.execute(select(StationORM).where(StationORM.id == station_id))
        station = result.scalars().first()
        if not station:
            raise StationNotFoundError(station_id)
        # Aqui você pode adicionar lógica para calcular estatísticas reais
        return {
            "id": station.id,
            "total_sessions": station.total_sessions,
            "total_revenue": str(station.total_revenue)
        }

    def exemplo(self):
        return "Hello from StationUseCase" 