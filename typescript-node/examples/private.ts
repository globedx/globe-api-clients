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
  const globe = new Globe(errorHandler)
  await globe.connect({ credentials: CREDENTIALS })
  console.log("Authenticated worked and connected to websocket")

  // Subscribe to private channels
  globe.subscribe(Channel.myMarketEvents(instrument), handle)
  globe.subscribe(Channel.myOpenOrders(instrument), handle)
  globe.subscribe(Channel.myAccountOverview(), handle)
  globe.subscribe(Channel.myPositions(), handle)

  // Place limit & market order
  const marketOrder = {
    instrument: "XBTUSD",
    quantity: 250,
    order_type: OrderType.Market,
    side: Side.Sell,
  }
  globe.placeOrder(marketOrder)

  const limitOrder = {
    instrument: "XBTUSD",
    quantity: 250,
    price: 9500.0,
    order_type: OrderType.Limit,
    side: Side.Buy,
  }
  globe.placeOrder(limitOrder)
}

;(async () => {
  try {
    await main()
  } catch (e) {
    // Handle errors
  }
})()
