import address_approvals
import approvals_dto
import price_enricher
import asyncio
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any


app = FastAPI()
logger = logging.getLogger("uvicorn.error")
token_price_enricher = price_enricher.PriceEnricher()


class ApprovalsRequest(BaseModel):
    addresses: List[str]
    include_token_price: bool | None = None


async def _fetch_async_approvals(owner: str, semaphore: asyncio.Semaphore, result: Dict[str, List[Dict[str, Any]]]):
    async with semaphore:
        result[owner] = await address_approvals.get_address_approvals(owner)


async def _enrich_prices(response: Dict[str, List[approvals_dto.ApprovalDTO]]) -> None:
    unique = set()
    for dtos in response.values():
        for dto in dtos:
            unique.add(dto.token_address)
    token_prices = await token_price_enricher.get_tokens_prices(unique)
    for dtos in response.values():
        for dto in dtos:
            dto.price = token_prices.get(dto.token_address, None)


@app.post("/get_approvals")
async def get_approvals(request: ApprovalsRequest) -> Dict[str, Any]:
    results = dict()

    semaphore = asyncio.Semaphore(6)
    addresses = set(address.lower() for address in request.addresses)
    tasks = [_fetch_async_approvals(address, semaphore, results) for address in addresses]

    await asyncio.gather(*tasks)
    response = dict()
    for owner in results.keys():
        approvals_dtos = []
        for approval in results[owner]:
            approvals_dtos.append(approvals_dto.approval_dto_from_log(approval))
        response[owner] = approvals_dtos
    
    if request.include_token_price:
        await _enrich_prices(response)

    return response
