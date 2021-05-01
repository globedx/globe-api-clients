import { Globe, OrderType, Side, ApiCredentials, Channel } from "../src/globe"

const errorHandler = (err: any) => console.log(err)

// Please add your own credentials
const CREDENTIALS: ApiCredentials = {
  apiKey: "",
  secret: "",
  passphrase: "",
}

const instrument = "XBTUSD"
const handle = (response: any) => console.log(response)

async function main() {
  console.log("Starting ...")
  const globe = new Globe(errorHandler, CREDENTIALS)
  await globe.connect()
  console.log("Authenticated worked and connected to websocket")

  // Subscribe to private channels
  globe.subscribe(Channel.myMarketEvents(instrument), handle)
  globe.subscribe(Channel.myOpenOrders(instrument), handle)
  globe.subscribe(Channel.myAccountOverview(), handle)
  globe.subscribe(Channel.myPositions(), handle)

  console.log(await globe.getOpenOrders(instrument))
  console.log(await globe.getMyTrades(instrument))

  // Place limit & market order
  const marketOrder = {
    instrument: "XBTUSD",
    quantity: 1,
    order_type: OrderType.Market,
    side: Side.Sell,
  }
  globe.placeOrder(marketOrder)

  const limitOrder = {
    instrument: "XBTUSD",
    quantity: 1,
    price: 57000.0,
    order_type: OrderType.Limit,
    side: Side.Sell,
  }
  globe.placeOrder(limitOrder)

  const stopMarketOrder = {
    instrument: "XBTUSD",
    quantity: 1,
    trigger_price: 56300.0,
    order_type: OrderType.StopMarket,
    side: Side.Buy,
  }
  globe.placeOrder(stopMarketOrder)

  const stopLimitOrder = {
    instrument: "XBTUSD",
    quantity: 1,
    price: 56400.0,
    trigger_price: 56300.0,
    order_type: OrderType.StopLimit,
    side: Side.Buy,
  }
  globe.placeOrder(stopLimitOrder)
}

;(async () => {
  try {
    await main()
  } catch (e) {
    // Handle errors
  }
})()
