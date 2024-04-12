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
  result = {} # The result of a trading iteration

  productInfo: dict[Symbol, ProductInfo] = {} # A dictionary of useful product info such as margin or position



  def run(self, state: TradingState):
    # Resets the results dictionary
    self.result = {}

    # Initialised productInfo if this is the first iteration
    if state.timestamp == 0:
      self.InitProductInfo() #TODO: replace placeholder position limits in InitProductInfo() with the actual position limits

    self.CheckMarketTrades(state) 
    
    print("--= Trading started! =--\n")
    
    # Loops through all the order depths for each product (currently "AMETHYSTS" and "STARFRUIT")
    for product in state.order_depths:
        
      #TODO: Use ctrl f to replace "PRODUCT#" with the name of the actual product
      if product == "PRODUCT1":
        self.DoPRODUCT1Trading(state)

      elif product == "PRODUCT2":
        self.DoPRODUCT2Trading(state)

    print("=--  Trading ended!  --=\n")

    traderData = "SAMPLE"

    conversions = 1

    return self.result, conversions, traderData



  def DoPRODUCT1Trading(self, state: TradingState):
    print("= PRODUCT1 =")
    product = "PRODUCT1"

    # A list of any orders made
    orders: List[Order] = []

    # The buy and sell orders
    orderDepth: OrderDepth = state.order_depths[product]

    # Loops through all the sell orders, sees if any are worth buying from
    for sellOrder in orderDepth.sell_orders:
      
      # Gets the price and size of the order
      askPrice = sellOrder
      askAmount = -orderDepth.sell_orders[sellOrder]
      
      if "Some condition":  # If...

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
    


  def DoPRODUCT2Trading(self, state: TradingState):
    print("= PRODUCT2 =")
    product = "PRODUCT2"

    # A list of any orders made
    orders: List[Order] = []

    # The buy and sell orders
    orderDepth: OrderDepth = state.order_depths[product]

    # Loops through all the sell orders, sees if any are worth buying from
    for sellOrder in orderDepth.sell_orders:
      
      # Gets the price and size of the order
      askPrice = sellOrder
      askAmount = -orderDepth.sell_orders[sellOrder]
      
      if "Some condition":  # If...

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
    PRODUCT1 = ProductInfo("SOMENUM")
    self.productInfo["PRODUCT1"] = PRODUCT1

    PRODUCT2 = ProductInfo("SOMENUM")
    self.productInfo["PRODUCT2"] = PRODUCT2