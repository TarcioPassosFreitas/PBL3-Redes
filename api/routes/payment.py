from fastapi import APIRouter, Request, status, Depends
from fastapi.responses import JSONResponse
from shared.utils.logger import Logger
from shared.constants.texts import Texts
from shared.constants.config import Config

from adapters.http.flask_adapter import FlaskAdapter
from domain.use_cases.pay import PaymentUseCase
from adapters.blockchain.web3_adapter import Web3Adapter
from decimal import Decimal

# Inicializa logger e blueprint
logger = Logger(__name__)
router = APIRouter()

# Initialize adapters and use cases
http_adapter = FlaskAdapter()
payment_use_case = None  # Will be initialized in app.py

@router.post("/", tags=["Pagamentos"], summary="Processa um novo pagamento")
async def process_payment(request: Request):
    """
    Processa um novo pagamento.
    
    ---
    tags:
      - Pagamentos
    summary: Processa pagamento
    description: Processa um novo pagamento para uma sessão de carregamento
    security:
      - bearerAuth: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - session_id
            - amount
          properties:
            session_id:
              type: integer
              description: ID da sessão de carregamento
            amount:
              type: string
              description: Valor do pagamento em ETH
    responses:
      201:
        description: Pagamento processado com sucesso
      400:
        description: Dados inválidos
      401:
        description: Não autorizado
      404:
        description: Sessão não encontrada
      409:
        description: Pagamento já realizado
    """
    try:
        # Obtém dados da requisição
        data = await request.json()
        adapter = FlaskAdapter(request)
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Processa pagamento
        use_case = PaymentUseCase()
        payment = use_case.process_payment(
            session_id=data["session_id"],
            user_address=adapter.get_user_address(),
            amount=adapter.parse_decimal(data["amount"])
        )
        
        # Registra evento
        logger.info(Texts.format(Texts.LOG_PAYMENT_EVENT, "process", {
            "payment_id": payment.id,
            "session_id": payment.session_id,
            "user_address": payment.user_address
        }))
        
        return adapter.create_response(payment, 201)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_PAYMENT_PROCESS, str(e)))
        return adapter.handle_error(e)

@router.get("/{payment_id}", tags=["Pagamentos"], summary="Obtém detalhes de um pagamento específico")
async def get_payment_details(payment_id: int, request: Request):
    """
    Obtém detalhes de um pagamento específico.
    
    ---
    tags:
      - Pagamentos
    summary: Obtém detalhes do pagamento
    description: Retorna os detalhes completos de um pagamento específico
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: payment_id
        required: true
        type: integer
        description: ID do pagamento
    responses:
      200:
        description: Detalhes do pagamento
      401:
        description: Não autorizado
      404:
        description: Pagamento não encontrado
    """
    try:
        adapter = FlaskAdapter(request)
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Obtém pagamento
        use_case = PaymentUseCase()
        payment = use_case.get_payment(
            payment_id=payment_id,
            user_address=adapter.get_user_address()
        )
        
        return adapter.create_response(payment)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_PAYMENT_GET, str(e)))
        return adapter.handle_error(e)

@router.get("/user", tags=["Pagamentos"], summary="Lista todos os pagamentos do usuário autenticado")
async def get_user_payments(request: Request):
    """
    Lista todos os pagamentos do usuário autenticado.
    
    ---
    tags:
      - Pagamentos
    summary: Lista pagamentos do usuário
    description: Retorna todos os pagamentos do usuário autenticado
    security:
      - bearerAuth: []
    parameters:
      - in: query
        name: status
        type: string
        enum: [pending, completed, failed]
        description: Filtra pagamentos por status
      - in: query
        name: start_date
        type: string
        format: date
        description: Filtra pagamentos a partir desta data
      - in: query
        name: end_date
        type: string
        format: date
        description: Filtra pagamentos até esta data
    responses:
      200:
        description: Lista de pagamentos do usuário
      401:
        description: Não autorizado
    """
    try:
        adapter = FlaskAdapter(request)
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Obtém parâmetros de filtro
        status = request.query_params.get("status")
        start_date = adapter.parse_date(request.query_params.get("start_date"))
        end_date = adapter.parse_date(request.query_params.get("end_date"))
        
        # Lista pagamentos
        use_case = PaymentUseCase()
        payments = use_case.get_user_payments(
            user_address=adapter.get_user_address(),
            status=status,
            start_date=start_date,
            end_date=end_date
        )
        
        return adapter.create_response(payments)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_PAYMENT_LIST_USER, str(e)))
        return adapter.handle_error(e)

@router.get("/station/{station_id}", tags=["Pagamentos"], summary="Lista todos os pagamentos de uma estação específica")
async def get_station_payments(station_id: int, request: Request):
    """
    Lista todos os pagamentos de uma estação específica.
    
    ---
    tags:
      - Pagamentos
    summary: Lista pagamentos da estação
    description: Retorna todos os pagamentos realizados em uma estação específica
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: station_id
        required: true
        type: integer
        description: ID da estação
      - in: query
        name: status
        type: string
        enum: [pending, completed, failed]
        description: Filtra pagamentos por status
      - in: query
        name: start_date
        type: string
        format: date
        description: Filtra pagamentos a partir desta data
      - in: query
        name: end_date
        type: string
        format: date
        description: Filtra pagamentos até esta data
    responses:
      200:
        description: Lista de pagamentos da estação
      401:
        description: Não autorizado
      404:
        description: Estação não encontrada
    """
    try:
        adapter = FlaskAdapter(request)
        
        # Valida autenticação
        adapter.authenticate_request()
        
        # Obtém parâmetros de filtro
        status = request.query_params.get("status")
        start_date = adapter.parse_date(request.query_params.get("start_date"))
        end_date = adapter.parse_date(request.query_params.get("end_date"))
        
        # Lista pagamentos
        use_case = PaymentUseCase()
        payments = use_case.get_station_payments(
            station_id=station_id,
            status=status,
            start_date=start_date,
            end_date=end_date
        )
        
        return adapter.create_response(payments)
        
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_PAYMENT_LIST_STATION, str(e)))
        return adapter.handle_error(e)

@router.get("/", tags=["Pagamentos"], summary="Lista todos os pagamentos")
async def list_payments():
    try:
        blockchain = Web3Adapter()
        # Supondo que há um método para listar todos os pagamentos na blockchain
        payments = blockchain.contract.functions.getAllPayments().call()
        def serialize_payment(pay):
            return {
                "payment_id": pay[0],
                "session_id": pay[1],
                "user_address": pay[2],
                "amount": str(pay[3]) if isinstance(pay[3], Decimal) else pay[3],
                "timestamp": str(pay[4]),
                "status": pay[5]
            }
        data = [serialize_payment(p) for p in payments]
        return JSONResponse(content={"success": True, "data": data})
    except Exception as e:
        logger.error(f"Erro ao listar pagamentos: {str(e)}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)}) 