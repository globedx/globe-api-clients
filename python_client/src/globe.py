"""
globe.py holds the key methods for the WebSocket API.
"""
import json
from datetime import datetime
import hmac
import hashlib
import base64
import websockets


class Globe:
    """
    Globe class contains all the relevant WebSocket API commands.
    """

    def __init__(self, error_handler=None):
        self.uri = "wss://globedx.com/api/v1/ws"
        self.socket = websockets
        self.error_handler = error_handler
        self.received_handlers = {}

    async def _send(self, message):
        """
        Sends the request to the webserver
        """
        await self.socket.send(json.dumps(message))

    async def run_loop(self):
        """
        Listens for the response from the webserver.
        """
        while True:
            received = await self.socket.recv()
            received = json.loads(received)
            if "subscription" in received:
                if received["subscription"]["channel"] in self.received_handlers:
                    self.received_handlers[received["subscription"]["channel"]](
                        received
                    )
                else:
                    print(received)
            else:
                if self.error_handler:
                    self.error_handler(received)
                else:
                    print("Globe Error: ", received)

    async def subscribe_depth(self, instrument, handler=None):
        """
        Subscribes to market depth.
        """
        if handler:
            self.received_handlers["depth"] = handler
        message = {"command": "subscribe",
                   "channel": "depth", "instrument": instrument}
        await self._send(message)

    async def subscribe_product_list(self, handler=None):
        """
        Subscribes to product list.
        """
        if handler is not None:
            self.received_handlers["product-list"] = handler
        message = {"command": "subscribe", "channel": "product-list"}
        await self._send(message)

    async def subscribe_index_price(self, instrument, handler=None):
        """
        Subscribes to current index price.
        """
        if handler is not None:
            self.received_handlers["index-price"] = handler
        message = {
            "command": "subscribe",
            "channel": "index-price",
            "instrument": instrument,
        }
        await self._send(message)

    async def subscribe_product_detail(self, instrument, handler=None):
        """
        Subscribes to product detail.
        """
        if handler:
            self.received_handlers["product-detail"] = handler
        message = {
            "command": "subscribe",
            "channel": "product-detail",
            "instrument": instrument,
        }
        await self._send(message)

    async def subscribe_recent_trades(self, instrument, handler=None):
        """
        Subscribes to recent trades.
        """
        if handler:
            self.received_handlers["trades"] = handler
        message = {
            "command": "subscribe",
            "channel": "trades",
            "instrument": instrument,
        }
        await self._send(message)

    async def subscribe_market_overview(self, instrument, handler=None):
        """
        Subscribes to market overview.
        """
        if handler:
            self.received_handlers["market-overview"] = handler
        message = {
            "command": "subscribe",
            "channel": "market-overview",
            "instrument": instrument,
        }
        await self._send(message)

    async def subscribe_open_interest(self, instrument, handler=None):
        """
        Subscribes to open interest.
        """
        if handler:
            self.received_handlers["open-interest"] = handler
        message = {
            "command": "subscribe",
            "channel": "open-interest",
            "instrument": instrument,
        }
        await self._send(message)

    async def subscribe_insurance_fund(self, instrument, handler=None):
        """
        Subscribes to insurance funds.
        """
        if handler:
            self.received_handlers["insurance-fund"] = handler
        message = {"command": "subscribe",
                   "channel": "insurance-fund", "instrument": instrument}
        await self._send(message)

    async def subscribe_my_account_overview(self, handler=None):
        """
        Subscribes to your account overview.
        """
        if handler:
            self.received_handlers["my-account-overview"] = handler
        message = {"command": "subscribe", "channel": "my-account-overview"}
        await self._send(message)

    async def subscribe_my_market_events(self, instrument, handler=None):
        """
        Subscribes to your market events.
        """
        if handler:
            self.received_handlers["my-market-events"] = handler
        message = {
            "command": "subscribe",
            "channel": "my-market-events",
            "instrument": instrument,
        }
        await self._send(message)

    async def cancel_order(self, _id, instrument):
        """
        Cancel your order.
        """
        message = {"command": "cancel-order",
                   "instrument": instrument, "order_id": _id}
        await self._send(message)

    async def my_open_orders(self, instrument, handler=None):
        """
        Subscribes to your open orders.
        """
        if handler:
            self.received_handlers["my-orders"] = handler
        message = {
            "command": "subscribe",
            "channel": "my-orders",
            "instrument": instrument,
        }

        await self._send(message)

    async def my_positions(self, handler=None):
        """
        Subscribes to your positions.
        """
        if handler:
            self.received_handlers["my-positions"] = handler
        message = {"command": "subscribe", "channel": "my-positions"}
        await self._send(message)

    async def place_order(self, order):
        """
        Places an order.
        """
        order["command"] = "place-order"
        await self._send(order)

    async def stop_order(self, trigger, order):
        """
        Stops an order.
        """
        message = {"command": "stop-order", "trigger": trigger, "order": order}
        await self._send(message)

    async def connect(self, authentication=None):
        """
        Connects to the webserver.
        """
        if not authentication:
            self.socket = await websockets.connect(self.uri)
            print("Connected to Globe Websocket.")
        if authentication:
            headers = {
                "X-Access-Key": authentication["api-key"],
                "X-Access-Signature": "",
                "X-Access-Nonce": str(int(datetime.now().strftime("%Y%m%d%H%M%S"))),
                "X-Access-Passphrase": authentication["passphrase"],
            }
            secret = authentication["secret"]
            sign_txt = headers["X-Access-Nonce"] + "GET/api/v1/ws"

            headers["X-Access-Signature"] = str(
                _hash(sign_txt, secret), "utf-8")

            self.socket = await websockets.connect(self.uri, extra_headers=headers)
            print("Connected to Globe Websocket.")


def _hash(sign_txt, secret):
    """
    Hashing function for the signature and authentication.
    """
    sign_txt = bytes(sign_txt, "utf-8")
    secret = bytes(secret, "utf-8")
    secret = base64.b64decode(secret)
    signature = base64.b64encode(
        hmac.new(secret, sign_txt, digestmod=hashlib.sha256).digest()
    )
    return signature
