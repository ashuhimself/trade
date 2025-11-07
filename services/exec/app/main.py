import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

from .routes import orders, quotes

# Create prometheus multiproc dir if it doesn't exist
prometheus_dir = os.getenv("PROMETHEUS_MULTIPROC_DIR", "/tmp/prometheus_multiproc")
Path(prometheus_dir).mkdir(parents=True, exist_ok=True)

order_counter = Counter("exec_orders_total", "Total orders received")
order_latency = Histogram("exec_order_latency_seconds", "Order processing latency")


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="Trading Execution Gateway",
    description="Low-latency order execution microservice",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(quotes.router, prefix="/quotes", tags=["quotes"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "exec-gateway"}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type="text/plain")
