from web3 import AsyncWeb3
from web3.contract.async_contract import AsyncContract
from typing import Set, Dict
import json
import asyncio

infura_api_key = "ee139a7e573e401c968e84cb8d8342a6"
w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(f'https://mainnet.infura.io/v3/{infura_api_key}'))

with open("erc20_basic_abi.json") as abi:
    erc20_abi = json.load(abi)

contract_name_map:Dict = dict()

def get_async_client() -> AsyncWeb3:
    return w3

def encode_address_to_32bytes(address: str) -> str:
    address_bytes = bytes.fromhex(address[2:])
    padded = address_bytes.rjust(32, b'\0')
    return '0x' + padded.hex()

async def get_all_logs_of_an_event_signature_of_address(event_signature:str, from_address: str):
    approval_filter = await w3.eth.filter({
        "fromBlock":'earliest', 
        "toBlock":'latest',
        "topics": [event_signature,
                   from_address]
        })
    filtered_logs = await approval_filter.get_all_entries()
    return filtered_logs

def get_erc20_contract(contract_address: str) -> AsyncContract:
    return w3.eth.contract(address=contract_address, abi=erc20_abi)

async def get_contract_name(contract: AsyncContract) -> str:
    return await contract.functions.name().call()

async def fetch_contract_names(contract_addresses: Set[str]) -> None:
    
    async def fetch_name(address: str):
        try:
            contract = get_erc20_contract(address)
            name = await get_contract_name(contract)
            contract_name_map[address] = name
        except Exception as e:
            contract_name_map[address] = address  # fallback - name isn't mandatory on

    addresses_for_name_request = contract_addresses - contract_name_map.keys()
    tasks = [fetch_name(address) for address in addresses_for_name_request]
    await asyncio.gather(*tasks)
