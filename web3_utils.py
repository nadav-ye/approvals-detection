from web3 import AsyncWeb3
from web3.contract.async_contract import AsyncContract
from typing import Set, Dict, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception,
)

import json
import logging


infura_api_key = "ee139a7e573e401c968e84cb8d8342a6"
w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(f'https://mainnet.infura.io/v3/{infura_api_key}'))
logger = logging.getLogger(__name__)
with open("erc20_basic_abi.json") as abi:
    erc20_abi = json.load(abi)
contract_name_map:Dict = dict()


def encode_address_to_32bytes(address: str) -> str:
    """
    padding address to 32 bytes
    """
    address_bytes = bytes.fromhex(address[2:])
    padded = address_bytes.rjust(32, b'\0')
    return '0x' + padded.hex()

def get_erc20_spender(log: Dict[str, Any]) -> str:
    """
    given an erc20 approval log, returns the spender address
    """
    spender_topic = log["topics"][2]
    return "0x" + spender_topic.hex()[26:]  # represented 20 bytes

def _is_429_exception(exception: Exception):
    return '429' in str(exception)

@retry(
    retry=retry_if_exception(_is_429_exception),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(2),
    reraise=True
)
async def get_all_logs_of_an_event_signature_of_address(event_signature:str, from_address: str):
    """
    returns all logs of a given event signature from an address
    """
    approval_filter = await w3.eth.filter({
        "fromBlock":'earliest', 
        "toBlock":'latest',
        "topics": [event_signature,
                   from_address]
        })
    filtered_logs = await approval_filter.get_all_entries()
    return filtered_logs

def _get_erc20_contract(contract_address: str) -> AsyncContract:
    """
    return the erc20 contract of an address
    """
    return w3.eth.contract(address=contract_address, abi=erc20_abi)

async def _get_contract_name(contract: AsyncContract) -> str:
    """
    given a contract gets its name, if exists
    """
    return await contract.functions.name().call()

@retry(
    retry=retry_if_exception(_is_429_exception),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(2),
    reraise=True
)
async def fetch_contract_names(contract_addresses: Set[str]) -> None:
    """
    updates the contract name map with the contract addresses names
    """
    
    async def fetch_name(address: str):
        try:
            contract = _get_erc20_contract(address)
            name = await _get_contract_name(contract)
            contract_name_map[address] = name
        except Exception as e:
            logger.error(f"failed to fetch name for address {address}, error details: {e}")
            contract_name_map[address] = address  # fallback - name isn't mandatory; in case that it exist but raised a 429 error, the address would be a placeholder
            raise e

    addresses_for_name_request = contract_addresses - contract_name_map.keys()
    for address_for_request in addresses_for_name_request:
        await fetch_name(address_for_request)