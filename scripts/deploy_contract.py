import os
import json
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from web3 import Web3
from shared.utils.logger import Logger
from shared.constants.texts import Texts
from domain.exceptions.custom_exceptions import BlockchainError

# Carrega variáveis de ambiente
load_dotenv()

logger = Logger(__name__)

def compile_contract():
    """
    Compila o contrato inteligente EVCharging.sol.
    Retorna o bytecode e ABI do contrato compilado.
    """
    try:
        # Instala versão do solc
        subprocess.run(["solc-select", "install", "0.8.19"], check=True)
        subprocess.run(["solc-select", "use", "0.8.19"], check=True)

        # Lê código fonte do contrato
        contract_path = Path("contracts/EVCharging.sol")
        with open(contract_path, "r") as f:
            contract_source = f.read()

        # Compila o contrato
        compile_command = [
            "solc",
            "--bin",
            "--abi",
            "--optimize",
            "--overwrite",
            "-o",
            "contracts",
            str(contract_path)
        ]
        subprocess.run(compile_command, check=True)

        # Salva contrato compilado
        compiled_data = {
            "bytecode": f"0x{open('contracts/EVCharging.bin').read()}",
            "abi": json.loads(open('contracts/EVCharging.abi').read())
        }
        with open("contracts/EVCharging.json", "w") as f:
            json.dump(compiled_data, f, indent=2)

        logger.info(Texts.LOG_CONTRACT_COMPILED)
        return compiled_data

    except subprocess.CalledProcessError as e:
        logger.error(Texts.format(Texts.ERROR_CONTRACT_COMPILE, str(e)))
        raise BlockchainError(Texts.format(Texts.ERROR_CONTRACT_COMPILE, str(e)))
    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_CONTRACT_COMPILE_UNEXPECTED, str(e)))
        raise BlockchainError(Texts.format(Texts.ERROR_CONTRACT_COMPILE_UNEXPECTED, str(e)))

def deploy_contract(compiled_sol):
    """
    Implanta o contrato compilado na rede Sepolia.
    Retorna o endereço do contrato implantado.
    """
    try:
        # Obtém bytecode e ABI do contrato
        bytecode = compiled_sol["bytecode"]
        abi = compiled_sol["abi"]

        # Conecta à rede Sepolia
        w3 = Web3(Web3.HTTPProvider(os.getenv("BLOCKCHAIN_PROVIDER_URL")))
        if not w3.is_connected():
            raise BlockchainError(Texts.ERROR_CONTRACT_NETWORK)

        # Configura conta do deployer
        deployer_address = os.getenv("BLOCKCHAIN_DEPLOYER_ADDRESS")
        deployer_key = os.getenv("BLOCKCHAIN_DEPLOYER_KEY")
        if not deployer_address or not deployer_key:
            raise BlockchainError(Texts.ERROR_CONTRACT_DEPLOYER_CONFIG)

        # Cria instância do contrato
        contract = w3.eth.contract(abi=abi, bytecode=bytecode)

        # Constrói transação de deploy
        nonce = w3.eth.get_transaction_count(deployer_address)
        gas_price = w3.eth.gas_price
        gas_limit = 3000000  # Ajuste conforme necessário

        transaction = contract.constructor().build_transaction({
            "from": deployer_address,
            "nonce": nonce,
            "gas": gas_limit,
            "gasPrice": gas_price,
            "chainId": 11155111  # Sepolia
        })

        # Assina e envia transação
        signed_txn = w3.eth.account.sign_transaction(transaction, deployer_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # Aguarda confirmação
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        contract_address = receipt.contractAddress

        logger.info(Texts.format(Texts.LOG_CONTRACT_DEPLOYED, contract_address))
        return contract_address

    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_CONTRACT_DEPLOY, str(e)))
        raise BlockchainError(Texts.format(Texts.ERROR_CONTRACT_DEPLOY, str(e)))

def main():
    """
    Função principal que orquestra a compilação e implantação do contrato.
    """
    try:
        # Compila o contrato
        compiled_sol = compile_contract()
        logger.info(Texts.LOG_CONTRACT_COMPILATION_COMPLETE)

        # Implanta o contrato
        contract_address = deploy_contract(compiled_sol)
        logger.info(Texts.format(Texts.LOG_CONTRACT_DEPLOYMENT_COMPLETE, contract_address))

        # Resumo da implantação
        print("\nResumo da Implantação:")
        print(f"Rede: Sepolia")
        print(f"Endereço do Contrato: {contract_address}")
        print(f"ABI salvo em: contracts/EVCharging.json")
        print("\nLembre-se de atualizar o arquivo .env com o novo endereço do contrato!")

    except Exception as e:
        logger.error(Texts.format(Texts.ERROR_CONTRACT_DEPLOYMENT_FAILED, str(e)))
        raise BlockchainError(Texts.format(Texts.ERROR_CONTRACT_DEPLOYMENT_FAILED, str(e)))

if __name__ == "__main__":
    main() 