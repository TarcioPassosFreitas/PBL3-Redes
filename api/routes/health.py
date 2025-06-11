from flask import Blueprint, jsonify
from shared.utils.logger import Logger

# Inicializa logger e blueprint
logger = Logger(__name__)
health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health():
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
        from datetime import datetime
        from shared.constants.config import Config
        
        response = {
            "status": "ok",
            "version": Config.VERSION,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info("Health check realizado com sucesso")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Erro ao realizar health check: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Erro ao verificar status da API"
        }), 500 