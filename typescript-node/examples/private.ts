import {
  Globe,
  OrderType,
  Side,
  ApiCredentials,
  Channel,
  OpenOrder,
  OrderExecutionType,
} from "../src/globe"

const errorHandler = (err: any) => console.log(err)

// Add your own credentials
const credentials: ApiCredentials = {
  apiKey: "",
  secret: "",
  passphrase: "",
}

const instrument = "XBTUSD"

async function main() {
  console.log("Starting...")
  const globe = new Globe(errorHandler, { credentials })
  await globe.connect()
  console.log("Connected")

  // track orders in a map as they are created and removed
  const orders: Map<string, OpenOrder> = new Map()

  globe.subscribe(Channel.myMarketEvents(instrument), (response: any) => {
    console.log(response)
    if (response.data.event === "order-cancelled") {
      orders.delete(response.data.order_id)
    } else if (response.data.event === "rejected") {
      orders.delete(response.data.request_id)
    }
  })

  globe.subscribe(Channel.myOpenOrders(instrument), console.log)
  globe.subscribe(Channel.myAccountOverview(), console.log)

  // wait for the first index price message
  const index: number = await new Promise((resolve) => {
    globe.subscribe(Channel.indexPrice(instrument), (response: any) => {
      globe.unsubscribe(Channel.indexPrice(instrument))
      resolve(response.data.price)
    })
  })

  // add any orders that are from previous sessions
  const openOrdersResult = await globe.getOpenOrders(instrument)
  openOrdersResult.forEach((order: OpenOrder) => {
    orders.set(order.order_id, order)
  })

  // place some new orders
  for (let i = 0; i < 5; i++) {
    const order = {
      instrument,
      quantity: 1000,
      price: Math.round(index) - 10 + i,
      order_type: OrderType.Limit,
      side: Side.Buy,
    }
    const order_id = globe.placeOrder(order)
    const timestamp = new Date().getTime()
    // keep track of orders we have placed
    orders.set(order_id, {
      type: OrderExecutionType.Order,
      filled_quantity: 0,
      order_id,
      timestamp,
      ...order,
    })
  }

  // cancel all of our orders
  orders.forEach((order, order_id) => {
    globe.cancelOrder({ instrument, order_id })
    orders.delete(order_id)
  })
}

;(async () => {
  try {
    await main()
  } catch (e) {
    // Handle errors
  }
})()
