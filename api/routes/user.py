from fastapi import APIRouter, Request, status, Depends
from fastapi.responses import JSONResponse
from shared.utils.logger import Logger
from shared.constants.texts import Texts
from shared.constants.config import Config
from adapters.http.flask_adapter import FlaskAdapter
from adapters.blockchain.web3_adapter import Web3Adapter
from decimal import Decimal

# Inicializa logger e blueprint
logger = Logger(__name__)
router = APIRouter()

http_adapter = FlaskAdapter()

@router.get("/", tags=["Usuários"], summary="Lista todos os usuários")
async def list_users():
    try:
        blockchain = Web3Adapter()
        # Supondo que há um método para listar todos os usuários na blockchain
        users = blockchain.contract.functions.getAllUsers().call()
        def serialize_user(user):
            return {
                "wallet_address": user[0],
                "total_sessions": user[1],
                "total_energy": str(user[2]) if isinstance(user[2], Decimal) else user[2],
                "total_spent": str(user[3]) if isinstance(user[3], Decimal) else user[3],
                "last_session_id": user[4]
            }
        data = [serialize_user(u) for u in users]
        return JSONResponse(content={"success": True, "data": data})
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {str(e)}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@router.get("/<int:user_id>", tags=["Usuários"], summary="Obtém um usuário pelo ID")
async def get_user(user_id: int):
    user = user_use_case.get_user(user_id)
    if not user:
        return JSONResponse(status_code=404, content={"error": "Usuário não encontrado"})
    return JSONResponse(content=user)

@router.post("/", tags=["Usuários"], summary="Cria um novo usuário")
async def create_user(data: dict):
    user = user_use_case.create_user(data)
    return JSONResponse(content=user, status_code=201)

@router.put("/<int:user_id>", tags=["Usuários"], summary="Atualiza um usuário pelo ID")
async def update_user(user_id: int, data: dict):
    user = user_use_case.update_user(user_id, data)
    if not user:
        return JSONResponse(status_code=404, content={"error": "Usuário não encontrado"})
    return JSONResponse(content=user)

@router.delete("/<int:user_id>", tags=["Usuários"], summary="Deleta um usuário pelo ID")
async def delete_user(user_id: int):
    user_use_case.delete_user(user_id)
    return JSONResponse(content={"deleted": True})

@router.get("/profile", tags=["Usuários"], summary="Obtém o perfil do usuário autenticado")
async def get_user_profile(request: Request):
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

@router.get("/balance", tags=["Usuários"], summary="Obtém o saldo ETH do usuário autenticado")
async def get_user_balance(request: Request):
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

@router.get("/stats", tags=["Usuários"], summary="Obtém estatísticas do usuário autenticado")
async def get_user_stats(request: Request):
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
        start_date = adapter.parse_date(request.query.get("start_date"))
        end_date = adapter.parse_date(request.query.get("end_date"))
        
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

@router.get("/history", tags=["Usuários"], summary="Obtém o histórico completo do usuário autenticado")
async def get_user_history(request: Request):
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
        include_sessions = request.query.get("include_sessions", "true").lower() == "true"
        include_payments = request.query.get("include_payments", "true").lower() == "true"
        include_reservations = request.query.get("include_reservations", "true").lower() == "true"
        start_date = adapter.parse_date(request.query.get("start_date"))
        end_date = adapter.parse_date(request.query.get("end_date"))
        
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

@router.get("/preferences", tags=["Usuários"], summary="Obtém as preferências do usuário autenticado")
async def get_user_preferences(request: Request):
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

@router.put("/preferences", tags=["Usuários"], summary="Atualiza as preferências do usuário autenticado")
async def update_user_preferences(request: Request):
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
        data = await request.json()
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