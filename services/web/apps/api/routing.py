from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/quotes/", consumers.QuotesConsumer.as_asgi()),
    path("ws/orders/", consumers.OrdersConsumer.as_asgi()),
    path("ws/pnl/", consumers.PnLConsumer.as_asgi()),
]
