from flask import Blueprint, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from adapters.http.flask_adapter import FlaskAdapter
from domain.use_cases.user import UserUseCase
from shared.constants.texts import Texts
from shared.utils.logger import Logger
from infra.repositories.user_repository import UserRepository
from sqlalchemy.orm import scoped_session, sessionmaker
from shared.constants.config import Config
from adapters.database.sqlalchemy_adapter import SQLAlchemyAdapter
from domain.entities.user import User
from sqlalchemy import create_engine

# Inicializa logger e blueprint
logger = Logger(__name__)
user_bp = Blueprint("user", __name__, url_prefix="/users")

# Configura rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Setup SQLAlchemy session
engine = create_engine(Config.DB_URL)
Session = scoped_session(sessionmaker(bind=engine))
user_repository = UserRepository(Session())
user_use_case = UserUseCase(user_repository)

@user_bp.route("/", methods=["GET"])
def list_users():
    users = user_use_case.list_users()
    return jsonify(users)

@user_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = user_use_case.get_user(user_id)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    return jsonify(user)

@user_bp.route("/", methods=["POST"])
def create_user():
    data = request.get_json()
    user = user_use_case.create_user(data)
    return jsonify(user), 201

@user_bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    user = user_use_case.update_user(user_id, data)
    if not user:
        return jsonify({"error": "Usuário não encontrado"}), 404
    return jsonify(user)

@user_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user_use_case.delete_user(user_id)
    return jsonify({"deleted": True})

@user_bp.route("", methods=["GET"])
@limiter.limit("30 per minute")
def get_user_profile():
    """
    Obtém o perfil do usuário autenticado.
    
    ---
    tags:
      - Usuário
    summary: Obtém perfil do usuário
    description: Retorna os detalhes do perfil do usuário autenticado
    security:
      - bearerAuth: []
    responses:
      200:
        description: Perfil do usuário
      401:
        description: Não autorizado
    """
    try:
        adapter = FlaskAdapter(request)
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Obtém perfil
        use_case = UserUseCase()
        profile = use_case.get_user_profile(
            user_address=adapter.get_user_address()
        )
        
        return adapter.create_response(profile)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_USER_PROFILE, str(e)))
        return adapter.handle_error(e)

@user_bp.route("/balance", methods=["GET"])
@limiter.limit("30 per minute")
def get_user_balance():
    """
    Obtém o saldo ETH do usuário autenticado.
    
    ---
    tags:
      - Usuário
    summary: Obtém saldo do usuário
    description: Retorna o saldo em ETH da carteira do usuário autenticado
    security:
      - bearerAuth: []
    responses:
      200:
        description: Saldo do usuário
      401:
        description: Não autorizado
    """
    try:
        adapter = FlaskAdapter(request)
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Obtém saldo
        use_case = UserUseCase()
        balance = use_case.get_user_balance(
            user_address=adapter.get_user_address()
        )
        
        return adapter.create_response(balance)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_USER_BALANCE, str(e)))
        return adapter.handle_error(e)

@user_bp.route("/stats", methods=["GET"])
@limiter.limit("30 per minute")
def get_user_stats():
    """
    Obtém estatísticas do usuário autenticado.
    
    ---
    tags:
      - Usuário
    summary: Obtém estatísticas do usuário
    description: Retorna estatísticas de uso do usuário autenticado
    security:
      - bearerAuth: []
    parameters:
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
        description: Estatísticas do usuário
      401:
        description: Não autorizado
    """
    try:
        adapter = FlaskAdapter(request)
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Obtém parâmetros de filtro
        start_date = adapter.parse_date(request.args.get("start_date"))
        end_date = adapter.parse_date(request.args.get("end_date"))
        
        # Obtém estatísticas
        use_case = UserUseCase()
        stats = use_case.get_user_stats(
            user_address=adapter.get_user_address(),
            start_date=start_date,
            end_date=end_date
        )
        
        return adapter.create_response(stats)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_USER_STATS, str(e)))
        return adapter.handle_error(e)

