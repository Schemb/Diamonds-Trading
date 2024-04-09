from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string

class Trader:
  result = {}   # The result of a trading iteration

  amethystMargin = 0      # Variable to store the current profit/loss of amethyst
  amethystAmount = 0      # The number of amethyst that is currently held (must be within the position limit)
  amethystPosLimit = 20   # The position limits for amethyst 

  starfruitMargin = 0     # Variable to store the current profit/loss of starfruit
  starfruitAmount = 0     # The number of starfruit that is currently held (must be within the position limit)
  starfruitPosLimit = 0   # The position limits for starfruit 

  def run(self, state: TradingState):
    # Resets the results dictionary
    self.result = {}
    
    print("--= Trading started! =--\n")
    
    # Loops through all the order depths for each product (currently "AMETHYSTS" and "STARFRUIT")
    for product in state.order_depths:
        
      if product == "AMETHYSTS":
        self.DoAmethystTrading(self, product, state)

      elif product == "STARFRUIT":
        self.DoStarfruitTrading(self, product, state)

    print("=--  Trading ended!  --=\n")

    traderData = "SAMPLE"

    conversions = 1

    return self.result, conversions, traderData

  def DoAmethystTrading(self, product, state: TradingState):
    print("=", product, "=")

    # A list of any orders made
    orders: List[Order] = []

    # The precalculated median of the amethyst price, used to determine when to buy/sell
    median = 10000

    # Gets the buy and sell order depths for amethyst
    order_depth: OrderDepth = state.order_depths[product]

    # Loops through all the sell orders
    for sellOrder in order_depth.sell_orders:
      
      # Gets the price and size of the order
      askPrice = sellOrder
      askAmount = order_depth.sell_orders[sellOrder]
      
      if int(askPrice) < median:  # If they are being sold less than the median

        # Adjust stored amethyst variables based on the order
        self.amethystMargin = self.amethystMargin + (askAmount * askPrice)
        self.amethystAmount = self.amethystAmount - askAmount

        # Prints how many were bought, and at what value
        print("\tBUY", str(-askAmount) + "x", askPrice)

        # Appends the buy to the orders list
        orders.append(Order(product, askPrice, -askAmount))

      else:
        # Prints what the order was, even though it wasn't bought
        print("\tDIDN'T BUY", str(-askAmount) + "x", askPrice)

    print() # Prints a newline for formatting (only works in local testing)

    # Loops through all the buy orders
    for buyOrder in order_depth.buy_orders:

      # Gets the asking price and the amount of the bid
      bidPrice = buyOrder
      bidAmount = order_depth.buy_orders[buyOrder]

      if int(bidPrice) > median: # If they are paying above the median

        # Adjust stored amethyst variables based on the order
        self.amethystMargin = self.amethystMargin + (bidAmount * bidPrice)
        self.amethystAmount = self.amethystAmount - bidAmount

        # Prints how many were sold, and at what value
        print("\tSELL", str(bidAmount) + "x", bidPrice)

        # Appends the sell to the orders list
        orders.append(Order(product, bidPrice, -bidAmount))

      else:
        # Prints what the order was, even though nothing was sold
        print("\tDIDN'T SELL", str(bidAmount) + "x", bidPrice)
    
    print() # Prints a newline for formatting (only works in local testing)

    # Adds the order to the results dictionary
    self.result[product] = orders
    
    # Prints of the current trading attributes relating to amethst
    print("\tCurrently holding", str(self.amethystAmount), "amethyst(s)!")
    print("\tCurrent profit margin for amethyst is:", str(self.amethystMargin), '\n')
    
  def DoStarfruitTrading(self, product, state: TradingState):
    print("=", product, "=")

    # A list of any orders made
    orders: List[Order] = []

    # Gets the buy and sell order depths for starfruit
    order_depth: OrderDepth = state.order_depths[product]

    # Loops through all the sell orders
    for sellOrder in order_depth.sell_orders:
      
      # Gets the price and size of the order
      askPrice = sellOrder
      askAmount = order_depth.sell_orders[sellOrder]

    # print() # Prints a newline for formatting (only works in local testing)

    # Loops through all the buy orders
    for buyOrder in order_depth.buy_orders:

      # Gets the asking price and the amount of the bid
      bidPrice = buyOrder
      bidAmount = order_depth.buy_orders[buyOrder]
    
    # print() # Prints a newline for formatting (only works in local testing)

    # Adds the order to the results dictionary
    self.result[product] = orders
    
    # Prints of the current trading attributes relating to amethst
    print("\tCurrently holding", str(self.starfruitAmount), "starfruit!")
    print("\tCurrent profit margin for starfruit is:", str(self.starfruitMargin), '\n')