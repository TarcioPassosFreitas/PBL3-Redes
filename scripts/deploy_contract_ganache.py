#!/usr/bin/env python3
"""
Script para compilar e implantar o contrato EVCharging.sol no Ganache local.
Este script deve ser executado após o Ganache estar rodando.
"""

import json
import os
import time
from pathlib import Path
from web3 import Web3
from eth_account import Account
from shared.constants.texts import Texts
from shared.utils.logger import Logger

logger = Logger(__name__)

def compile_contract():
    """Compila o contrato EVCharging.sol usando solc."""
    try:
        # Verifica se o solc está instalado
        if os.system("solc --version") != 0:
            raise Exception("solc não está instalado. Por favor, instale o solc.")

        # Compila o contrato
        contract_path = Path("contracts/EVCharging.sol")
        if not contract_path.exists():
            raise Exception(f"Contrato não encontrado em {contract_path}")

        # Cria diretório de build se não existir
        build_dir = Path("contracts/build")
        build_dir.mkdir(exist_ok=True)

        # Compila o contrato
        os.system(f"solc --abi --bin --overwrite -o {build_dir} {contract_path}")

        # Lê o ABI e bytecode
        with open(build_dir / "EVCharging.abi", "r") as f:
            abi = json.load(f)
        with open(build_dir / "EVCharging.bin", "r") as f:
            bytecode = f.read().strip()

        return abi, bytecode

    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_CONTRACT_COMPILE, str(e)))
        raise

def deploy_contract():
    """Implanta o contrato no Ganache."""
    try:
        # Conecta ao Ganache
        w3 = Web3(Web3.HTTPProvider("http://ganache:8545"))
        if not w3.is_connected():
            raise Exception("Não foi possível conectar ao Ganache")

        # Compila o contrato
        abi, bytecode = compile_contract()

        # Usa a primeira conta do Ganache como deployer
        accounts = w3.eth.accounts
        if not accounts:
            raise Exception("Nenhuma conta encontrada no Ganache")
        
        deployer = accounts[0]
        logger.info(f"Usando conta {deployer} para deploy")

        # Cria instância do contrato
        contract = w3.eth.contract(abi=abi, bytecode=bytecode)

        # Prepara transação
        tx = contract.constructor().build_transaction({
            "from": deployer,
            "nonce": w3.eth.get_transaction_count(deployer),
            "gas": 3000000,
            "gasPrice": w3.eth.gas_price
        })

        # Envia transação
        tx_hash = w3.eth.send_transaction(tx)
        logger.info(f"Transação enviada: {tx_hash.hex()}")

        # Aguarda confirmação
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        contract_address = tx_receipt.contractAddress

        logger.info(f"Contrato implantado em: {contract_address}")

        # Salva o endereço do contrato
        with open("contracts/build/contract_address.txt", "w") as f:
            f.write(contract_address)

        # Salva o ABI
        with open("contracts/build/EVCharging.json", "w") as f:
            json.dump({
                "abi": abi,
                "address": contract_address,
                "networks": {
                    "development": {
                        "address": contract_address
                    }
                }
            }, f, indent=2)

        return contract_address

    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_CONTRACT_DEPLOY, str(e)))
        raise

if __name__ == "__main__":
    try:
        # Aguarda o Ganache estar pronto
        max_retries = 30
        retry_interval = 2
        for i in range(max_retries):
            try:
                w3 = Web3(Web3.HTTPProvider("http://ganache:8545"))
                if w3.is_connected():
                    break
            except:
                if i == max_retries - 1:
                    raise Exception("Timeout aguardando Ganache")
                logger.info(f"Aguardando Ganache... ({i+1}/{max_retries})")
                time.sleep(retry_interval)

        # Deploy do contrato
        contract_address = deploy_contract()
        logger.info("Deploy concluído com sucesso!")
        logger.info(f"Endereço do contrato: {contract_address}")

    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_CONTRACT_DEPLOYMENT_FAILED, str(e)))
        exit(1) 