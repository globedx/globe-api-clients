"""
An example file to test the public calls are working.
"""
import asyncio
import sys

sys.path.append("..")
sys.path.append("python_client/")
sys.path.append("")


def print_(string):
    """
    A Handler - can be defined by user.
    """
    print(string)


async def test_logic():
    """
    Functions to test
    """
    await GLOBE.get_my_market_events(instrument="XBTUSD", handler=print_)
    await GLOBE.my_open_orders(instrument="XBTUSD", handler=print_)
    await GLOBE.get_my_account_overview(handler=print_)
    await GLOBE.my_positions(handler=print_)
    market = {
        "instrument": "XBTUSD",
        "quantity": 1,
        "order_type": "market",
        "side": "sell",
    }
    await GLOBE.place_order(market)
    limit = {
        "instrument": "XBTUSD",
        "quantity": 1,
        "order_type": "limit",
        "price": 57000,
        "side": "sell",
    }
    await GLOBE.place_order(limit)
    stop_market = {
        "instrument": "XBTUSD",
        "quantity": 1,
        "trigger_price": 56300.0,
        "order_type": "stop-market",
        "side": "buy",
    }
    await GLOBE.place_order(stop_market)
    stop_limit = {
        "instrument": "XBTUSD",
        "quantity": 1,
        "trigger_price": 56300.0,
        "order_type": "stop-limit",
        "price": 56400,
        "side": "buy",
    }
    await GLOBE.place_order(stop_limit)
    print(await GLOBE.get_open_orders(instrument="XBTUSD"))
    print(await GLOBE.get_my_trades(instrument="XBTUSD"))


async def main(logic):
    """
    The main function it is running including connecting.
    """
    await GLOBE.connect()
    await asyncio.wait([GLOBE.run_loop(), logic()])


if __name__ == "__main__":
    from src.globe import Globe
    AUTH = {"api-key": "",
            "passphrase": "",
            "secret": ""
            }
    GLOBE = Globe(authentication=AUTH)
    asyncio.get_event_loop().run_until_complete(main(test_logic))
