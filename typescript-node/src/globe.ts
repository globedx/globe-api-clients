import Websocket from "ws"
import crypto from "crypto"
import fetch from "node-fetch"

export enum Side {
  Buy = "buy",
  Sell = "sell",
}

export type ResolutionType =
  | "1m"
  | "3m"
  | "5m"
  | "15m"
  | "30m"
  | "1h"
  | "2h"
  | "4h"
  | "6h"
  | "12h"
  | "1d"
  | "3d"
  | "1w"

export enum OrderType {
  Limit = "limit",
  PostOnly = "post_only",
  Market = "market",
}

export type Order = {
  instrument: string
  order_type: OrderType
  quantity: number
  price?: number
  side: Side
  order_id?: string
}

export const Channel = {
  /**
   * Subscription message for the market depth channel.
   * Responses contain arrays of the best long and short prices for the given instrument.
   *
   * This channel does not require authentication.
   */
  depth: (instrument: string) => {
    return { instrument, channel: "depth" }
  },

  /**
   * Subscription message for the index price channel.
   * Responses contain the current index price for the given instrument.
   *
   * This channel does not require authentication.
   */
  indexPrice: (instrument: string) => {
    return { instrument, channel: "index-price" }
  },

  /**
   * Subscription message for the insurance fund channel.
   * Responses contain the current balance of the insurance fund.
   *
   * This channel does not require authentication.
   */
  insuranceFund: (instrument: string) => {
    return { instrument, channel: "insurance-fund" }
  },

  /**
   * Subscription message for product list channel.
   * Responses contain an array of the current available products.
   *
   * This channel does not require authentication.
   */
  productList: () => {
    return { channel: "product-list" }
  },

  /**
   * Subscription message for the product details channel.
   * Responses contain objects with details of the contract for the given instrument,
   * including fees and funding period.
   *
   * This channel does not require authentication.
   */
  productDetail: (instrument: string) => {
    return { instrument, channel: "product-detail" }
  },

  /**
   * Subscription message for the recent trades channel.
   * Responses contain an array of the 100 most recent trades for the given instrument.
   *
   * This channel does not require authentication.
   */
  trades: (instrument: string) => {
    return { instrument, channel: "trades" }
  },

  /**
   * Subscription message for the market overview channel.
   * Responses are objects containing 24 hour trading volume, price change and funding rate.
   *
   * This channel does not require authentication.
   */
  marketOverview: (instrument: string) => {
    return { instrument, channel: "market-overview" }
  },

  /**
   * Subscription message for the price history channel.
   * Responses are objects containing candle metrics (high, low, open, close, time and volume)
   *
   * This channel does not require authentication.
   */
  priceHistory: (instrument: string, resolution: ResolutionType) => {
    return { instrument, resolution, channel: "market-overview" }
  },

  /**
   * Subscription message for the market open interest channel.
   * Responses are the number of outstanding contracts for the given instrument.
   *
   * This channel does not require authentication.
   */
  openInterest: (instrument: string) => {
    return { instrument, channel: "open-interest" }
  },

  /**
   * Subscription message for the market events channel.
   * Responses are market data messages for the current user, including order confirmations, rejections and trades.
   *
   * This channel is personalized per trader and requires authentication.
   */
  myMarketEvents: (instrument: string) => {
    return { instrument, channel: "my-market-events" }
  },

  /**
   * Subscription message for the account overview channel.
   * Responses contain account information for the current user, including balances, margin limits and PnL.
   *
   * This channel is personalized per trader and requires authentication.
   */
  myAccountOverview: () => {
    return { channel: "my-account-overview" }
  },

  /**
   * Subscription message for the open orders channel.
   * Responses are updates to your open orders for the specified instrument.
   * The updates are objects whose keys are order ids. The values are either the order details or `null`
   * to indicate the order has been removed (by being cancelled or filled).
   *
   * This channel is personalized per trader and requires authentication.
   */
  myOpenOrders: (instrument: string) => {
    return { instrument, channel: "my-orders" }
  },

  /**
   * Subscription message for the positions channel.
   * Responses are objects whose keys are instrument symbols
   * and whose values contain the quantity and average entry price for the position.
   *
   * This channel is personalized per trader and requires authentication.
   */
  myPositions: () => {
    return { channel: "my-positions" }
  },
}

// Api types

export type ApiCredentials = {
  secret: string
  apiKey?: string
  passphrase: string
}

type Fields = { [key: string]: any }
type ReceiveHandler = (event: Websocket.Data) => void
type ConnectionOptions = { credentials?: ApiCredentials }
type Message = { path: string; method: string; body: string }
type ErrorHandler = (event: Websocket.Data) => void

const sign = (request: string, credentials: ApiCredentials) => {
  const nonce = new Date().getTime()
  const hmac = crypto.createHmac(
    "sha256",
    Buffer.from(credentials.secret, "base64"),
  )
  const messageText = `${nonce}${request}`

  return {
    passphrase: credentials.passphrase,
    nonce,
    signature: hmac.update(messageText).digest("base64"),
    api_key: credentials.apiKey,
  }
}

const signMessage = (msg: Message, credentials: ApiCredentials) =>
  sign(`${msg.method}${msg.path}${msg.body}`, credentials)

