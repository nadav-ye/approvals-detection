from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

import address_approvals
import approvals_dto
import price_enricher
import asyncio
import logging


app = FastAPI()
logger = logging.getLogger("uvicorn.error")

token_price_enricher = price_enricher.PriceEnricher()


class ApprovalsRequest(BaseModel):
    """
    approval request object
    """
    addresses: List[str]
    include_token_price: bool | None = None


async def _fetch_async_approvals(owner: str, semaphore: asyncio.Semaphore, result: Dict[str, List[Dict[str, Any]]]):
    """
    given an owner, a semaphore and a result dictionary, fetches the owner approvals in an async manner
    """
    async with semaphore:
        result[owner] = await address_approvals.get_address_approvals(owner)


async def _enrich_prices(response: Dict[str, List[approvals_dto.ApprovalDTO]]) -> None:
    """
    given the reponse to the client, enriches with the token price, if exists
    """
    unique_addresses = set()
    for dtos in response.values():
        for dto in dtos:
            unique_addresses.add(dto.token_address)
    token_prices = await token_price_enricher.get_tokens_prices(unique_addresses)
    for dtos in response.values():
        for dto in dtos:
            dto.price = token_prices.get(dto.token_address, None)


@app.post("/get_approvals", response_model_exclude_none=True)
async def get_approvals(request: ApprovalsRequest) -> Dict[str, Any]:
    """
    an entry point for a list of addresses, returning their most recent approvals per token and a spender
    """
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
