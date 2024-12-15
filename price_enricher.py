import httpx
import logging
from fastapi import HTTPException
from typing import Dict, List, Any

class PriceEnricher():
    def __init__(self):
        self.__template_enrich_url:str = "https://api.coingecko.com/api/v3/simple/token_price/ethereum?contract_addresses={}&vs_currencies=usd"
        self.__gecko_headers:Dict = dict({"x-cg-demo-api-key":"CG-JpTpQR8qC3H8BNFca9Y363px"})

    _price_map: Dict = dict()

    def _prepare_gecko_request(self, missing_addresses: List[str]) -> str:
        con_addresses = ",".join(missing_addresses)
        logging.error(f"url: {self.__template_enrich_url.format(con_addresses)}")
        return self.__template_enrich_url.format(con_addresses)

    async def _fetch_tokens_prices(self, token_addresses: List[str]):
        request_url = self._prepare_gecko_request(token_addresses)
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(request_url, headers=self.__gecko_headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as exc:
                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail=f"Error fetching data from CoinGecko: {exc.response.text}"
                )
            except httpx.RequestError as exc:
                raise HTTPException(
                    status_code=500,
                    detail=f"An error occurred while requesting {exc.request.url!r}."
                )

    async def get_tokens_prices(self, token_addresses: List[str]) -> Dict[str, Dict[str, Any]]:
        missing_tokens: List[str] = []
        for token_address in token_addresses:
            if token_address not in self._price_map.keys():
                missing_tokens.append(token_address)
        if len(missing_tokens):
            missing_tokens_prices = await self._fetch_tokens_prices(missing_tokens)
            self._price_map = self._price_map | missing_tokens_prices
        return self._price_map