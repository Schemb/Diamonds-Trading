from datamodel import OrderDepth, Symbol, TradingState, Order
from typing import List, Dict
import numpy as np



# Contains the profit, position, and position limit of a product
class ProductInfo:
  def __init__(self, posLimit: int):
    self.net_profit: float = 0         # Variable to store the current profit/loss of the product
    self.amount: int = 0           # How much of this product is currently held (must be within the position limit)
    self.posLimit: int = posLimit  # The position limit of this product



class Trader:
  result = {} # The result of a trading iteration

  productInfo: Dict[Symbol, ProductInfo] = {} # A dictionary of useful product info such as net_profit or position

  starfruitBuyIn = [0, 5, 10] # should be changed to get good buy in rates relative to price

  long_prices_array = np.array([5044, 5043, 5044, 5049, 5048, 5047, 5044, 5043, 5043, 5046, 5046, 5047, 5044])

  short_prices_array = np.array([5046, 5047, 5044])
  
  prevSunLight = [0, 0, 0]
  sunLightPeakTimeStamp = -1


  def run(self, state: TradingState):
    # Resets the results dictionary
    self.result = {}

    # Initialised productInfo if this is the first iteration
    if state.timestamp == 0:
      self.InitProductInfo()

    self.CheckMarketTrades(state) 
    
    print("--= Trading started! =--\n")
    
    orchidConversions = 0

    # Loops through all the order depths for each product (currently "AMETHYSTS" and "STARFRUIT")
    for product in state.order_depths:
        
      if product == "AMETHYSTS":
        self.DoAMETHYSTSTrading(state)

      elif product == "STARFRUIT":
        i = 0
        # self.DoSTARFRUITTrading(state)

      elif product == "ORCHIDS":
        orchidConversions = self.DoORCHIDSTrading(state)
        print(str(orchidConversions))

      elif product == "GIFT_BASKET":
        self.DoGIFT_BASKETTrading(state)

    print("=--  Trading ended!  --=\n")

    traderData = "SAMPLE"

    return self.result, orchidConversions, traderData



  def DoAMETHYSTSTrading(self, state: TradingState):
    print("= AMETHYSTS =")
    product = "AMETHYSTS"

    # A list of any orders made
    orders: List[Order] = []

    maxBuy = self.productInfo[product].posLimit - self.productInfo[product].amount
    maxSell = self.productInfo[product].posLimit + self.productInfo[product].amount
    
    # Appends the buy to the orders list
    orders.append(Order(product, 9998, maxBuy))

    # Appends the sell to the orders list
    orders.append(Order(product, 10002, -maxSell))

    # Adds the order to the results dictionary
    self.result[product] = orders
    


  # The price shown on starfruit graph
  graphPrice = []

  def DoSTARFRUITTrading(self, state: TradingState):
    print("= STARFRUIT =")
    product = "STARFRUIT"

    # Damo's equation
    totalMarketPrice = 0
    al2 = totalMarketPrice
    zt = 0 # zt = sum(z(k-i))+al
    
    print(totalMarketPrice)

    # Get t
    # Checks to make sure that trades have been made before (other wise the own_trades dict is empty)
    checkTrades = True
    try:
      state.market_trades[product]
    except:
      checkTrades = False
    
    if checkTrades:
      for trade in state.market_trades[product]:
        totalMarketPrice = totalMarketPrice + trade.price
      totalMarketPrice = totalMarketPrice / len(state.market_trades[product])
      self.graphPrice.append(totalMarketPrice)
      
      al1 = totalMarketPrice
    if len(self.graphPrice) > 2:
      for prices in self.graphPrice:
        zt = zt + (self.graphPrice[int(prices)-1] - self.graphPrice[int(prices)-2])
        predictedPrice = zt + self.graphPrice[state.timestamp/100 - 1]
    else:
      return
        

    # A list of any orders made
    orders: List[Order] = []

    # The buy and sell orders
    orderDepth: OrderDepth = state.order_depths[product]

    # here

    # Loops through all the sell orders, sees if any are worth buying from
    for sellOrder in orderDepth.sell_orders:

      # Gets the price and size of the order
      askPrice = sellOrder
      askAmount = -orderDepth.sell_orders[sellOrder]

      if predictedPrice < sellOrder:  # If...
        #buy
        askAmount = 3
        # greater than
      elif predictedPrice > sellOrder:  #sell

        sellAmount = 3
        
        # Determine how many should be bought, between the minimum of:
        #   - How many are being sold
        #   - How many it can buy without exceeding the position limit
        buyAmount = min(askAmount, 
                        self.productInfo[product].posLimit - self.productInfo[product].amount)

        # Adjust how many products are being held on how the order was executed
        self.productInfo[product].amount = self.productInfo[product].amount + buyAmount

        # Prints how many were were worth buying, and at what value
        print("\tBUY:", str(buyAmount) + "x", askPrice)

        # Appends the buy to the orders list
        orders.append(Order(product, askPrice, buyAmount))

    # Loops through all the buy orders, sees if any are worth selling to
    for buyOrder in orderDepth.buy_orders:

      # Gets the asking price and the amount of the bid
      bidPrice = buyOrder
      bidAmount = orderDepth.buy_orders[buyOrder]

      if "Some condition":  # If...

        # Determine how many should be sold, between the minimum of:
        #   - How many are being bought
        #   - How many it can sell without exceeding the position limit
        sellAmount = min(bidAmount, 
                         self.productInfo[product].posLimit + self.productInfo[product].amount)

        # Adjust how many products are being held on how the order was executed
        self.productInfo[product].amount = self.productInfo[product].amount - sellAmount

        # Prints how many were put on sale, and at what value
        print("\tSELL", str(sellAmount) + "x", bidPrice)

        # Appends the sell to the orders list
        orders.append(Order(product, bidPrice, -sellAmount))

    # Adds the order to the results dictionary
    self.result[product] = orders


  def DoORCHIDSTrading(self, state: TradingState):
    print("= ORCHIDS =")
    product = "ORCHIDS"

    orchidInfo = state.observations.conversionObservations[product]

    sunlight =      orchidInfo.sunlight
    humidity =      orchidInfo.humidity
    southAskPrice = orchidInfo.askPrice
    southBidPrice = orchidInfo.bidPrice
    exportFees =    orchidInfo.exportTariff
    importFees =    orchidInfo.importTariff
    transportFees = orchidInfo.transportFees

    production_from_humidity = 100
    if humidity < 60:
      production_from_humidity = (2 / 5) * humidity + 76
    if humidity > 80:
      production_from_humidity = - (2 / 5) * humidity + 132

    #predicted_price trading within our own market
    predicted_price = 1998.39 + 0.0524167 * sunlight - 10.5565 * production_from_humidity + 500
    print("The predicted price for Orchids is:", predicted_price)

    #price when we buy/import from southern archepelago
    import_price=southAskPrice+importFees+transportFees

    #price when we sell/export to the southern archepelago
    export_revenue=southBidPrice-exportFees-transportFees

    # ------------= Local Market Trades =------------
    # A list of any orders made
    orders: List[Order] = []

    # The buy and sell orders
    orderDepth: OrderDepth = state.order_depths[product]

    """
    for each product, 2 dictionaries, one buy, one sell

    For example, if the buy_orders property would look like this for a certain product {9: 5, 10: 4} 
    That would mean that there is a total buy order quantity of 5 at the price level of 9, and a total
    buy order quantity of 4 at a price level of 10.

    Players should note that in the sell_orders property, the quantities specified will be negative. 
    E.g., {12: -3, 11: -2} would mean that the aggregated sell order volume at price level 12 is 3, 
    and 2 at price level 11.
    """

    lowest_ask_price = -1
    highest_ask_price = -1

    quantity_sell_orders = 0

    # Loops through all the sell orders in this iteration of this product, sees if any are worth buying from
    for sellOrder in orderDepth.sell_orders: #goes over the key of the dictionary
      
      # Gets the price and size of the order
      askPrice = sellOrder #key
      askAmount = -orderDepth.sell_orders[sellOrder] #values
      quantity_sell_orders = quantity_sell_orders + askAmount

      if lowest_ask_price == -1 or lowest_ask_price > askPrice:
        lowest_ask_price = askPrice
      if highest_ask_price < askPrice:
        highest_ask_price = askPrice
      
      if askPrice < predicted_price:  # If they are asking for less than we think it will be worth

        # Determine how many should be bought, between the minimum of:
        #   - How many are being sold
        #   - How many it can buy without exceeding the position limit
        buyAmount = min(askAmount, 
                        self.productInfo[product].posLimit - self.productInfo[product].amount)

        # Adjust how many products are being held on how the order was executed
        self.productInfo[product].amount = self.productInfo[product].amount + buyAmount

        # Prints how many were were worth buying, and at what value
        print("\tBUY:", str(buyAmount) + "x", askPrice)

        # Appends the buy to the orders list
        orders.append(Order(product, askPrice, buyAmount))

    lowest_bid_price = 0
    highest_bid_price = 0
    quantity_buy_orders = 0

    # Loops through all the buy orders, sees if any are worth selling to
    for buyOrder in orderDepth.buy_orders:

      # Gets the asking price and the amount of the bid
      bidPrice = buyOrder
      bidAmount = orderDepth.buy_orders[buyOrder]
      quantity_buy_orders = quantity_buy_orders + bidAmount

      if lowest_bid_price == -1 or lowest_bid_price > bidPrice:
        lowest_bid_price = bidPrice
      if highest_bid_price < bidPrice:
        highest_bid_price = bidPrice

      if bidPrice > predicted_price:  # If they are willing to buy for more then we think they will be worth in the future

        # Determine how many should be sold, between the minimum of:
        #   - How many are being bought
        #   - How many it can sell without exceeding the position limit
        sellAmount = min(bidAmount, 
                         self.productInfo[product].posLimit + self.productInfo[product].amount)

        # Adjust how many products are being held on how the order was executed
        self.productInfo[product].amount = self.productInfo[product].amount - sellAmount

        # Prints how many were put on sale, and at what value
        print("\tSELL", str(sellAmount) + "x", bidPrice)

        # Appends the sell to the orders list
        orders.append(Order(product, bidPrice, -sellAmount))
    
    #----------=Determine whether we should buy or sell=-----------
    conversions = self.productInfo[product].amount
    
    #Compare the lowest sell/ask price of our own market and the import price of southern market
    # lowest_ask_price #lowest_sell_order
    # if (import_price<lowest_ask_price) and (highest_ask_price<predicted_price):
    #     #we decide to import from southern market
    #     quantity_import=quantity_buy_orders
    #     conversions=+quantity_import #quantity our market want to buy in this iteration
    #     # =quantity_import

    # #Lowest sell price of our own market
    # highest_bid_price #highest_buy_order
    # if (export_revenue>highest_bid_price) and (predicted_price<lowest_bid_price):
    #     #we decide to sell from southern market
    #     quantity_export=quantity_sell_orders
    #     conversions=-quantity_export #quantity our market want to sell in this iteration
    #     self.num_stored_orchids=-quantity_export
    
    #if the number of orchids we hold is too great we should also export to the southern market
    #DO IT LATER
  
    return conversions

  highestBuySpread = 0
  lowestBuySpread = -1
  
  highestSellSpread = 0
  lowestSellSpread = -1

  def DoGIFT_BASKETTrading(self, state: TradingState):
    print("= GIFT_BASKET =")
    lowestAskPrices: Dict[str, int] = {"GIFT_BASKET": -1, "STRAWBERRIES": -1, "CHOCOLATE": -1, "ROSES": -1}
    highestBidPrices: Dict[str, int] = {"GIFT_BASKET": 0, "STRAWBERRIES": 0, "CHOCOLATE": 0, "ROSES": 0}
    baskets = "GIFT_BASKET"
    strawberries = "STRAWBERRIES"
    chocolate = "CHOCOLATE"
    roses = "ROSES"

    # A list of any orders made
    orders: Dict[str, List[Order]] = {baskets: [], chocolate: [], strawberries: [], roses: []}


    # ------------------------ BUYING ------------------------
    for product in lowestAskPrices:
      orderDepth: OrderDepth = state.order_depths[product]
      # Loops through all the sell orders in this iteration of this product, sees if any are worth buying from
      for sellOrder in orderDepth.sell_orders: #goes over the key of the dictionary
        
        # Gets the price and size of the order
        askPrice = sellOrder #key
        # askAmount = -orderDepth.sell_orders[sellOrder] #values

        if lowestAskPrices[product] == -1 or lowestAskPrices[product] > askPrice:
          lowestAskPrices[product] = askPrice

    # If spread is: positive, then baskets are more expensive to buy compared to its components
    #               negative, then baskets are cheaper to buy compared to its components
    buySpread = lowestAskPrices[baskets] - (4 * lowestAskPrices[chocolate] + 6 * lowestAskPrices[strawberries] + lowestAskPrices[roses])

    if buySpread > self.highestBuySpread:
      self.highestBuySpread = buySpread
    if buySpread < self.lowestBuySpread or self.lowestBuySpread == -1:
      self.lowestBuySpread = buySpread

    # if buySpread >= 400: # buy components
    #     # Prints how many were were worth buying, and at what value
    #     print("\tBUY COMPONENTS:", chocolate, lowestAskPrices[chocolate], strawberries, lowestAskPrices[strawberries], roses, lowestAskPrices[roses])

    #     # Appends the buy to the orders list
    #     orders[chocolate].append(Order(chocolate, lowestAskPrices[chocolate], 4))
    #     orders[strawberries].append(Order(strawberries, lowestAskPrices[strawberries], 6))
    #     orders[roses].append(Order(roses, lowestAskPrices[roses], 1))

    if buySpread < 400: # buy basket
        # Prints how many were were worth buying, and at what value
        print("\tBUY BASKET:", baskets, lowestAskPrices[baskets])

        # Appends the buy to the orders list
        orders[baskets].append(Order(baskets, lowestAskPrices[baskets], 1))


    # ------------------------ SELLING ------------------------
    for product in highestBidPrices:
      orderDepth: OrderDepth = state.order_depths[product]
      # Loops through all the sell orders in this iteration of this product, sees if any are worth buying from
      for buyOrder in orderDepth.buy_orders: #goes over the key of the dictionary
        
        # Gets the price and size of the order
        bidPrice = buyOrder #key
        # askAmount = -orderDepth.sell_orders[sellOrder] #values

        if highestBidPrices[product] < bidPrice:
          highestBidPrices[product] = bidPrice

    # If spread is: positive, then baskets are selling for MORE compared to its components
    #               negative, then baskets are selling for LESS compared to its components
    sellSpread = highestBidPrices[baskets] - (4 * highestBidPrices[chocolate] + 6 * highestBidPrices[strawberries] + highestBidPrices[roses])

    if sellSpread > self.highestSellSpread:
      self.highestSellSpread = sellSpread
    if sellSpread < self.lowestSellSpread or self.lowestSellSpread == -1:
      self.lowestSellSpread = sellSpread

    # if sellSpread <= 400: # buy components
    #     # Prints how many were were worth buying, and at what value
    #     print("\tSELL COMPONENTS:", chocolate, highestBidPrices[chocolate], strawberries, highestBidPrices[strawberries], roses, highestBidPrices[roses])

    #     # Appends the buy to the orders list
    #     orders[chocolate].append(Order(chocolate, highestBidPrices[chocolate], -4))
    #     orders[strawberries].append(Order(strawberries, highestBidPrices[strawberries], -6))
    #     orders[roses].append(Order(roses, highestBidPrices[roses], -1))

    if sellSpread > 400: # buy basket
        # Prints how many were were worth buying, and at what value
        print("\tSELL BASKET:", baskets, highestBidPrices[baskets])

        # Appends the buy to the orders list
        orders[baskets].append(Order(baskets, highestBidPrices[baskets], -1))

    # print("SPREADS:", buySpread, self.highestBuySpread, self.lowestBuySpread, sellSpread, self.highestSellSpread, self.lowestSellSpread)

    # Adds the order to the results dictionary
    self.result[baskets] = orders[baskets]


  # This function checks all the market trades from the previous iteration, 
  # updating stored variables to reflect profits and positions
  def CheckMarketTrades(self, state: TradingState):

    print("The results of the previous trading period!")

    # Loops through all the products
    for symbol in self.productInfo:

      # Updates the position of the product held if available
      try:
        self.productInfo[symbol].amount = state.position[symbol]
      except:
        self.productInfo[symbol].amount = 0

      # Checks to make sure that trades have been made before (other wise the own_trades dict is empty)
      try:
        state.own_trades[symbol]
      except:
        continue

      # Loops through all the trades for this product
      for trade in state.own_trades[symbol]:

        # Checks to make sure that the trade is current and not from past iterations
        if trade.timestamp != state.timestamp - 100:
          continue

        print("=", symbol, "=")

        # If the algorithm was the buyer of the order
        if trade.buyer == "SUBMISSION":

          # Adjusts net_profit accordingly
          self.productInfo[symbol].net_profit = self.productInfo[symbol].net_profit - trade.price * trade.quantity

          # Prints how many were bought, and at what value
          print("\tBOUGHT", str(trade.quantity) + "x", trade.price)

        # If the algorithm was the seller of the order
        if trade.seller == "SUBMISSION":

          # Adjusts net_profit accordingly
          self.productInfo[symbol].net_profit = self.productInfo[symbol].net_profit + trade.price * trade.quantity

          # Prints how many were sold, and at what value
          print("\tSOLD", str(trade.quantity) + "x", trade.price)
          
      # Prints of the current trading attributes relating to the product
      print("\tCurrently holding", str(self.productInfo[symbol].amount), symbol, "!")
      print("\tCurrent profit net_profit for", symbol, "is:", str(self.productInfo[symbol].net_profit), '\n')



  # Initialises the productInfo variable
  def InitProductInfo(self):
    AMETHYSTS = ProductInfo(20)
    self.productInfo["AMETHYSTS"] = AMETHYSTS

    STARFRUIT = ProductInfo(20)
    self.productInfo["STARFRUIT"] = STARFRUIT

    ORCHIDS = ProductInfo(100)
    self.productInfo["ORCHIDS"] = ORCHIDS

    CHOCOLATE = ProductInfo(250)
    self.productInfo["CHOCOLATE"] = CHOCOLATE

    STRAWBERRIES = ProductInfo(350)
    self.productInfo["STRAWBERRIES"] = STRAWBERRIES

    ROSES = ProductInfo(60)
    self.productInfo["ROSES"] = ROSES

    GIFT_BASKET = ProductInfo(60)
    self.productInfo["GIFT_BASKET"] = GIFT_BASKET
