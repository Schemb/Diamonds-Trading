# git acces token: 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

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

  productInfo: Dict[Symbol, ProductInfo] = {} # A dictionary of useful product info such as margin or position

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
        self.DoSTARFRUITTrading(state)

      elif product == "ORCHIDS":
        orchidConversions = self.DoORCHIDSTrading(state)

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
    if self.graphPrice > 1:
      for prices in self.graphPrice:
        zt = zt + (self.graphPrice[prices-1] - self.graphPrice[prices-2])
        predictedPrice = zt + self.graphPrice[state.timestamp/100 - 1]
        

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


  num_stored_orchids = 0

  def DoORCHIDSTrading(self, state: TradingState):
    print("= ORCHIDS =")
    product = "ORCHIDS"

    sunlight = state.observations.conversionObservations[product].sunlight
    humidity = state.observations.conversionObservations[product].humidity
    southAskPrice = state.observations.conversionObservations[product].askPrice
    southBidPrice = state.observations.conversionObservations[product].bidPrice
    exportFees = state.observations.conversionObservations[product].exportTariff
    importFees = state.observations.conversionObservations[product].importTariff
    transportFees = state.observations.conversionObservations[product].transportFees

    production_from_humidity = 100
    if humidity < 60:
      production_from_humidity = (2 / 5) * humidity + 76
    if humidity > 80:
      production_from_humidity = - (2 / 5) * humidity + 132

    #predicted_price trading within our own market
    predicted_price = 1998.39 + 0.0524167 * sunlight - 10.5565 * production_from_humidity

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
                        self.productInfo[product].posLimit - self.productInfo[product].amount,
                        self.num_stored_orchids)

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
                         self.productInfo[product].posLimit + self.productInfo[product].amount,
                        self.num_stored_orchids)

        # Adjust how many products are being held on how the order was executed
        self.productInfo[product].amount = self.productInfo[product].amount - sellAmount

        # Prints how many were put on sale, and at what value
        print("\tSELL", str(sellAmount) + "x", bidPrice)

        # Appends the sell to the orders list
        orders.append(Order(product, bidPrice, -sellAmount))
    
    #----------=Determine whether we should buy or sell=-----------
    conversions = 0
    
    #Compare the lowest sell/ask price of our own market and the import price of southern market
    lowest_ask_price #lowest_sell_order
    if (import_price<lowest_ask_price) and (highest_ask_price<predicted_price):
        #we decide to import from southern market
        quantity_import=quantity_buy_orders
        conversions=+quantity_import #quantity our market want to buy in this iteration
        num_stored_orchids=quantity_import

    #Lowest sell price of our own market
    highest_bid_price #highest_buy_order
    if (export_revenue>highest_bid_price) and (predicted_price<lowest_bid_price):
        #we decide to sell from southern market
        quantity_export=quantity_sell_orders
        conversions=-quantity_export #quantity our market want to sell in this iteration
        num_stored_orchids=-quantity_export
    
    #if the number of orchids we hold is too great we should also export to the southern market
    #DO IT LATER
  
    return conversions



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

          # Adjusts margin accordingly
          self.productInfo[symbol].margin = self.productInfo[symbol].margin - trade.price * trade.quantity

          # Prints how many were bought, and at what value
          print("\tBOUGHT", str(trade.quantity) + "x", trade.price)

        # If the algorithm was the seller of the order
        if trade.seller == "SUBMISSION":

          # Adjusts margin accordingly
          self.productInfo[symbol].margin = self.productInfo[symbol].margin + trade.price * trade.quantity

          # Prints how many were sold, and at what value
          print("\tSOLD", str(trade.quantity) + "x", trade.price)
          
      # Prints of the current trading attributes relating to the product
      print("\tCurrently holding", str(self.productInfo[symbol].amount), symbol, "!")
      print("\tCurrent profit margin for", symbol, "is:", str(self.productInfo[symbol].margin), '\n')



  # Initialises the productInfo variable
  def InitProductInfo(self):
    AMETHYSTS = ProductInfo(20)
    self.productInfo["AMETHYSTS"] = AMETHYSTS

    STARFRUIT = ProductInfo(20)
    self.productInfo["STARFRUIT"] = STARFRUIT

    ORCHIDS = ProductInfo(100)
    self.productInfo["ORCHIDS"] = ORCHIDS