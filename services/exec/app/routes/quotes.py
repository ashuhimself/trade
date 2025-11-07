from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class Quote(BaseModel):
    symbol: str
    exchange: str
    last_price: float
    bid: float
    ask: float
    volume: int


@router.get("/{exchange}/{symbol}", response_model=Quote)
async def get_quote(exchange: str, symbol: str):
    return Quote(
        symbol=symbol,
        exchange=exchange,
        last_price=1000.0,
        bid=999.5,
        ask=1000.5,
        volume=100000,
    )


@router.post("/subscribe")
async def subscribe_quotes(symbols: List[str]):
    return {"status": "subscribed", "symbols": symbols}
