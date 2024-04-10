from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string

class Trader:
  result = {}   # The result of a trading iteration

  amethystMargin = 0      # Variable to store the current profit/loss of amethyst
  amethystAmount = 0      # The number of amethyst that is currently held (must be within the position limit)
  amethystPosLimit = 20   # The position limits for amethyst 
  amethestBuyIn = [0, 1, 3, 9, 27, 40]

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
        self.DoAmethystTrading(state)

      elif product == "STARFRUIT":
        self.DoStarfruitTrading(state)

    print("=--  Trading ended!  --=\n")

    traderData = "SAMPLE"

    conversions = 1

    return self.result, conversions, traderData



  def DoAmethystTrading(self, state: TradingState):
    print("= AMETHYSTS =")

    
    # A list of any orders made
    orders: List[Order] = []

    # The buy and sell orders
    orderDepth: OrderDepth = state.order_depths["AMETHYSTS"]

    # The precalculated median of the amethyst price, used to determine when to buy/sell
    median = 10000

    # Used to determine if any of the amethysts that the algorithm
    #   tries to sell in the final iterations were bought by any bots
    if (state.position["AMETHYSTS"] != self.amethystAmount):
      posDifference = self.amethystAmount - state.position["AMETHYSTS"]
      self.amethystAmount = state.position["AMETHYSTS"]
      self.amethystMargin = self.amethystMargin + posDifference * median

    # Loops through all the sell orders
    for sellOrder in orderDepth.sell_orders:
      
      # Gets the price and size of the order
      askPrice = sellOrder
      askAmount = -orderDepth.sell_orders[sellOrder]
      
      if int(askPrice) < median:  # If they are being sold less than the median

        # Determine the difference in price
        difference = median - askPrice

        # Don't buy if the difference is out of range
        if difference > 5:
          continue

        # Determine how many should be bought, between the minimum of:
        #   - How many are being sold
        #   - How many it can buy without exceeding the position limit
        #   - How many it wants to buy based on the difference in price (can be changed)
        buyAmount = min(askAmount,
                        self.amethestBuyIn[difference], 
                        self.amethystPosLimit - self.amethystAmount)

        # Adjust stored amethyst variables based on how the order was executed
        self.amethystMargin = self.amethystMargin - (buyAmount * askPrice)
        self.amethystAmount = self.amethystAmount + buyAmount

        # Prints how many were bought, and at what value
        print("\tBUY", str(buyAmount) + "x", askPrice)

        # Appends the buy to the orders list
        orders.append(Order("AMETHYSTS", askPrice, buyAmount))

      else:
        # Prints what the order was, even though it wasn't bought
        print("\tDIDN'T BUY (too expensive)", str(askAmount) + "x", askPrice)

    print() # Prints a newline for formatting (only works in local testing)

    # Loops through all the buy orders
    for buyOrder in orderDepth.buy_orders:

      # Gets the asking price and the amount of the bid
      bidPrice = buyOrder
      bidAmount = orderDepth.buy_orders[buyOrder]

      if int(bidPrice) > median: # If they are paying above the median
        
        # Determine the difference in price
        difference = bidPrice - median

        # Don't buy if the difference is out of range
        if difference > 5:
          continue

        # Determine how many should be sold, between the minimum of:
        #   - How many are being bought
        #   - How many it can sell without exceeding the position limit
        #   - How many it wants to sell based on the difference in price (can be changed)
        sellAmount = min(bidAmount,
                        self.amethestBuyIn[difference], 
                        self.amethystPosLimit + self.amethystAmount)

        # Adjust stored amethyst variables based on the order
        self.amethystMargin = self.amethystMargin + (sellAmount * bidPrice)
        self.amethystAmount = self.amethystAmount - sellAmount

        # Prints how many were sold, and at what value
        print("\tSELL", str(sellAmount) + "x", bidPrice)

        # Appends the sell to the orders list
        orders.append(Order("AMETHYSTS", bidPrice, -sellAmount))

      else:
        # Prints what the order was, even though nothing was sold
        print("\tDIDN'T SELL", str(bidAmount) + "x", bidPrice)
    
    # Attempts to sell as much as possible in the last 5 iterations
    if state.timestamp >= 99500:
      print("\tAttempting to sell remaining")

      # However many positions are left to sell
      sellAmount = self.amethystPosLimit + self.amethystAmount

      # Prints how many were sold, and at what value
      print("\tSELL", str(sellAmount) + "x", median)

      # Sells remaining at median price
      orders.append(Order("AMETHYSTS", median, -sellAmount))

    print() # Prints a newline for formatting (only works in local testing)

    # Adds the order to the results dictionary
    self.result["AMETHYSTS"] = orders
    
    # Prints of the current trading attributes relating to amethst
    print("\tCurrently holding", str(self.amethystAmount), "amethyst(s)!")
    print("\tCurrent profit margin for amethyst is:", str(self.amethystMargin), '\n')
    


  def DoStarfruitTrading(self, state: TradingState):
    print("= STARFRUIT =")

    # A list of any orders made
    orders: List[Order] = []
    
    # The buy and sell orders
    orderDepth: OrderDepth = state.order_depths["STARFRUIT"]

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