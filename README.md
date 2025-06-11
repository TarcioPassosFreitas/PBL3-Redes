# Sistema de Gerenciamento de Estações de Recarga de Veículos Elétricos (VEs) com Blockchain

## Objetivo

Este projeto implementa um sistema para gerenciamento de estações de recarga de veículos elétricos (VEs), garantindo **transparência, segurança, descentralização e auditabilidade** em todas as transações de reserva, recarga e pagamento, utilizando blockchain (Ganache/Ethereum), FastAPI, PostgreSQL e Redis.

---

## Contexto e Motivação

Com o aumento do uso de VEs no Brasil, surgem desafios como fraudes, disputas por pontos de recarga, falta de integração entre empresas e necessidade de transparência para usuários e empresas. O sistema resolve esses problemas utilizando **blockchain** como livro razão distribuído, registrando todas as operações críticas e promovendo confiança entre todos os envolvidos.

---

## Como Funciona a Blockchain no Projeto

- Todas as transações críticas (reservas, sessões de recarga, pagamentos) são **registradas e consultadas na blockchain**.
- Isso garante que nenhuma empresa ou usuário pode manipular dados em benefício próprio.
- Auditoria e transparência: qualquer parte pode verificar o histórico de transações.
- Descentralização: não há um servidor central controlando tudo, mas sim um registro público e imutável.

---

## Endpoints Disponíveis

### Usuários
- `GET /api/v1/users/` — Lista todos os usuários (blockchain)
- `POST /api/v1/users/` — Cria novo usuário (blockchain)
- `GET /api/v1/users/{user_id}` — Detalhes do usuário

### Estações
- `GET /api/v1/stations/` — Lista todas as estações (banco, 100 já pré-cadastradas)
- `GET /api/v1/stations/{station_id}` — Detalhes da estação
- `GET /api/v1/stations/{station_id}/status` — Status da estação
- `GET /api/v1/stations/{station_id}/availability` — Disponibilidade da estação

### Reservas
- `GET /api/v1/reservation/` — Lista todas as reservas (blockchain)
- `POST /api/v1/reservation/` — Cria nova reserva (blockchain)
- `DELETE /api/v1/reservation/{reservation_id}` — Cancela reserva (blockchain)
- `GET /api/v1/reservation/user` — Lista reservas do usuário autenticado

### Sessões de Recarga
- `GET /api/v1/charging/` — Lista todas as sessões (blockchain)
- `POST /api/v1/charging/` — Inicia sessão de recarga
- `PUT /api/v1/charging/{session_id}` — Finaliza sessão
- `GET /api/v1/charging/user` — Lista sessões do usuário autenticado

### Pagamentos
- `GET /api/v1/payment/` — Lista todos os pagamentos (blockchain)
- `POST /api/v1/payment/` — Processa novo pagamento
- `GET /api/v1/payment/user` — Lista pagamentos do usuário autenticado

### Outros
- `GET /api/v1/health` — Healthcheck da API
- `GET /docs` — Documentação Swagger interativa

---

## Como Executar o Projeto

1. **Clone o repositório:**
   ```bash
   git clone <repo-url>
   cd <repo>
   ```
2. **Configure o arquivo `.env`** (veja modelo abaixo ou use `.env.example`).
3. **Suba os serviços:**
   ```bash
   docker-compose down -v
   docker-compose up --build
   ```
4. **Acesse a documentação:**
   - [http://localhost:5000/docs](http://localhost:5000/docs)

---

## Testes e Dados de Exemplo

- O sistema já vem com **100 usuários** e **100 estações** pré-cadastradas para facilitar os testes.
- Use o Swagger para testar todos os fluxos: reservas, sessões, pagamentos, etc.
- Todas as operações críticas são registradas na blockchain (Ganache).

---

## Exemplo de .env

```ini
#########################
# ⚡ FastAPI
#########################
API_ENV=development
API_DEBUG=1
SECRET_KEY=40f8ca558c6b376a8ae5793c0f9105c47cd843ea5618c3f075595f18a17309f1

#########################
# ⚙️ Blockchain (Ganache)
#########################
WEB3_PROVIDER=ganache
WEB3_NETWORK=development
WEB3_PROVIDER_URL=http://ganache:8545
WEB3_CONTRACT_ADDRESS=0xaaFE6747B0dD988D016Aba9cd31Bf427Bafd4207
WEB3_GAS_LIMIT=3000000
WEB3_TIMEOUT=120

#########################
# 🧠 Redis
#########################
REDIS_URL=redis://redis:6379/0

#########################
# 🛢️ PostgreSQL
#########################
DB_HOST=postgres
DB_PORT=5432
DB_NAME=evcharging
DB_USER=evcharging
DB_PASSWORD=Tqp35ktFlHnfLhJgA21k2JkKEaPXmExrbMXKxTeWzl0=

#########################
# 🔑 JWT
#########################
JWT_SECRET=iyPtaowd2dSjjxHIjAmEOX1WofRbsceRywXtGw-f6oFqlFmXkbnHv-2iBE8Mx5rgHJ6a16yPknVcIoMxU7qpUQ
JWT_ALGORITHM=HS256
JWT_EXP_DELTA_SECONDS=3600

#########################
# 📧 E-mail (opcional)
#########################
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=t.passos.2017.2@gmail.com
SMTP_PASSWORD=jodp jznk lpmm aqgc
EMAIL_FROM=t.passos.2017.2@gmail.com

#########################
# 📄 Logging
#########################
LOG_LEVEL=INFO
```

---

## Alinhamento com o PBL

- **Transparência, segurança e auditabilidade:** Blockchain registra todas as transações críticas.
- **Descentralização:** Não há ponto único de falha, múltiplas empresas podem operar sem confiar umas nas outras.
- **Frameworks de terceiros:** FastAPI, SQLAlchemy, Web3.py, Ganache, PostgreSQL, Redis.
- **Pronto para demonstração:** Dados de teste já inseridos, endpoints documentados, fácil de rodar e testar.
- **Código comentado e modular:** Facilita manutenção e entendimento.

---

## Regras e Entrega

- O sistema deve ser apresentado no laboratório de Redes e Sistemas Distribuídos.
- O código fonte está comentado e pronto para entrega.
- O relatório pode ser baseado neste README, complementando com diagramas e prints dos testes.
- Prazo final: **10/06/2025**.

---

## Dúvidas?
Entre em contato com o time de desenvolvimento ou consulte a documentação Swagger para exemplos de uso dos endpoints.
