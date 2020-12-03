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
    await GLOBE.get_my_account_overview()
    await GLOBE.my_positions()
    market = {
        "instrument": "XBTUSD",
        "quantity": 250,
        "order_type": "market",
        "side": "sell",
    }
    limit = {
        "instrument": "XBTUSD",
        "quantity": 1,
        "price": 10.0,
        "order_type": "limit",
        "side": "buy",
    }
    await GLOBE.place_order(market)
    await GLOBE.place_order(limit)


async def main(logic):
    """
    The main function it is running including connecting.
    """
    auth = {"api-key": "", "passphrase": "", "secret": ""}
    await GLOBE.connect(authentication=auth)
    await asyncio.wait([GLOBE.run_loop(), logic()])


if __name__ == "__main__":
    from src.globe import Globe

    GLOBE = Globe()
    asyncio.get_event_loop().run_until_complete(main(test_logic))
