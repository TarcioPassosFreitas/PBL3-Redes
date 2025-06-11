from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from shared.constants.config import Config
from shared.constants.texts import Texts
from shared.utils.logger import Logger
import uvicorn

# Inicializa o logger
logger = Logger(__name__)

app = FastAPI(
    title="API do Sistema de Carregamento de Veículos Elétricos",
    description="API para gerenciamento de estações de carregamento de veículos elétricos, sessões, reservas e pagamentos em blockchain.",
    version=Config.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Middleware de logging
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.log_request(
            method=request.method,
            endpoint=request.url.path,
            status=0,
            duration=0.0
        )
        response = await call_next(request)
        logger.info(f"Resposta: {response.status_code}")
        return response

app.add_middleware(LoggingMiddleware)

# Handlers de erro
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "error": str(exc)}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.error(f"Erro interno: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "error": Texts.ERROR_INTERNAL}
    )

# Importa e registra os routers (rotas)
from api.routes.health import router as health_router
from api.routes.reservation import router as reservation_router
from api.routes.charging import router as charging_router
from api.routes.payment import router as payment_router
from api.routes.station import router as station_router
from api.routes.user import router as user_router

app.include_router(health_router, prefix=f"{Config.API_PREFIX}")
app.include_router(reservation_router, prefix=f"{Config.API_PREFIX}/reservations")
app.include_router(charging_router, prefix=f"{Config.API_PREFIX}/sessions")
app.include_router(payment_router, prefix=f"{Config.API_PREFIX}/payments")
app.include_router(station_router, prefix=f"{Config.API_PREFIX}/stations")
app.include_router(user_router, prefix=f"{Config.API_PREFIX}/users")

if __name__ == "__main__":
    uvicorn.run("app:app", host=Config.HOST, port=Config.PORT, reload=True) 