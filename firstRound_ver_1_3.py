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
        self.DoAmethystTrading(state.order_depths[product])

      elif product == "STARFRUIT":
        self.DoStarfruitTrading(state.order_depths[product])

    print("=--  Trading ended!  --=\n")

    traderData = "SAMPLE"

    conversions = 1

    return self.result, conversions, traderData



  def DoAmethystTrading(self, orderDepth: OrderDepth):
    print("= AMETHYSTS =")

    # A list of any orders made
    orders: List[Order] = []

    # The precalculated median of the amethyst price, used to determine when to buy/sell
    median = 10000

    # Loops through all the sell orders
    for sellOrder in orderDepth.sell_orders:
      
      # Gets the price and size of the order
      askPrice = sellOrder
      askAmount = orderDepth.sell_orders[sellOrder]
      
      if int(askPrice) < median:  # If they are being sold less than the median

        # Adjust stored amethyst variables based on the order
        self.amethystMargin = self.amethystMargin + (askAmount * askPrice)
        self.amethystAmount = self.amethystAmount - askAmount

        # Prints how many were bought, and at what value
        print("\tBUY", str(-askAmount) + "x", askPrice)

        # Appends the buy to the orders list
        orders.append(Order("AMETHYSTS", askPrice, -askAmount))

      else:
        # Prints what the order was, even though it wasn't bought
        print("\tDIDN'T BUY", str(-askAmount) + "x", askPrice)

    print() # Prints a newline for formatting (only works in local testing)

    # Loops through all the buy orders
    for buyOrder in orderDepth.buy_orders:

      # Gets the asking price and the amount of the bid
      bidPrice = buyOrder
      bidAmount = orderDepth.buy_orders[buyOrder]

      if int(bidPrice) > median: # If they are paying above the median

        # Adjust stored amethyst variables based on the order
        self.amethystMargin = self.amethystMargin + (bidAmount * bidPrice)
        self.amethystAmount = self.amethystAmount - bidAmount

        # Prints how many were sold, and at what value
        print("\tSELL", str(bidAmount) + "x", bidPrice)

        # Appends the sell to the orders list
        orders.append(Order("AMETHYSTS", bidPrice, -bidAmount))

      else:
        # Prints what the order was, even though nothing was sold
        print("\tDIDN'T SELL", str(bidAmount) + "x", bidPrice)
    
    print() # Prints a newline for formatting (only works in local testing)

    # Adds the order to the results dictionary
    self.result["AMETHYSTS"] = orders
    
    # Prints of the current trading attributes relating to amethst
    print("\tCurrently holding", str(self.amethystAmount), "amethyst(s)!")
    print("\tCurrent profit margin for amethyst is:", str(self.amethystMargin), '\n')
    


  def DoStarfruitTrading(self, orderDepth: OrderDepth):
    print("= STARFRUIT =")

    # A list of any orders made
    orders: List[Order] = []

    # Loops through all the sell orders
    for sellOrder in orderDepth.sell_orders:
      
      # Gets the price and size of the order
      askPrice = sellOrder
      askAmount = orderDepth.sell_orders[sellOrder]

    # print() # Prints a newline for formatting (only works in local testing)

    # Loops through all the buy orders
    for buyOrder in orderDepth.buy_orders:

      # Gets the asking price and the amount of the bid
      bidPrice = buyOrder
      bidAmount = orderDepth.buy_orders[buyOrder]
    
    # print() # Prints a newline for formatting (only works in local testing)

    # Adds the order to the results dictionary
    self.result["STARFRUIT"] = orders
    
    # Prints of the current trading attributes relating to amethst
    print("\tCurrently holding", str(self.starfruitAmount), "starfruit!")
    print("\tCurrent profit margin for starfruit is:", str(self.starfruitMargin), '\n')