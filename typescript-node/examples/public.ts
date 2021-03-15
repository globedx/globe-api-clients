import { Globe, Channel } from "../src/globe"

const errorHandler = (err: any) => console.log(err)

const instrument = "XBTUSD"
const handle = (response: any) => console.log(response)

async function main() {
  const globe = new Globe(errorHandler)
  await globe.connect()
  console.log("Connected to websocket")

  // REST endpoints for price history data
  console.log(await globe.getHistoricMarketRates(instrument, "1m"))
  console.log(await globe.getHistoricIndexPriceRates(instrument, "1m"))

  // Subscribe to public channels
  globe.subscribe(Channel.indexPrice(instrument), handle)
  globe.subscribe(Channel.depth(instrument), handle)
  globe.subscribe(Channel.productList(), handle)
  globe.subscribe(Channel.productDetail(instrument), handle)
  globe.subscribe(Channel.trades(instrument), handle)
  globe.subscribe(Channel.marketOverview(instrument), handle)
  globe.subscribe(Channel.openInterest(instrument), handle)
  globe.subscribe(Channel.insuranceFund(instrument), handle)
  globe.subscribe(Channel.priceHistory(instrument, "1m"), handle)
}

;(async () => {
  try {
    await main()
  } catch (e) {
    // Handle errors
  }
})()
