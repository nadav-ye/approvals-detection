import address_approvals
import approvals_dto

from typing import List, Dict, Any

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()


class ApprovalsRequest(BaseModel):
    addresses: List[str]
    include_token_price: bool | None = None


@app.post("/get_approvals")
async def get_approvals(request: ApprovalsRequest) -> Dict[str, Any]:
    result = dict()
    for address in set(request.addresses):
        approvals: List[Dict] = await address_approvals.get_address_approvals(address)
        approvals_dtos = []
        for approval in approvals:
            approvals_dtos.append(approvals_dto.approval_dto_from_log(approval))
        result[address] = approvals_dtos
    print(result)
    return result
