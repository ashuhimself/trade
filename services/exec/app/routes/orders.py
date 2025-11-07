from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class OrderRequest(BaseModel):
    symbol: str
    exchange: str
    side: str
    quantity: int
    order_type: str = "market"
    price: float | None = None
    trigger_price: float | None = None


class OrderResponse(BaseModel):
    order_id: str
    status: str
    message: str


@router.post("/", response_model=OrderResponse)
async def place_order(order: OrderRequest):
    import uuid

    order_id = str(uuid.uuid4())

    return OrderResponse(
        order_id=order_id,
        status="submitted",
        message="Order submitted to execution queue",
    )


@router.get("/{order_id}", response_model=dict)
async def get_order_status(order_id: str):
    return {
        "order_id": order_id,
        "status": "pending",
        "filled_quantity": 0,
        "avg_fill_price": 0.0,
    }


@router.delete("/{order_id}")
async def cancel_order(order_id: str):
    return {"order_id": order_id, "status": "cancelled"}
