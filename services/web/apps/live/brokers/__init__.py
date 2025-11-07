from .base import BaseBroker
from .paper import PaperBroker
from .upstox import UpstoxBroker
from .zerodha import ZerodhaBroker

__all__ = ["BaseBroker", "PaperBroker", "ZerodhaBroker", "UpstoxBroker"]


def get_broker(broker_name: str = "paper") -> BaseBroker:
    brokers = {
        "paper": PaperBroker,
        "zerodha": ZerodhaBroker,
        "upstox": UpstoxBroker,
    }

    broker_class = brokers.get(broker_name.lower())
    if not broker_class:
        raise ValueError(f"Unknown broker: {broker_name}")

    return broker_class()
