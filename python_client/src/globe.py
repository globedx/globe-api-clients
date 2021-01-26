"""
globe.py holds the key methods for the WebSocket API.
"""
import json
from datetime import datetime
import hmac
import hashlib
import base64
import websockets
import aiohttp


class Globe:
    """
    Globe class contains all of Globes WebSocket WS channel subscriptions
    """

    def __init__(self, error_handler=None):
        self.uri = "wss://globedx.com/api/v1/ws"
        self.socket = websockets
        self.http_api = "http://www.globedx.com/api/v1"
        self.error_handler = error_handler
        self.received_handlers = {}
        self.session = aiohttp.ClientSession()

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
                        received["subscription"]["channel"], received["subscription"]["instrument"])
                    if key in self.received_handlers:
                        self.received_handlers[key](
                            received
                        )
                elif received["subscription"]["channel"] in self.received_handlers:
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

    async def cancel_order(self, _id, instrument):
        """
        Submit an order cancellation, with a given order id and instrument.
        """
        message = {"command": "cancel-order",
                   "instrument": instrument, "order_id": _id}
        await self._send(message)

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

    async def place_order(self, order):
        """
        Place an order.
        """
        order["command"] = "place-order"
        await self._send(order)

    async def stop_order(self, trigger, order):
        """
        Place an stop order.
        """
        message = {"command": "stop-order", "trigger": trigger, "order": order}
        await self._send(message)

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
        await self.session.close()
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
        await self.session.close()
        return output

    async def connect(self, authentication=None):
        """
        Connect to the websocket server.
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
