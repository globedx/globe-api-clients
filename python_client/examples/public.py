"""
An example file to test the public calls are working.
"""
import asyncio
import sys


sys.path.append("..")
sys.path.append("python_client/")
sys.path.append("")


async def print_(string):
    """
    A Handler - can be defined by user.
    """
    print(string)
    await asyncio.sleep(0.0001)


async def test_logic():
    """
    Functions to test
    """
    await GLOBE.get_index_price(instrument="XBTUSD", handler=print_)
    await GLOBE.get_depth(instrument="XBTUSD", handler=print_)
    await GLOBE.get_product_list(handler=print_)
    await GLOBE.get_product_detail(instrument="XBTUSD", handler=print_)
    await GLOBE.get_recent_trades(instrument="XBTUSD", handler=print_)
    await GLOBE.get_market_overview(instrument="XBTUSD", handler=print_)
    await GLOBE.get_open_interest(instrument="XBTUSD", handler=print_)
    await GLOBE.get_insurance_fund(handler=print_)
    await GLOBE.get_price_history(instrument="XBTUSD", resolution="1m", handler=print_)
    print(await GLOBE.get_historic_market_rates(instrument="XBTUSD", resolution="1m"))
    print(await GLOBE.get_historic_index_price_rates(instrument="XBTUSD", resolution="1m"))


async def main(logic):
    """
    The main function it is running including connecting.
    """
    await GLOBE.connect()
    await asyncio.wait([GLOBE.run_loop(), logic()])


if __name__ == "__main__":
    from src.globe import Globe

    GLOBE = Globe()
    asyncio.get_event_loop().run_until_complete(main(test_logic))
