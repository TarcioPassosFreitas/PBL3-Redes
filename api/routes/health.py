from fastapi import APIRouter
from fastapi.responses import JSONResponse
from shared.utils.logger import Logger
from shared.constants.config import Config
from datetime import datetime

# Inicializa logger e APIRouter
logger = Logger(__name__)
router = APIRouter()

@router.get("/health", tags=["Saúde"], summary="Verifica o status da API")
async def health():
    """
    Endpoint de verificação de saúde da API.
    
    ---
    tags:
      - Saúde
    summary: Verifica o status da API
    description: Retorna o status atual da API e suas dependências
    responses:
      200:
        description: API está funcionando normalmente
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
            version:
              type: string
              example: 1.0.0
            timestamp:
              type: string
              format: date-time
    """
    try:
        response = {
            "status": "ok",
            "version": Config.VERSION,
            "timestamp": datetime.utcnow().isoformat()
        }
        logger.info("Health check realizado com sucesso")
        return JSONResponse(content=response)
    except Exception as e:
        logger.error(f"Erro ao realizar health check: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Erro ao verificar status da API"
            }
        ) 