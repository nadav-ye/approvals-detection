from pydantic import BaseModel
from typing import Dict, Any

import web3_utils

class ApprovalDTO(BaseModel):
    token_name: str
    token_address: str
    price: str | None = None
    spender: str
    amount: int

def approval_dto_from_log(approval_log: Dict[str, Any]) -> ApprovalDTO:
    approval_dto = ApprovalDTO(
        token_name=web3_utils.contract_name_map[approval_log["address"]],
        token_address=approval_log["address"].lower(),
        spender=web3_utils.get_erc20_spender(approval_log),
        amount = int(approval_log["data"].hex(), 16)
    )
    return approval_dto