const authHeaders = (request: Message, credentials: ApiCredentials) => {
  const signed = signMessage(request, credentials)
  return {
    "X-Access-Key": `${signed.api_key}`,
    "X-Access-Signature": signed.signature,
    "X-Access-Nonce": `${signed.nonce}`,
    "X-Access-Passphrase": signed.passphrase,
  }
}

// Time

const withTimeout = <T>(
  timeout: number,
  promise: Promise<T>,
  message: string,
  cleanup?: () => void,
): Promise<T> =>
  Promise.race([
    promise,
    new Promise<T>((resolve, reject) => {
      setTimeout(() => {
        if (cleanup) {
          cleanup()
        }
        reject(new Error(`Timeout after ${timeout}ms. Context: ${message}`))
      }, timeout)
    }),
  ])

// Client

export class Globe {
  private error: ErrorHandler
  private ws?: Websocket
  private path: string
  private host: string
  private httpApi: string
  private connectionTimeout: number
  private receiveHandlers: Record<string, ReceiveHandler> = {}

  constructor(error: ErrorHandler) {
    this.error = error
    this.path = "/api/v1/ws"
    this.host = "wss://globedx.com"
    this.httpApi = "http://www.globedx.com/api/v1"
    this.connectionTimeout = 30000
  }

  async connect(options?: ConnectionOptions): Promise<Globe> {
    const path = this.path
    const headers =
      options?.credentials &&
      authHeaders({ path, method: "GET", body: "" }, options.credentials)
    this.ws = new Websocket(this.host + this.path, { headers })

    this.ws.onmessage = (message) => {
      const data = JSON.parse(message.data as string)

      if (data.subscription) {
        if (this.receiveHandlers[data.subscription.channel]) {
          this.receiveHandlers[data.subscription.channel](data)
        } else if (
          data.subscription.channel === "my-orders" &&
          this.receiveHandlers[
            data.subscription.channel + "-" + data.subscription.instrument
          ]
        ) {
          this.receiveHandlers[
            data.subscription.channel + "-" + data.subscription.instrument
          ](data)
        }
      } else if (data.error) {
        this.error(data)
      }
    }

    if (this.ws.readyState && Websocket.OPEN) {
      return Promise.resolve(this)
    }

    return withTimeout(
      this.connectionTimeout,
      new Promise<Globe>((resolve, reject) => {
        if (this.ws) {
          this.ws.onerror = (error) => {
            reject(error)
          }

          this.ws.onopen = () => {
            resolve(this)
          }
        } else {
          reject(new Error("Error while creating the Websocket"))
        }
      }),
      `Connecting to '${this.path}'`,
    )
  }

  private addReceiveHandler(channel: string, handle: ReceiveHandler) {
    this.receiveHandlers[channel] = handle
  }

  private send(message: Fields) {
    if (!this.ws) {
      throw new Error("Socket not connected")
    }

    this.ws.send(JSON.stringify(message))
  }

  subscribe(
    details: { instrument?: string; channel: string },
    handle: ReceiveHandler,
  ) {
    this.send({
      command: "subscribe",
      ...details,
    })
    if (details.channel === "my-orders") {
      this.addReceiveHandler(details.channel + "-" + details.instrument, handle)
    } else {
      this.addReceiveHandler(details.channel, handle)
    }
  }

  unsubscribe(channel: string, subscription?: Fields) {
    this.send({
      command: "unsubscribe",
      channel,
      ...subscription,
    })

    // Need to remove the handle here as well
  }

  close() {
    if (!this.ws) {
      console.warn("Socket not connected")
      return
    }

    if (this.ws.readyState === Websocket.OPEN) {
      this.ws.terminate()
    }
  }

  // Public REST

  async getHistoricMarketRates(
    instrument: string,
    resolution: ResolutionType,
  ): Promise<any> {
    const endpoint =
      this.httpApi + `/history/${instrument}/candles/${resolution}`
    return fetch(endpoint)
      .then((res) => res.text())
      .then((text) => JSON.parse(text))
  }

  async getHistoricIndexPriceRates(
    instrument: string,
    resolution: ResolutionType,
  ): Promise<any> {
    const endpoint =
      this.httpApi + `/history/index-price/${instrument}/candles/${resolution}`
    return fetch(endpoint)
      .then((res) => res.text())
      .then((text) => JSON.parse(text))
  }

  // Private methods (Requires authentication with an API key)

  placeOrder(order: Partial<Order>) {
    this.send({
      command: "place-order",
      ...order,
    })
  }

  cancelOrder(
    instrument: string,
    order_id: string,
    cancel_id?: string,
    new_quantity?: number,
  ) {
    this.send({
      command: "cancel-order",
      instrument,
      order_id,
      cancel_id,
      new_quantity,
    })
  }

  stopOrder(trigger: number, order: Order) {
    this.send({
      command: "stop-order",
      trigger,
      order,
    })
  }

  cancelStopOrder(
    trigger: number,
    instrument: string,
    order_id: string,
    cancel_id?: string,
  ) {
    this.send({
      command: "cancel-stop-order",
      instrument,
      order_id,
      cancel_id,
    })
  }
}
