from typing import Dict, List, Any
from fastapi import HTTPException

import httpx
import logging

logger = logging.getLogger(__name__)

class PriceEnricher():
    """
    Enricher for contracts prices
    """
    def __init__(self):
        self.__template_enrich_url:str = "https://api.coingecko.com/api/v3/simple/token_price/ethereum?contract_addresses={}&vs_currencies=usd"
        self.__gecko_headers:Dict = dict({"x-cg-demo-api-key":"CG-JpTpQR8qC3H8BNFca9Y363px"})

    _price_map: Dict = dict()

    def _prepare_gecko_request(self, missing_addresses: List[str]) -> str:
        """
        given a list of missing addresses prices, perpare a request for gecko API
        """
        con_addresses = ",".join(missing_addresses)
        return self.__template_enrich_url.format(con_addresses)

    async def _fetch_tokens_prices(self, token_addresses: List[str]):
        """
        fetches tokens prices from gecko
        """
        request_url = self._prepare_gecko_request(token_addresses)
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(request_url, headers=self.__gecko_headers)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"failed to fetch price from gecko with error: {e}")

    async def get_tokens_prices(self, token_addresses: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        given a lost of token addresses, returns their prices (if exist), enriching from gecko if needed
        """
        missing_tokens: List[str] = []
        for token_address in token_addresses:
            if token_address not in self._price_map.keys():
                missing_tokens.append(token_address)
        if len(missing_tokens):
            missing_tokens_prices = await self._fetch_tokens_prices(missing_tokens)
            self._price_map = self._price_map | missing_tokens_prices
        return self._price_map