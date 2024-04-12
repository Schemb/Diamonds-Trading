#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

from datamodel import OrderDepth, Symbol, TradingState, Order
from typing import List
import numpy as np



# Contains the profit, position, and position limit of a product
class ProductInfo:
  def __init__(self, posLimit: int):
    self.margin: float = 0         # Variable to store the current profit/loss of the product
    self.amount: int = 0           # How much of this product is currently held (must be within the position limit)
    self.posLimit: int = posLimit  # The position limit of this product



class Trader:
  result = {}   # The result of a trading iteration

  productInfo: dict[Symbol, ProductInfo] = {} # A dictionary of useful product info such as margin or position

  starfruitBuyIn = [0, 5, 10] # should be changed to get good buy in rates relative to price

  long_prices_array = np.array([5044, 5043, 5044, 5049, 5048, 5047, 5044, 5043, 5043, 5046, 5046, 5047, 5044])

  short_prices_array = np.array([5046, 5047, 5044])

  sum = 0
  count = 0



  def run(self, state: TradingState):
    # Resets the results dictionary
    self.result = {}

    # Initialised productInfo if this is the first iteration
    if state.timestamp == 0:
      self.InitProductInfo()

    self.CheckMarketTrades(state)
    
    print("--= Trading started! =--\n")
    
    # Loops through all the order depths for each product (currently "AMETHYSTS" and "STARFRUIT")
    for product in state.order_depths:
        
      if product == "AMETHYSTS":
        self.DoAmethystTrading(state)

      elif product == "STARFRUIT":
        i = 0
        self.DoStarfruitTrading(state)

    print("=--  Trading ended!  --=\n")

    traderData = "SAMPLE"

    conversions = 1

    return self.result, conversions, traderData



  def DoAmethystTrading(self, state: TradingState):
    print("= AMETHYSTS =")
    product = "AMETHYSTS"

    # A list of any orders made
    orders: List[Order] = []

    # The buy and sell orders
    orderDepth: OrderDepth = state.order_depths[product]

    # The precalculated median of the amethyst price, used to determine when to buy/sell
    median = 10000


    # Loops through all the sell orders, only orders valued at 9998 should (can) be bought
    for sellOrder in orderDepth.sell_orders:
      
      # Gets the price and size of the order
      askPrice = sellOrder
      askAmount = -orderDepth.sell_orders[sellOrder]
      
      if int(askPrice) < median:  # If they are being sold less than the median

        # Determine the difference in price
        difference = median - askPrice

        # Don't buy if the order isn't value at 9998
        if difference != 2:
          continue

        # Determine how many should be bought, between the minimum of:
        #   - How many are being sold
        #   - How many it can buy without exceeding the position limit
        buyAmount = min(askAmount + 200, self.productInfo[product].posLimit - self.productInfo[product].amount)

        # Adjust stored amethyst variables based on how the order was executed
        self.productInfo[product].amount = self.productInfo[product].amount + buyAmount

        # Prints how many were bought, and at what value
        # print("\tBUY", str(buyAmount) + "x", askPrice)

        # Appends the buy to the orders list
        orders.append(Order(product, askPrice, buyAmount))

      # else:
      #   # Prints what the order was, even though it wasn't bought
      #   print("\tDIDN'T BUY (too expensive)", str(askAmount) + "x", askPrice)

    # Loops through all the buy orders, only orders valued at 10002 should (can) be sold
    for buyOrder in orderDepth.buy_orders:

      # Gets the asking price and the amount of the bid
      bidPrice = buyOrder
      bidAmount = orderDepth.buy_orders[buyOrder]

      if int(bidPrice) > median: # If they are paying above the median
        
        # Determine the difference in price
        difference = bidPrice - median

        # Don't buy if the order isn't value at 9998
        if difference != 2:
          continue

        # Determine how many should be sold, between the minimum of:
        #   - How many are being bought
        #   - How many it can sell without exceeding the position limit
        sellAmount = min(bidAmount + 200, self.productInfo[product].posLimit + self.productInfo[product].amount)

        # Adjust stored amethyst variables based on the order
        self.productInfo[product].amount = self.productInfo[product].amount - sellAmount

        # Prints how many were sold, and at what value
        # print("\tSELL", str(sellAmount) + "x", bidPrice)

        # Appends the sell to the orders list
        orders.append(Order(product, bidPrice, -sellAmount))

      # else:
      #   # Prints what the order was, even though nothing was sold
      #   print("\tDIDN'T SELL", str(bidAmount) + "x", bidPrice)

    # Adds the order to the results dictionary
    self.result[product] = orders
    


  def DoStarfruitTrading(self, state: TradingState):
    print("= STARFRUIT =")
    product = "STARFRUIT"

    # A list of any orders made
    orders: List[Order] = []

    # The buy and sell orders
    orderDepth: OrderDepth = state.order_depths[product]

    # Get averages from starting arrays
    longAverage = np.average(self.long_prices_array)
    shortAverage = np.average(self.short_prices_array)

    # Loops through all the sell orders
    for sellOrder in orderDepth.sell_orders:

      # Gets the price and size of the order
      askPrice = sellOrder
      askAmount = -orderDepth.sell_orders[sellOrder]

      if (state.timestamp) > 1300:
        for i in range(0,11):
          self.long_prices_array[i] = self.long_prices_array[(i + 1)]
        self.long_prices_array[12] = askPrice

        for i in range(0,1):
          self.short_prices_array[i] = self.short_prices_array[(i+1)]
        self.short_prices_array[2] = askPrice

      if longAverage > shortAverage and shortAverage >= askPrice:

        factor: int = 0
        buyInDifference = abs(longAverage - askPrice)

        if buyInDifference == 0:
          factor = 0
        elif buyInDifference > 0 and buyInDifference < 3:
          factor = 1
        elif buyInDifference >= 2:
          factor = 2

        # Determine how many should be bought, between the minimum of:
        #   - How many are being sold
        #   - How many it can buy without exceeding the position limit
        buyAmount = min(askAmount, self.productInfo[product].posLimit - self.productInfo[product].amount, self.starfruitBuyIn[factor])

        # Adjust stored amethyst variables based on how the order was executed
        self.productInfo[product].amount = self.productInfo[product].amount + buyAmount

        # Prints how many were bought, and at what value
        print("\tBUY", str(buyAmount) + "x", askPrice)

        # Appends the buy to the orders list
        orders.append(Order(product, askPrice, buyAmount))

      elif longAverage > shortAverage and shortAverage < askPrice:
        buyAmount = min(askAmount, self.productInfo[product].posLimit - self.productInfo[product].amount)

        # Adjust stored amethyst variables based on how the order was executed
        self.productInfo[product].amount = self.productInfo[product].amount + buyAmount

        # Prints how many were bought, and at what value
        print("\tBUY", str(buyAmount) + "x", askPrice)

        # Appends the buy to the orders list
        orders.append(Order(product, askPrice, buyAmount))
      


    # Loops through all the buy orders
    for buyOrder in orderDepth.buy_orders:

      # Gets the asking price and the amount of the bid
      bidPrice = buyOrder
      bidAmount = orderDepth.buy_orders[buyOrder]

      if (state.timestamp) > 1300:
        for i in range(0,11):
          self.long_prices_array[i] = self.long_prices_array[(i + 1)]
        self.long_prices_array[12] = bidPrice

        for i in range(0,1):
          self.short_prices_array[i] = self.short_prices_array[(i+1)]
        self.short_prices_array[2] = bidPrice
      

      if longAverage < shortAverage and shortAverage <= bidPrice:  # If they are being sold less than the median

        factor: int = 0
        buyInDifference = abs(bidPrice - longAverage)

        if buyInDifference == 0:
          factor = 0
        elif buyInDifference > 0 and buyInDifference < 3:
          factor = 1
        elif buyInDifference >= 2:
          factor = 2

        # Determine how many should be bought, between the minimum of:
        #   - How many are being sold
        #   - How many it can buy without exceeding the position limit
        sellAmount = min(bidAmount, self.productInfo[product].posLimit + self.productInfo[product].amount, self.starfruitBuyIn[factor])

        # Adjust stored amethyst variables based on how the order was executed
        self.productInfo[product].amount = self.productInfo[product].amount + bidAmount

        # Prints how many were bought, and at what value
        print("\tSELL", str(bidAmount) + "x", bidPrice)

        # Appends the buy to the orders list
        orders.append(Order(product, bidPrice, -sellAmount))

      elif longAverage < shortAverage and shortAverage > bidPrice:
        # Determine how many should be bought, between the minimum of:
        #   - How many are being sold
        #   - How many it can buy without exceeding the position limit
        sellAmount = min(bidAmount, self.productInfo[product].posLimit + self.productInfo[product].amount)

        # Adjust stored amethyst variables based on how the order was executed
        self.productInfo[product].amount = self.productInfo[product].amount + bidAmount

        # Prints how many were bought, and at what value
        print("\tSELL", str(bidAmount) + "x", bidPrice)

        # Appends the buy to the orders list
        orders.append(Order(product, bidPrice, -sellAmount))

    # Adds the orders to the results dictionary
    self.result[product] = orders

    

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
    amethyst = ProductInfo(20)
    self.productInfo["AMETHYSTS"] = amethyst

    starfruit = ProductInfo(20)
    self.productInfo["STARFRUIT"] = starfruit