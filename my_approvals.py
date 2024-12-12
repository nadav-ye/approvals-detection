from web3 import Web3
from typing import Dict, List, Tuple, Any
import argparse
import asyncio

import web3_utils


approval_event_signature = "0x" + Web3.keccak(text="Approval(address,address,uint256)").hex()

def get_padded_address_from_arg() -> hex:
    parser = argparse.ArgumentParser()
    parser.add_argument("--address", required=True)
    args = parser.parse_args()
    address:hex = args.address
    return web3_utils.encode_address_to_32bytes(address)

def is_valid_data(log_data: str) -> bool:
    try:
        int(log_data.hex(), 16)
        return True
    except Exception as e:
        print(f"couldn't retreive data, exception: {e}")
        return False

def is_log_more_recent(candidate_block_number: str, candidate_log_index: str, existing_block: str, existing_index):
    return (candidate_block_number > existing_block) or (candidate_block_number == existing_block and candidate_log_index > existing_index)

def get_most_recent_approvals(logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    latest_logs: Dict[Tuple[str, str], Dict[str, Any]] = {}
    
    for log in logs:
        try:
            token = log["address"].lower()
            spender_topic = log["topics"][2] # spender topic
            spender = "0x" + spender_topic.hex()[26:]  # represented 20 bytes
            block_number = log.get("blockNumber", 0)
            log_index = log.get("logIndex", 0)
            
            key = (spender, token)
            
            if key not in latest_logs:
                latest_logs[key] = log
            else:
                existing_log = latest_logs[key]
                existing_block = existing_log.get("blockNumber", 0)
                existing_index = existing_log.get("logIndex", 0)
                if is_valid_data(log["data"]) and is_log_more_recent(block_number, log_index, existing_block, existing_index):
                    latest_logs[key] = log

        except (IndexError, AttributeError, KeyError) as e:
            continue  # Skip potentially malformed logs
    
    return list(latest_logs.values())


async def main():
    padded_address = get_padded_address_from_arg()

    filtered_logs = await web3_utils.get_all_logs_of_an_event_signature_of_address(approval_event_signature, padded_address)

    contracts_addresses_set = set(log["address"] for log in filtered_logs)

    contract_name_map = await web3_utils.fetch_contract_names(contracts_addresses_set)

    latest_approvals:List[Dict[str, Any]] = get_most_recent_approvals(filtered_logs)

    for log in latest_approvals:
        amount = int(log["data"].hex(), 16)
        print(f"approval on {contract_name_map[log['address']]} on amount of {amount}")
    

if __name__ == "__main__":
    asyncio.run(main())