from web3 import Web3
from typing import Dict, List, Tuple, Any

import logging
import web3_utils


approval_event_signature = "0x" + Web3.keccak(text="Approval(address,address,uint256)").hex()
logger = logging.getLogger(__name__)


def _is_valid_data(log_data: str) -> bool:
    """
    given an approval log, verifing its data (amount)
    """
    try:
        int(log_data.hex(), 16)
        return True
    except Exception as e:
        logger.error(f"couldn't retreive data field from log, exception: {e}")
        return False

def _is_log_more_recent(candidate_log: str, existing_log: str):
    """
    given two logs, check whether the candidate is newer than the existing one
    """
    candidate_block_number = candidate_log.get("blockNumber", 0)
    candidate_transaction_index = candidate_log.get("transactionIndex", 0)
    candidate_log_index = candidate_log.get("logIndex", 0)
    existing_block = existing_log.get("blockNumber", 0)
    existing_transaction_index = candidate_log.get("transactionIndex", 0)
    existing_log_index = existing_log.get("logIndex", 0)
    return (candidate_block_number > existing_block) or \
        (candidate_block_number == existing_block and candidate_transaction_index > existing_transaction_index) or \
        (candidate_block_number == existing_block and candidate_transaction_index == existing_transaction_index and candidate_log_index > existing_log_index)

def _get_most_recent_approvals(logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    given approval logs, returns the most recent approvals per token and spender
    """
    latest_logs: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for log in logs:
        try:
            token = log["address"].lower()
            spender = web3_utils.get_erc20_spender(log)
            key = (spender, token)
            if key not in latest_logs:
                latest_logs[key] = log
            else:
                existing_log = latest_logs[key]
                if _is_valid_data(log["data"]) and _is_log_more_recent(candidate_log=log, existing_log=existing_log):
                    latest_logs[key] = log
        except Exception as e:
            logger.error(f"error during log processing: {e}")
            continue  # Skip potentially malformed logs
    return list(latest_logs.values())

async def get_address_approvals(owner: str):
    """
    given an owner address, fetches its approval since the first block
    """
    padded_owner = web3_utils.encode_address_to_32bytes(owner)
    filtered_logs = await web3_utils.get_all_logs_of_an_event_signature_of_address(approval_event_signature, padded_owner)
    contracts_addresses_set = set(log["address"] for log in filtered_logs)
    await web3_utils.fetch_contract_names(contracts_addresses_set)
    latest_approvals:List[Dict[str, Any]] = _get_most_recent_approvals(filtered_logs)
    return latest_approvals