@user_bp.route("/history", methods=["GET"])
@limiter.limit("30 per minute")
def get_user_history():
    """
    Obtém o histórico completo do usuário autenticado.
    
    ---
    tags:
      - Usuário
    summary: Obtém histórico do usuário
    description: Retorna o histórico completo de uso do usuário autenticado
    security:
      - bearerAuth: []
    parameters:
      - in: query
        name: include_sessions
        type: boolean
        description: Inclui sessões de carregamento
      - in: query
        name: include_payments
        type: boolean
        description: Inclui pagamentos
      - in: query
        name: include_reservations
        type: boolean
        description: Inclui reservas
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
        description: Histórico do usuário
      401:
        description: Não autorizado
    """
    try:
        adapter = FlaskAdapter(request)
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Obtém parâmetros de filtro
        include_sessions = request.args.get("include_sessions", "true").lower() == "true"
        include_payments = request.args.get("include_payments", "true").lower() == "true"
        include_reservations = request.args.get("include_reservations", "true").lower() == "true"
        start_date = adapter.parse_date(request.args.get("start_date"))
        end_date = adapter.parse_date(request.args.get("end_date"))
        
        # Obtém histórico
        use_case = UserUseCase()
        history = use_case.get_user_history(
            user_address=adapter.get_user_address(),
            include_sessions=include_sessions,
            include_payments=include_payments,
            include_reservations=include_reservations,
            start_date=start_date,
            end_date=end_date
        )
        
        return adapter.create_response(history)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_USER_HISTORY, str(e)))
        return adapter.handle_error(e)

@user_bp.route("/preferences", methods=["GET"])
@limiter.limit("30 per minute")
def get_user_preferences():
    """
    Obtém as preferências do usuário autenticado.
    
    ---
    tags:
      - Usuário
    summary: Obtém preferências do usuário
    description: Retorna as preferências de uso do usuário autenticado
    security:
      - bearerAuth: []
    responses:
      200:
        description: Preferências do usuário
      401:
        description: Não autorizado
    """
    try:
        adapter = FlaskAdapter(request)
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Obtém preferências
        use_case = UserUseCase()
        preferences = use_case.get_user_preferences(
            user_address=adapter.get_user_address()
        )
        
        return adapter.create_response(preferences)
        
    except Exception as e:
        logger.error(f"Erro ao obter preferências do usuário: {str(e)}")
        return adapter.handle_error(e)

@user_bp.route("/preferences", methods=["PUT"])
@limiter.limit("10 per minute")
def update_user_preferences():
    """
    Atualiza as preferências do usuário autenticado.
    
    ---
    tags:
      - Usuário
    summary: Atualiza preferências do usuário
    description: Atualiza as preferências de uso do usuário autenticado
    security:
      - bearerAuth: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            preferred_stations:
              type: array
              items:
                type: integer
              description: IDs das estações preferidas
            notification_settings:
              type: object
              properties:
                email:
                  type: boolean
                  description: Receber notificações por email
                push:
                  type: boolean
                  description: Receber notificações push
                sms:
                  type: boolean
                  description: Receber notificações por SMS
            language:
              type: string
              enum: [pt-BR, en-US]
              description: Idioma preferido
            timezone:
              type: string
              description: Fuso horário preferido
    responses:
      200:
        description: Preferências atualizadas com sucesso
      400:
        description: Dados inválidos
      401:
        description: Não autorizado
    """
    try:
        # Obtém dados da requisição
        data = request.get_json()
        adapter = FlaskAdapter(request)
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Atualiza preferências
        use_case = UserUseCase()
        preferences = use_case.update_user_preferences(
            user_address=adapter.get_user_address(),
            preferences=data
        )
        
        return adapter.create_response(preferences)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_USER_PREFERENCES, str(e)))
        return adapter.handle_error(e) 