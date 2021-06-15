"""
globe.py holds the key methods for the WebSocket API.
"""
import json
from datetime import datetime, timezone
import hmac
import hashlib
import base64
from uuid import uuid4
import websockets
import aiohttp

# pylint: disable=R0904


class Globe:
    """
    Globe class contains all of Globes WebSocket WS channel subscriptions
    """

    def __init__(self, error_handler=None, authentication=None):
        self.uri = "wss://globedx.com/api/v1/ws"
        self.socket = websockets
        self.http_api = "http://www.globedx.com/api/v1"
        self.error_handler = error_handler
        self.received_handlers = {}
        self.session = aiohttp.ClientSession()
        self.authentication = authentication

    async def _send(self, message):
        """
        Send the subscription channel request to the server.
        """
        await self.socket.send(json.dumps(message))

    async def run_loop(self):
        """
        Continually listen and process any responses on the websocket from the server.
        """
        while True:
            received = await self.socket.recv()
            received = json.loads(received)
            if "subscription" in received:
                if "instrument" in received["subscription"]:
                    key = "{}{}".format(
                        received["subscription"]["channel"],
                        received["subscription"]["instrument"])
                    if key in self.received_handlers:
                        await self.received_handlers[key](
                            received
                        )
                elif received["subscription"]["channel"] in self.received_handlers:
                    await self.received_handlers[received["subscription"]["channel"]](
                        received)
                else:
                    print(received)
            else:
                if self.error_handler:
                    self.error_handler(received)
                else:
                    print("Globe Error: ", received)

    async def get_depth(self, instrument, handler=None):
        """
        Subscribe to the the market depth (l2 orderbook) with a given handler, for an instrument.
        """
        if handler is not None:
            key = "depth{}".format(instrument)
            self.received_handlers[key] = handler
        message = {"command": "subscribe",
                   "channel": "depth", "instrument": instrument}
        await self._send(message)

    async def get_product_list(self, handler=None):
        """
        Get the product list with a given handler
        """
        if handler is not None:
            self.received_handlers["product-list"] = handler
        message = {"command": "subscribe", "channel": "product-list"}
        await self._send(message)

    async def get_index_price(self, instrument, handler=None):
        """
        Subscribe to the index price with a given handler, for an instrument.
        """
        if handler is not None:
            key = "index-price{}".format(instrument)
            self.received_handlers[key] = handler
        message = {
            "command": "subscribe",
            "channel": "index-price",
            "instrument": instrument,
        }
        await self._send(message)

    async def get_product_detail(self, instrument, handler=None):
        """
        Get the product detail with a given handler, for an instrument.
        """
        if handler is not None:
            key = "product-detail{}".format(instrument)
            self.received_handlers[key] = handler
        message = {
            "command": "subscribe",
            "channel": "product-detail",
            "instrument": instrument,
        }
        await self._send(message)

    async def get_recent_trades(self, instrument, handler=None):
        """
        Subscribe to recent trades with a given handler, for an instrument.
        """
        if handler is not None:
            key = "trades{}".format(instrument)
            self.received_handlers[key] = handler
        message = {
            "command": "subscribe",
            "channel": "trades",
            "instrument": instrument,
        }
        await self._send(message)

    async def get_market_overview(self, instrument, handler=None):
        """
        Get the market overview with a given handler, for an instrument.
        """
        if handler is not None:
            key = "market-overview{}".format(instrument)
            self.received_handlers[key] = handler
        message = {
            "command": "subscribe",
            "channel": "market-overview",
            "instrument": instrument,
        }
        await self._send(message)

    async def get_price_history(self, instrument, resolution="1m", handler=None):
        """
        Subscribe to the price history with a given handler, for an instrument and resolution.
        """
        if handler is not None:
            key = "price-history{}".format(instrument)
            self.received_handlers[key] = handler
        message = {
            "command": "subscribe",
            "channel": "price-history",
            "instrument": instrument,
            "resolution": resolution,
        }
        await self._send(message)

    async def get_open_interest(self, instrument, handler=None):
        """
        Gets the open interest with a given handler, for an instrument.
        """
        if handler is not None:
            key = "open-interest{}".format(instrument)
            self.received_handlers[key] = handler
        message = {
            "command": "subscribe",
            "channel": "open-interest",
            "instrument": instrument,
        }
        await self._send(message)

    async def get_insurance_fund(self, handler=None):
        """
        Get the insurance fund, with a given handler, for an instrument.
        """
        if handler is not None:
            self.received_handlers["insurance-fund"] = handler
        message = {
            "command": "subscribe",
            "channel": "insurance-fund",
        }
        await self._send(message)

    async def get_my_account_overview(self, handler=None):
        """
        Get your account overview, with a given handler.
        """
        if handler:
            self.received_handlers["my-account-overview"] = handler
        message = {"command": "subscribe", "channel": "my-account-overview"}
        await self._send(message)

    async def get_my_market_events(self, instrument, handler=None):
        """
        Subscribe to your market events, with a given handler.
        """
        if handler is not None:
            key = "my-market-events{}".format(instrument)
            self.received_handlers[key] = handler
        message = {
            "command": "subscribe",
            "channel": "my-market-events",
            "instrument": instrument,
        }
        await self._send(message)

    async def cancel_order(self, _id, instrument, cancel_id=None, new_quantity=None) -> str:
        """
        Submit an order cancellation, with a given order id and instrument.
        """
        message = {"command": "cancel-order",
                   "instrument": instrument, "order_id": _id}
        if cancel_id:
            message["cancel_id"] = cancel_id
        else:
            message["cancel_id"] = str(uuid4())
        if new_quantity:
            message["new_quantity"] = new_quantity
        await self._send(message)
        return message["cancel_id"]

    async def cancel_stop_order(self, _id, instrument, cancel_id=None) -> str:
        """
        Submit an stop order cancellation, with a given order id and instrument.
        """
        message = {"command": "cancel-stop-order",
                   "instrument": instrument, "order_id": _id}
        if cancel_id:
            message["cancel_id"] = cancel_id
        else:
            message["cancel_id"] = str(uuid4())
        await self._send(message)
        return message["cancel_id"]

    async def my_open_orders(self, instrument, handler=None):
        """
        Get your open orders, with a given handler, for an instrument.
        """
        if handler is not None:
            key = "my-orders{}".format(instrument)
            self.received_handlers[key] = handler
        message = {
            "command": "subscribe",
            "channel": "my-orders",
            "instrument": instrument,
        }
        await self._send(message)

    async def my_positions(self, handler=None):
        """
        Get your positions, with a given handler.
        """
        if handler:
            self.received_handlers["my-positions"] = handler
        message = {"command": "subscribe", "channel": "my-positions"}
        await self._send(message)

    async def place_order(self, order) -> str:
        """
        Place an order.
        """
        if 'order_id' not in order:
            order['order_id'] = str(uuid4())
        order["command"] = "place-order"
        await self._send(order)
        return order['order_id']

    async def get_historic_market_rates(self, instrument, resolution):
        """
        Get historic OHLC bars for a instrument and are returned
        in grouped buckets based on requested resolution.
        """
        endpoint = (
            self.http_api + "/history/" + instrument + "/candles/" + resolution
        )
        async with self.session.get(endpoint) as output:
            output = await output.json()
        return output

    async def get_open_orders(self, instrument, upto_timestamp=None, page_size=100):
        """
        Get your current open orders for a product.
        """
        endpoint = (
            self.http_api + "/orders/open-orders"
        )
        if not upto_timestamp:
            upto_timestamp = int(datetime.now().timestamp() * 1000)

        params = {
            'instrument': instrument,
            'upto_timestamp': upto_timestamp,
            'page_size': page_size,
        }
        extra_headers = self.auth_headers(url="GET/api/v1/orders/open-orders")
        async with self.session.get(endpoint, params=params, headers=extra_headers) as output:
            output = await output.text()
        return output

    async def get_positions(self):
        """
        Get your current positions for instruments.
        """
        endpoint = (
            self.http_api + "/positions"
        )

        extra_headers = self.auth_headers(url="GET/api/v1/positions")
        async with self.session.get(endpoint, headers=extra_headers) as output:
            output = await output.json()
        return output

    async def get_account_overview(self):
        """
        Get your current account overview.
        """
        endpoint = (
            self.http_api + "/account-overview"
        )

        extra_headers = self.auth_headers(url="GET/api/v1/account-overview")
        async with self.session.get(endpoint, headers=extra_headers) as output:
            output = await output.json()
        return output

    async def get_my_trades(self, instrument, page=None):
        """
        Get your current my previous trades for a product.
        """
        endpoint = (
            self.http_api + "/history/my-trades"
        )
        if not page:
            page = 0

        params = {
            'instrument': instrument,
            'page': page,
        }
        extra_headers = self.auth_headers(url="GET/api/v1/history/my-trades")
        async with self.session.get(endpoint, params=params, headers=extra_headers) as output:
            output = await output.text()
        return output

    async def get_historic_index_price_rates(self, instrument, resolution):
        """
        Get historic OHLC bars for an indexp price of an instrument
        and are returned in grouped buckets based on requested resolution.
        """
        endpoint = (
            self.http_api
            + "/history/index-price/"
            + instrument
            + "/candles/"
            + resolution
        )
        async with self.session.get(endpoint) as output:
            output = await output.json()
        return output

    def auth_headers(self, url):
        """
        Generate new authentication headers
        """
        if not self.authentication:
            raise Exception("Authentication is required")
        headers = {
            "X-Access-Key": self.authentication["api-key"],
            "X-Access-Signature": "",
            "X-Access-Nonce": str(int(datetime.now(timezone.utc).timestamp() * 1000)),
            "X-Access-Passphrase": self.authentication["passphrase"],
        }
        secret = self.authentication["secret"]
        sign_txt = headers["X-Access-Nonce"] + url
        headers["X-Access-Signature"] = str(
            _hash(sign_txt, secret), "utf-8")
        return headers

    async def connect(self):
        """
        Connect to the websocket server.
        """
        if not self.authentication:
            self.socket = await websockets.connect(self.uri)
            print("Connected to Globe Websocket.")
        if self.authentication:
            extra_headers = self.auth_headers(url="GET/api/v1/ws")
            self.socket = await websockets.connect(self.uri, extra_headers=extra_headers)
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
