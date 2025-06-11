# EV Charging - Sistema de Carregamento de Veículos Elétricos

Sistema descentralizado para gerenciamento de estações de carregamento de veículos elétricos, utilizando blockchain para garantir transparência, segurança e auditabilidade das transações.

## 📋 Índice

- [Arquitetura](#arquitetura)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Configuração](#configuração)
- [Instalação](#instalação)
- [Uso](#uso)
- [Desenvolvimento](#desenvolvimento)
- [Testes](#testes)
- [Segurança](#segurança)
- [Deployment](#deployment)

## 🏗️ Arquitetura

O sistema é construído seguindo os princípios de arquitetura hexagonal (ports and adapters) e utiliza blockchain como fonte da verdade para todas as transações.

### 1. Camada de Domínio (Core)

#### Entidades (`domain/entities/`)
- `station.py`: Representa uma estação de carregamento
  ```python
  class Station:
      id: int
      location: str
      status: str
      current_session: Optional[int]
      reserved_until: Optional[datetime]
      reserved_by: Optional[str]
  ```
- `session.py`: Representa uma sessão de carregamento
  ```python
  class Session:
      id: int
      station_id: int
      user_address: str
      start_time: datetime
      end_time: Optional[datetime]
      status: str
      amount: Decimal
      paid: bool
  ```
- `user.py`: Representa um usuário do sistema
  ```python
  class User:
      address: str
      name: str
      email: str
      created_at: datetime
  ```

#### Casos de Uso (`domain/use_cases/`)
- `charge.py`: Gerencia sessões de carregamento
- `reserve.py`: Gerencia reservas de estações
- `pay.py`: Gerencia pagamentos
- `station.py`: Gerencia estações

#### Portas (`domain/ports/`)
- `blockchain_port.py`: Interface para interação com blockchain
- `cache_port.py`: Interface para cache
- `database_port.py`: Interface para banco de dados
- `notification_port.py`: Interface para notificações

### 2. Camada de Adaptadores

#### Blockchain (`adapters/blockchain/`)
- `web3_adapter.py`: Implementa interação com Ethereum/Ganache
  - Conexão com blockchain
  - Compilação e deploy de contratos
  - Transações e eventos
  - Consultas ao contrato

#### Cache (`adapters/cache/`)
- `redis_adapter.py`: Implementa cache com Redis
  - Rate limiting
  - Cache de sessão
  - Cache de dados frequentes

#### Database (`adapters/database/`)
- `sqlalchemy_adapter.py`: Implementa persistência com PostgreSQL
  - Cache de dados
  - Índices para consultas
  - Relacionamentos

#### HTTP (`adapters/http/`)
- `flask_adapter.py`: Implementa API REST
  - Rotas e endpoints
  - Validação de dados
  - Respostas HTTP

#### Auth (`adapters/auth/`)
- `jwt_adapter.py`: Implementa autenticação
  - Geração de tokens
  - Validação de tokens
  - Middleware de autenticação

### 3. API REST (`api/routes/`)

#### Endpoints
- `/stations`: Gerenciamento de estações
- `/sessions`: Gerenciamento de sessões
- `/reservations`: Gerenciamento de reservas
- `/payments`: Gerenciamento de pagamentos
- `/users`: Gerenciamento de usuários

### 4. Smart Contract (`contracts/`)

#### EVCharging.sol
```solidity
contract EVCharging {
    // Estruturas
    struct Station { ... }
    struct Session { ... }
    struct User { ... }

    // Mapeamentos
    mapping(uint => Station) public stations;
    mapping(uint => Session) public sessions;
    mapping(address => User) public users;

    // Eventos
    event StationCreated(uint stationId, string location);
    event SessionStarted(uint sessionId, uint stationId, address user);
    event SessionEnded(uint sessionId, uint amount);
    event PaymentProcessed(uint sessionId, uint amount);
    event ReservationCreated(uint stationId, address user, uint startTime);
    event ReservationCancelled(uint stationId);

    // Funções
    function createStation(string memory location) public returns (uint) { ... }
    function startSession(uint stationId) public returns (uint) { ... }
    function endSession(uint sessionId) public { ... }
    function paySession(uint sessionId) public payable { ... }
    function reserveStation(uint stationId, uint startTime) public { ... }
    function cancelReservation(uint stationId) public { ... }
}
```

## ⚙️ Configuração

### 1. Variáveis de Ambiente (.env)

Crie um arquivo `.env` na raiz do projeto:

```env
# API
API_DEBUG=false
API_SECRET_KEY=your_secure_secret_key  # Gerar com: openssl rand -hex 32
API_JWT_SECRET=your_secure_jwt_secret  # Gerar com: openssl rand -hex 32
API_HOST=0.0.0.0
API_PORT=5000

# Blockchain (Ganache)
WEB3_PROVIDER=ganache
WEB3_PROVIDER_URL=http://ganache:8545
WEB3_CONTRACT_ADDRESS=  # Preenchido automaticamente após deploy

# Database (PostgreSQL)
DB_HOST=postgres
DB_PORT=5432
DB_NAME=evcharging
DB_USER=evcharging
DB_PASSWORD=your_secure_password  # Gerar com: openssl rand -base64 32

# Cache (Redis)
REDIS_URL=redis://redis:6379/0

# Logging
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=*  # Em produção, especificar domínios permitidos
```

### 2. Geração de Chaves

#### API Secret Key e JWT Secret
```bash
# No terminal
openssl rand -hex 32
```

#### Database Password
```bash
# No terminal
openssl rand -base64 32
```

### 3. Carteiras Ethereum

Para desenvolvimento, o Ganache cria 10 carteiras automaticamente. Para produção:

1. Instale MetaMask
2. Crie uma nova carteira
3. Obtenha ETH de teste (Goerli, Sepolia)
4. Exporte a chave privada (seguro apenas para desenvolvimento)

## 🚀 Instalação

### 1. Pré-requisitos

- Docker e Docker Compose
- Git
- Node.js e npm (para desenvolvimento)
- MetaMask (para interação com blockchain)

### 2. Clone e Configuração

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/ev-charging.git
cd ev-charging

# Crie e configure o .env
cp .env.example .env
# Edite o .env com suas configurações

# Inicie os serviços
docker-compose up -d

# Verifique o status
docker-compose ps

# Monitore os logs
docker-compose logs -f
```

### 3. Inicialização do Sistema

O sistema é inicializado automaticamente pelo Docker Compose:

1. **Ganache**: Blockchain local
   - Porta: 8545
   - 10 carteiras com 1000 ETH cada
   - Hardfork: Shanghai

2. **Redis**: Cache e Rate Limiting
   - Porta: 6379
   - Persistência ativada
   - Sem senha (apenas rede interna)

3. **PostgreSQL**: Cache/Índice
   - Porta: 5432
   - Banco: evcharging
   - Usuário: evcharging
   - Senha: definida no .env

4. **API Flask**: Backend
   - Porta: 5000
   - 4 workers
   - Timeout: 120s
   - Swagger UI: /docs

### 4. Deploy do Contrato

O contrato é compilado durante o build da imagem e implantado automaticamente:

```bash
# Verifique o status do deploy
docker-compose logs api | grep "Contract deployed"

# Endereço do contrato
docker-compose exec api python -c "import json; print(json.load(open('contracts/build/EVCharging.json'))['address'])"
```

## 💻 Uso

### 1. API REST

A API está disponível em `http://localhost:5000` com documentação Swagger em `/docs`.

#### Exemplos de Uso

1. **Criar Estação**
```bash
curl -X POST http://localhost:5000/api/v1/stations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"location": "Av. Paulista, 1000"}'
```

2. **Iniciar Sessão**
```bash
curl -X POST http://localhost:5000/api/v1/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"station_id": 1}'
```

3. **Processar Pagamento**
```bash
curl -X POST http://localhost:5000/api/v1/sessions/1/payment \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": "0.1"}'
```

### 2. Smart Contract

#### Funções Principais

1. **Criar Estação**
```solidity
function createStation(string memory location) public returns (uint)
```

2. **Iniciar Sessão**
```solidity
function startSession(uint stationId) public returns (uint)
```

3. **Finalizar Sessão**
```solidity
function endSession(uint sessionId) public
```

4. **Processar Pagamento**
```solidity
function paySession(uint sessionId) public payable
```

5. **Reservar Estação**
```solidity
function reserveStation(uint stationId, uint startTime) public
```

6. **Cancelar Reserva**
```solidity
function cancelReservation(uint stationId) public
```

## 🛠️ Desenvolvimento

### 1. Estrutura de Diretórios

```
ev-charging/
├── adapters/           # Implementações dos adaptadores
│   ├── blockchain/     # Adaptador Web3
│   ├── cache/         # Adaptador Redis
│   ├── database/      # Adaptador PostgreSQL
│   ├── http/          # Adaptador Flask
│   └── auth/          # Adaptador JWT
├── api/               # Rotas da API
│   └── routes/        # Endpoints
├── contracts/         # Smart Contracts
│   ├── build/         # Contratos compilados
│   └── EVCharging.sol # Contrato principal
├── domain/            # Lógica de negócio
│   ├── entities/      # Entidades
│   ├── ports/         # Interfaces
│   └── use_cases/     # Casos de uso
├── shared/            # Código compartilhado
│   ├── constants/     # Constantes
│   └── utils/         # Utilitários
├── scripts/           # Scripts utilitários
├── tests/             # Testes
├── .env              # Variáveis de ambiente
├── .env.example      # Exemplo de .env
├── docker-compose.yml # Configuração Docker
├── Dockerfile        # Build da API
└── requirements.txt  # Dependências Python
```

### 2. Comandos Úteis

```bash
# Iniciar serviços
docker-compose up -d

# Parar serviços
docker-compose down

# Reconstruir API
docker-compose build api

# Logs da API
docker-compose logs -f api

# Shell na API
docker-compose exec api bash

# Testes
docker-compose exec api pytest

# Migrações
docker-compose exec api alembic upgrade head
```

## 🧪 Testes

### 1. Testes Unitários

```bash
# Executar todos os testes
docker-compose exec api pytest

# Testes com cobertura
docker-compose exec api pytest --cov

# Testes específicos
docker-compose exec api pytest tests/unit/test_charge.py
```

### 2. Testes de Integração

```bash
# Executar testes de integração
docker-compose exec api pytest tests/integration

# Testes do contrato
docker-compose exec api pytest tests/contract
```

## 🔒 Segurança

### 1. Autenticação

- JWT para autenticação de usuários
- Tokens com expiração de 1 hora
- Refresh tokens (opcional)
- Rate limiting por IP

### 2. Blockchain

- Assinatura de transações
- Verificação de saldo
- Eventos para auditoria
- Funções de emergência

### 3. Dados

- PostgreSQL com SSL
- Redis sem acesso externo
- Variáveis de ambiente para segredos
- Logs sem dados sensíveis

## 🚀 Deployment

### 1. Produção

1. **Preparação**
   - Configure variáveis de ambiente
   - Gere chaves seguras
   - Prepare nós Ethereum

2. **Deploy**
   ```bash
   # Build e push das imagens
   docker-compose build
   docker-compose push

   # Deploy em produção
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Monitoramento**
   - Logs: `docker-compose logs -f`
   - Saúde: `docker-compose ps`
   - Métricas: Prometheus/Grafana

### 2. Backup

1. **PostgreSQL**
   ```bash
   docker-compose exec postgres pg_dump -U evcharging > backup.sql
   ```

2. **Redis**
   ```bash
   docker-compose exec redis redis-cli SAVE
   ```

3. **Blockchain**
   - Mantenha backup das chaves privadas
   - Monitore eventos do contrato
   - Mantenha nós de backup

## 📝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.
