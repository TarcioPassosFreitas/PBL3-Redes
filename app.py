import os
from flask import Flask, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from flasgger import Swagger

from adapters.blockchain.web3_adapter import Web3Adapter
from adapters.http.flask_adapter import FlaskAdapter
from domain.use_cases.reserve import ReserveUseCase
from domain.use_cases.charge import ChargeUseCase
from domain.use_cases.pay import PaymentUseCase
from shared.constants.config import Config
from shared.constants.texts import Texts
from shared.utils.logger import Logger

# Inicializa o logger
logger = Logger(__name__)

def create_app() -> Flask:
    """
    Cria e configura a aplicação Flask.
    """
    # Cria a aplicação Flask
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Registra o endpoint de health imediatamente
    from api.routes.health import health_bp
    app.register_blueprint(health_bp)

    # Configuração do Swagger
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "API do Sistema de Carregamento de Veículos Elétricos",
            "description": "API para gerenciamento de estações de carregamento de veículos elétricos, sessões, reservas e pagamentos em blockchain.",
            "version": "1.0.0"
        },
        "basePath": "/api/v1",
        "schemes": ["http", "https"],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Cabeçalho de autorização JWT usando o esquema Bearer. Exemplo: 'Authorization: Bearer {token}'"
            }
        }
    }
    Swagger(app, template=swagger_template)

    # Carrega a configuração
    app.config.from_object(Config)

    # Inicializa o CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": Config.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Inicializa o limitador de taxa
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=[Config.RATE_LIMIT_DEFAULT] if Config.RATE_LIMIT_ENABLED else None,
        storage_uri=Config.RATE_LIMIT_STORAGE_URL
    )

    # Inicializa os adaptadores
    blockchain_adapter = Web3Adapter()
    http_adapter = FlaskAdapter()

    # Inicializa os casos de uso
    reserve_use_case = ReserveUseCase(blockchain_adapter, http_adapter)
    charge_use_case = ChargeUseCase(blockchain_adapter, http_adapter)
    payment_use_case = PaymentUseCase(blockchain_adapter, http_adapter)

    # Registra os blueprints
    from api.routes.reservation import reservation_bp, http_adapter as reservation_http_adapter
    from api.routes.charging import charging_bp
    from api.routes.payment import payment_bp
    from api.routes.station import station_bp
    from api.routes.user import user_bp

    # Configura os casos de uso nos blueprints
    charging_bp.charge_use_case = charge_use_case
    reservation_bp.reserve_use_case = reserve_use_case
    reservation_bp.http_adapter = reservation_http_adapter
    payment_bp.payment_use_case = payment_use_case

    app.register_blueprint(reservation_bp, url_prefix=f"{Config.API_PREFIX}/reservations")
    app.register_blueprint(charging_bp, url_prefix=f"{Config.API_PREFIX}/sessions")
    app.register_blueprint(payment_bp, url_prefix=f"{Config.API_PREFIX}/payments")
    app.register_blueprint(station_bp, url_prefix=f"{Config.API_PREFIX}/stations")
    app.register_blueprint(user_bp, url_prefix=f"{Config.API_PREFIX}/users")

    # Registra os manipuladores de erro
    @app.errorhandler(400)
    def bad_request(error):
        return http_adapter.create_error_response(str(error), 400)

    @app.errorhandler(401)
    def unauthorized(error):
        return http_adapter.create_error_response(Texts.UNAUTHORIZED, 401)

    @app.errorhandler(403)
    def forbidden(error):
        return http_adapter.create_error_response(Texts.FORBIDDEN, 403)

    @app.errorhandler(404)
    def not_found(error):
        return http_adapter.create_error_response(Texts.NOT_FOUND, 404)

    @app.errorhandler(429)
    def too_many_requests(error):
        return http_adapter.create_error_response(Texts.API_RATE_LIMITED, 429)

    @app.errorhandler(500)
    def internal_server_error(error):
        return http_adapter.create_error_response(Texts.ERROR_INTERNAL, 500)

    # Registra os manipuladores de requisição
    @app.before_request
    def before_request():
        """
        Registra as requisições recebidas.
        """
        logger.log_request(
            method=request.method,
            path=request.path,
            query_params=dict(request.args),
            headers=dict(request.headers),
            body=request.get_json(silent=True)
        )

    # Registra os manipuladores de resposta
    @app.after_request
    def after_request(response):
        """
        Registra as respostas enviadas.
        """
        logger.info(f"Resposta: {response.status} - {response.get_data(as_text=True)}")
        return response

    return app

def main():
    """
    Ponto de entrada principal da aplicação.
    """
    app = create_app()
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )

app = create_app()

if __name__ == "__main__":
    main() 