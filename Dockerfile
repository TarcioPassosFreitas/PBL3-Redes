# Usa Python 3.11 slim como base
FROM python:3.11-slim

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    nodejs \
    npm \
    wget \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Instala solc (compilador Solidity)
RUN wget https://github.com/ethereum/solidity/releases/download/v0.8.20/solc-static-linux \
    && chmod +x solc-static-linux \
    && mv solc-static-linux /usr/local/bin/solc

# Cria e configura diretório da aplicação
WORKDIR /app

# Copia arquivos de dependências
COPY requirements.txt requirements-dev.txt ./

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Cria diretório para build do contrato
RUN mkdir -p contracts/build

# Compila o contrato
RUN solc --abi --bin contracts/EVCharging.sol -o contracts/build --overwrite

# Cria diretórios necessários e ajusta permissões
RUN mkdir -p /app/logs && \
    chmod 777 /app/logs

# Configura usuário não-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expõe porta da API
EXPOSE 5000

# Torna o script de inicialização executável
RUN chmod +x scripts/init-db.sh

# Comando para iniciar a aplicação
CMD bash -c './scripts/init-db.sh && uvicorn app:app --host 0.0.0.0 --port 5000' 