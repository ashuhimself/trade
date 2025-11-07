import json

from channels.generic.websocket import AsyncWebsocketConsumer


class QuotesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("quotes", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("quotes", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get("action") == "subscribe":
            symbols = data.get("symbols", [])
            await self.send(
                text_data=json.dumps(
                    {"type": "subscribed", "symbols": symbols, "message": "Subscribed to quotes"}
                )
            )

    async def quote_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))


class OrdersConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("orders", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("orders", self.channel_name)

    async def order_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))


class PnLConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("pnl", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("pnl", self.channel_name)

    async def pnl_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
