import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from shared.constants.config import Config
from adapters.database.models import Base, UserORM, StationORM
from datetime import datetime
from decimal import Decimal
from sqlalchemy import text

DATABASE_URL = Config.DB_URL.replace('postgresql://', 'postgresql+asyncpg://')
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        # Apaga dados antigos
        await session.execute(text('DELETE FROM users'))
        await session.execute(text('DELETE FROM stations'))
        await session.commit()

        # Usuários de exemplo
        users = [
            UserORM(
                wallet_address=f"0x{str(i).zfill(40)}",
                email=f"user{i}@example.com",
                name=f"Usuário {i}",
                created_at=datetime.utcnow(),
                last_login=None,
                active_sessions=[],
                total_charges=Decimal('0.0'),
                total_sessions=0,
                active_reservations=[]
            ) for i in range(1, 101)
        ]
        # Estações de exemplo
        stations = [
            StationORM(
                location=f"Endereço {i}, Cidade Exemplo",
                power_output=Decimal(str(10 + (i % 20))),
                price_per_hour=Decimal('0.01') + Decimal(str(i)) * Decimal('0.0001'),
                is_available=True,
                current_session_id=None,
                reservations={},
                total_sessions=0,
                total_revenue=Decimal('0.0')
            ) for i in range(1, 101)
        ]
        session.add_all(users + stations)
        await session.commit()
        print("Usuários e estações inseridos com sucesso!")

if __name__ == "__main__":
    asyncio.run(seed()) 