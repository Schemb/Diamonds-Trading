from typing import Dict, List
from datamodel import Listing, OrderDepth, Trade, TradingState, ConversionObservation,  Observation, Order
import math 
import numpy as np



class Trader: #each new object of trader is created for one round eg. one day, 10000 iterations, timestamp from 0 to 1M

    position= {'AMETHYSTS' : 0, 'STARFRUIT' : 0, "ORCHIDS": 0, "STRAWBERRIES": 0, "ROSES":0, "CHOCOLATE":0, "GIFT_BASKET":0 }
    volume_traded= {'AMETHYSTS' : 0, 'STARFRUIT' : 0, "ORCHIDS":0, "STRAWBERRIES":0,"ROSES":0,"CHOCOLATE":0,"GIFT_BASKET":0 } #total_volume traded
    POSITION_LIMIT = {'AMETHYSTS': 20, 'STARFRUIT': 20, "ORCHIDS":100, "STRAWBERRIES":350,"ROSES":60,"CHOCOLATE":250,"GIFT_BASKET":60 }

    cpnl = {'AMETHYSTS' : 0, 'STARFRUIT' : 0, "ORCHIDS": 0, "STRAWBERRIES": 0,"ROSES":0,"CHOCOLATE":0,"GIFT_BASKET":0} #totals pnl of each product after each round

    starfruit_cache = []
    starfruit_dim = 4

    basket_cache=[]
    basket_dim=12

    choco_cache=[]
    choco_dim=12

    roses_cache=[]
    roses_dim=12

    straw_cache=[]
    straw_dim=12


    steps = 0
    

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        
        # Initialize the method output dict as an empty dict
        result = {'AMETHYSTS' : [], 'STARFRUIT' : [], "ORCHIDS": [], "STRAWBERRIES": [],"ROSES":[],"CHOCOLATE":[],"GIFT_BASKET":[] }

        timestamp = state.timestamp

        #Update the current position of each product from the position in the TradingState object
        for key, val in state.position.items():
            self.position[key] = val

        #Calculate lb and ub of STARFRUIT, and create STARFRUIT cache
        if len(self.starfruit_cache) == self.starfruit_dim:
            self.starfruit_cache.pop(0) #pop(0) modifies the list but also returns the element that is removed from the list
        _, bs_starfruit = self.values_extract(state.order_depths['STARFRUIT'].sell_orders,buy=0)
        _, bb_starfruit = self.values_extract(state.order_depths['STARFRUIT'].buy_orders, buy=1)
        self.starfruit_cache.append((bs_starfruit+bb_starfruit)/2)
        #from here onwards, starfruit_cache either have 1 element, 2 elements, 3 elements, or 4 elements
        starfruit_lb = self.calc_next_price_starfruit()-1
        starfruit_ub = self.calc_next_price_starfruit()+1

        #Calculate lb and ub of GIFT_BASKET, and create GIFT_BASKET cache
        if len(self.basket_cache) == self.basket_dim:
            del self.basket_cache[:4] #remove the first four elements of the list
        if len(self.choco_cache) == self.choco_dim:
            del self.choco_cache[:4] #remove the first four elements of the list
        if len(self.roses_cache) == self.roses_dim:
            del self.roses_cache[:4] #remove the first four elements of the list
        if len(self.straw_cache) == self.straw_dim:
            del self.straw_cache[:4] #remove the first four elements of the list

        _, bs_basket = self.values_extract(state.order_depths['GIFT_BASKET'].sell_orders,buy=0)
        _, bb_basket = self.values_extract(state.order_depths['GIFT_BASKET'].buy_orders, buy=1)
        mid_price_basket=(bs_basket+bb_basket)/2

        _, bs_choco = self.values_extract(state.order_depths['CHOCOLATE'].sell_orders,buy=0)
        _, bb_choco = self.values_extract(state.order_depths['CHOCOLATE'].buy_orders, buy=1)
        mid_price_choco=(bs_choco+bb_choco)/2

        _, bs_roses = self.values_extract(state.order_depths['ROSES'].sell_orders,buy=0)
        _, bb_roses = self.values_extract(state.order_depths['ROSES'].buy_orders, buy=1)
        mid_price_roses=(bs_roses+bb_roses)/2

        _, bs_straw = self.values_extract(state.order_depths['STRAWBERRIES'].sell_orders,buy=0)
        _, bb_straw = self.values_extract(state.order_depths['STRAWBERRIES'].buy_orders, buy=1)
        mid_price_straw=(bs_straw+bb_straw)/2

        #basket_cache
        self.basket_cache.append(mid_price_straw)
        self.basket_cache.append(mid_price_roses)
        self.basket_cache.append(mid_price_choco)
        self.basket_cache.append(mid_price_basket)
        #from here onwards, those caches either have 4 element, 8 elements, or 12 elements. cannot be more than that
        basket_lb = self.calc_next_price_basket()-6 #-6.42
        basket_ub = self.calc_next_price_basket()+6 #+6.42

        #choco_cache
        self.choco_cache.append(mid_price_basket)
        self.choco_cache.append(mid_price_straw)
        self.choco_cache.append(mid_price_roses)
        self.choco_cache.append(mid_price_choco)
        #from here onwards, those caches either have 4 element, 8 elements, or 12 elements. cannot be more than that
        choco_lb = self.calc_next_price_choco()-1 #-0.8
        choco_ub = self.calc_next_price_choco()+1 #+0.8

        #roses_cache
        self.roses_cache.append(mid_price_choco)
        self.roses_cache.append(mid_price_basket)
        self.roses_cache.append(mid_price_straw)
        self.roses_cache.append(mid_price_roses)
        #from here onwards, those caches either have 4 element, 8 elements, or 12 elements. cannot be more than that
        roses_lb = self.calc_next_price_roses()-1 #-2.17
        roses_ub = self.calc_next_price_roses()+1 #+2.17


        #straw_cache
        self.straw_cache.append(mid_price_roses)
        self.straw_cache.append(mid_price_choco)
        self.straw_cache.append(mid_price_basket)
        self.straw_cache.append(mid_price_straw)
        #from here onwards, those caches either have 4 element, 8 elements, or 12 elements. cannot be more than that
        straw_lb = self.calc_next_price_straw()-1 #-0.32
        straw_ub = self.calc_next_price_straw()+1 #+0.32
        

        #calculate lb and ub of AMETHYSTS
        AMETHYSTS_lb = 10000
        AMETHYSTS_ub = 10000

        #acc_bid and ask_ask of each product using regression
        acc_bid = {'AMETHYSTS' : AMETHYSTS_lb, 'STARFRUIT' : starfruit_lb, "STRAWBERRIES": straw_lb, "ROSES": roses_lb,"CHOCOLATE": choco_lb ,"GIFT_BASKET": basket_lb} # we want to buy at slightly below
        acc_ask = {'AMETHYSTS' : AMETHYSTS_ub, 'STARFRUIT' : starfruit_ub, "STRAWBERRIES": straw_ub, "ROSES": roses_ub,"CHOCOLATE": choco_ub ,"GIFT_BASKET": basket_ub} # we want to sell at slightly above

        self.steps += 1

        #Compute orders-------------------------------------------------------------------------------------------------
        for product in ['AMETHYSTS', 'STARFRUIT',"ROSES","STRAWBERRIES","CHOCOLATE","GIFT_BASKET"]: 
            order_depth: OrderDepth = state.order_depths[product]
            orders = self.compute_orders(product, order_depth, acc_bid[product], acc_ask[product])
            result[product] += orders #[]+[ , ] -> becomes a new list

            product, order_depth, acc_bid, acc_ask, self.POSITION_LIMIT[product]

        #Compute cpnl of each product-------------------------------------------------------------------------------------
       
        for product in state.own_trades.keys():
            for trade in state.own_trades[product]: #state.own_trades[product] - a list of Trade objects for each product
                if trade.timestamp != state.timestamp-100:
                    continue 
                self.volume_traded[product] += abs(trade.quantity) #actually no need because trade.quantity is always the absolute value in Trade objects
                if trade.buyer == "SUBMISSION":
                    self.cpnl[product] -= trade.quantity * trade.price #the amount we pay for each trade
                else:
                    self.cpnl[product] += trade.quantity * trade.price #the amount we receive for each trade

        #End computation of cpnl of each product-------------------------------------------------------------------------------------
        
        print(f"Timestamp {timestamp}, PnL of each product is: ")
        for product in state.order_depths.keys():
            print(f"Product {product} has PnL {self.cpnl[product]}")
        print(f"End timestamp {timestamp} \n ")

        traderData = "SAMPLE"

        orchidConversions=0

        return result, orchidConversions, traderData        
    
    def compute_orders(self, product, order_depth, acc_bid, acc_ask):

        if product == "AMETHYSTS":
            return self.compute_orders_AMETHYSTS(product, order_depth, acc_bid, acc_ask)
        if product in ["STARFRUIT","STRAWBERRIES","ROSES","CHOCOLATE","GIFT_BASKET"]:
            return self.compute_orders_regression(product, order_depth, acc_bid, acc_ask, self.POSITION_LIMIT[product])

    def compute_orders_AMETHYSTS(self, product, order_depth, acc_bid, acc_ask): #this is how to market make and market take around 10k considering the no. of positions
        #acc_bid: low bound; acc_ask: up bound
        #position= {'AMETHYSTS' : 0}
        #POSITION_LIMIT = {'AMETHYSTS': 20}
        orders: list[Order] = [] 

        sell_vol, best_sell_pr = self.values_extract(order_depth.sell_orders,buy=0)
        buy_vol, best_buy_pr = self.values_extract(order_depth.buy_orders, buy=1)

        osell =sorted(order_depth.sell_orders.items(), reverse=True) #order_depth dictionary {price: quantity}  in descending order
        obuy = sorted(order_depth.buy_orders.items(), reverse=False) # in increasing order

        #product='AMETHYSTS' #the value right now
        cpos = self.position[product] #cpos is an integer, the value of the position right now

        mx_with_buy = -1 #the highest ask/ sell price in osell

        #----------------generate buy orders for AMETHYSTS------------------

        for ask, vol in osell:
            if (  (ask < acc_bid)   or   ( (ask == acc_bid) and (self.position[product]<0) )  ) and cpos < self.POSITION_LIMIT['AMETHYSTS']:
                mx_with_buy = max(mx_with_buy, ask)
                order_for = min(-vol, self.POSITION_LIMIT['AMETHYSTS'] - cpos)
                cpos += order_for
                assert(order_for >= 0)
                orders.append(Order(product, ask, order_for))

        mprice_actual = (best_sell_pr + best_buy_pr)/2 #true mid price from the order depth of this iteration
        mprice_ours = (acc_bid+acc_ask)/2 #the calculated_next_price of the next iteration we predict in this iteration

        undercut_buy = best_buy_pr + 1 #highest buy +1
        undercut_sell = best_sell_pr - 1 #lowest sell -1

        bid_pr = min(undercut_buy, acc_bid-1) # we will shift this by 1 to beat this price
        sell_pr = max(undercut_sell, acc_ask+1)

        if (cpos < self.POSITION_LIMIT['AMETHYSTS']) and (self.position[product] < 0):
            num = min(40, self.POSITION_LIMIT['AMETHYSTS'] - cpos)
            orders.append(Order(product, min(undercut_buy + 1, acc_bid-1), num))
            cpos += num

        if (cpos < self.POSITION_LIMIT['AMETHYSTS']) and (self.position[product] > 15):
            num = min(40, self.POSITION_LIMIT['AMETHYSTS'] - cpos)
            orders.append(Order(product, min(undercut_buy - 1, acc_bid-1), num))
            cpos += num

        if cpos < self.POSITION_LIMIT['AMETHYSTS']:
            num = min(40, self.POSITION_LIMIT['AMETHYSTS'] - cpos)
            orders.append(Order(product, bid_pr, num))
            cpos += num
        
        cpos = self.position[product]

        #----------------generate sell orders for AMETHYSTS------------------

        for bid, vol in obuy:
            if ((bid > acc_ask) or ((self.position[product]>0) and (bid == acc_ask))) and cpos > -self.POSITION_LIMIT['AMETHYSTS']:
                order_for = max(-vol, -self.POSITION_LIMIT['AMETHYSTS']-cpos)
                # order_for is a negative number denoting how much we will sell
                cpos += order_for
                assert(order_for <= 0)
                orders.append(Order(product, bid, order_for))

        if (cpos > -self.POSITION_LIMIT['AMETHYSTS']) and (self.position[product] > 0):
            num = max(-40, -self.POSITION_LIMIT['AMETHYSTS']-cpos)
            orders.append(Order(product, max(undercut_sell-1, acc_ask+1), num))
            cpos += num

        if (cpos > -self.POSITION_LIMIT['AMETHYSTS']) and (self.position[product] < -15):
            num = max(-40, -self.POSITION_LIMIT['AMETHYSTS']-cpos)
            orders.append(Order(product, max(undercut_sell+1, acc_ask+1), num))
            cpos += num

        if cpos > -self.POSITION_LIMIT['AMETHYSTS']:
            num = max(-40, -self.POSITION_LIMIT['AMETHYSTS']-cpos)
            orders.append(Order(product, sell_pr, num))
            cpos += num

        return orders
    
    def compute_orders_regression(self, product, order_depth, acc_bid, acc_ask, LIMIT):
        orders: list[Order] = []

        #osell = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
        #obuy = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))

        sell_vol, best_sell_pr = self.values_extract(order_depth.sell_orders,buy=0)
        buy_vol, best_buy_pr = self.values_extract(order_depth.buy_orders, buy=1)

        osell =sorted(order_depth.sell_orders.items(), reverse=True) #selling price to us in descending order
        obuy = sorted(order_depth.buy_orders.items(), reverse=False) #buy_price from us in increasing order

        cpos = self.position[product]

        for ask, vol in osell:
            if ((ask <= acc_bid) or ((self.position[product]<0) and (ask == acc_bid+1))) and cpos < LIMIT:
                order_for = min(-vol, LIMIT - cpos)
                cpos += order_for
                assert(order_for >= 0)
                orders.append(Order(product, ask, order_for))

        undercut_buy = best_buy_pr + 1
        undercut_sell = best_sell_pr - 1

        bid_pr = min(undercut_buy, acc_bid) # we will shift this by 1 to beat this price
        sell_pr = max(undercut_sell, acc_ask)

        if cpos < LIMIT:
            num = LIMIT - cpos
            orders.append(Order(product, bid_pr, num))
            cpos += num
        
        cpos = self.position[product]
        

        for bid, vol in obuy:
            if ((bid >= acc_ask) or ((self.position[product]>0) and (bid+1 == acc_ask))) and cpos > -LIMIT:
                order_for = max(-vol, -LIMIT-cpos)
                # order_for is a negative number denoting how much we will sell
                cpos += order_for
                assert(order_for <= 0)
                orders.append(Order(product, bid, order_for))

        if cpos > -LIMIT:
            num = -LIMIT-cpos
            orders.append(Order(product, sell_pr, num))
            cpos += num

        return orders

    def calc_next_price_basket(self):
        coef = [-0.210096, 0.0146873, 0.0870346, -0.00949982, -0.147523, -0.0773193, -0.332617, 0.0503922, 0.379256, 0.0650236, 0.260812, 0.955566]
        intercept = 8.05676

        nxt_price = 0
        nxt_price += intercept
        n=self.basket_dim #which is 12

        for i, val in enumerate(reversed(self.basket_cache)): #going backward
            #val goes in the reverse order but i still goes from 0 to 12
            #when i=0, we want coef[11]. 
            #when i=1, we want coef[10].
            #when i=3, want coef[10] 
            #...
            #when i=7, want coef [4] 
            #when i=11 (we go to the last element of the cache alr), we want coef[0]
            #=> use coef[11-i]
            nxt_price += val * coef[n-1-i]
                
        return int(round(nxt_price)) #the price sent must be an integer. round function with no specified number rounds to NEAREST INTEGER
    
    def calc_next_price_choco(self):
        coef = [-0.00171852, -0.0206925, 0.00688553, 0.0103909, 0.000139229, 0.0304389, -0.00799088, 0.0199932, 0.00141778, -0.00907091, 0.0012941, 0.970149]
        intercept = 1.73695

        nxt_price = 0
        nxt_price += intercept
        n=self.choco_dim #which is 12

        for i, val in enumerate(reversed(self.choco_cache)): #going backward
            nxt_price += val * coef[n-1-i]
                
        return int(round(nxt_price))
    
    def calc_next_price_roses(self):
        coef = [0.0100365, 0.000249482, 0.0555328, -0.0113794, -0.0118852, -0.00774528, 0.0223854, 0.0304468, 0.00194246, 0.00765496, -0.07882, 0.98018]
        intercept = 2.54291

        nxt_price = 0
        nxt_price += intercept
        n=self.roses_dim #which is 12

        for i, val in enumerate(reversed(self.roses_cache)): #going backward
            nxt_price += val * coef[n-1-i]
                
        return int(round(nxt_price)) 
    
    def calc_next_price_straw(self):
        coef = [-0.000731349, 0.00837658, -0.000482421, 0.02052, 0.00417019, -0.00380315, -0.00296118, 0.126236, -0.00339336, -0.00421048, 0.00337559, 0.853475]
        intercept = 0.344167

        nxt_price = 0
        nxt_price += intercept
        n=self.straw_dim #which is 12

        for i, val in enumerate(reversed(self.straw_cache)): #going backward
            nxt_price += val * coef[n-1-i]
                
        return int(round(nxt_price)) 

    def calc_next_price_starfruit(self):
        
        #price is mid price, the average price of highest buy offer and lowest sell offer in that iteration.

        coef = [0.189599, 0.211908, 0.259882, 0.338144]
        intercept = 2.35578

        nxt_price = 0
        nxt_price += intercept

        n=self.starfruit_dim #which is 4

        for i, val in enumerate(reversed(self.starfruit_cache)): 
            nxt_price += val * coef[n-1-i]
                
        return int(round(nxt_price)) #the price sent must be an integer. round function with no specified number rounds to NEAREST INTEGER

    def values_extract(self, orderdepth_dict: dict, buy : int =0):
        #orderdepth of each product has two attributes, order_depth.buy_orders and order_depth.sell_orders
        #eg. buy_orders={9: 5, 10: 4, 8: 2} 
        #eg. sell_orders={12: -3, 11: -2, 14: -9 }
        #the role of this function is to, taken two parameters, one (ordinary) dictionary and buy=0 or 1; return total volume and best_value
        #the buy=0) in parameters in put means if not declaring, default value is buy=0. If declared 1, then buy=1
        #tot_vol is the total volume of all buy offers; and tot_vol of all sell offers
        #best_value: if buy==0 eg. this is buy_orders, best value is the HIGHEST BID OFFER/ BUY PRICE
        #best_value: if sell==1 eg. this is sell_orders, best value is the LOWEST ASK OFFER/ ASK PRICE
        tot_vol  = 0
        best_val  = 0
        if buy==1:
            #this is .buy_order
            buy_orders_sorted=sorted(orderdepth_dict.items(),reverse=False) #in_ascending_order
            #the highest bid offer/ buy price is the last key of this dictionary buy_orders_sorted
            for buy_price, vol in buy_orders_sorted:
                tot_vol += vol
                best_val = buy_price #when buy_price is iterated to the last key of buy_orders_sorted, that's also the value of best_val
    
        if buy==0:
            #This is .sell_order
            sell_orders_sorted=sorted(orderdepth_dict.items(),reverse=True) #in_descending_order
            #the lowest ask offer/ sell price to us is the last key
            for ask,vol in sell_orders_sorted:
                vol*= -1 #make vol positive
                tot_vol += vol
                best_val = ask #when ask is iterated to the last key which is the smallest ask offer/sell price to us, that's also the value of best_val

        return tot_vol, best_val

"""
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

        # if buySpread >= 400: # buy components
            # Prints how many were were worth buying, and at what value
            # print("\tBUY COMPONENTS:", chocolate, lowestAskPrices[chocolate], strawberries, lowestAskPrices[strawberries], roses, lowestAskPrices[roses])

            # # Appends the buy to the orders list
            # orders[chocolate].append(Order(chocolate, lowestAskPrices[chocolate], 4))
            # orders[strawberries].append(Order(strawberries, lowestAskPrices[strawberries], 6))
            # orders[roses].append(Order(roses, lowestAskPrices[roses], 1))

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


        # if sellSpread <= 400: # buy components
            # Prints how many were were worth buying, and at what value
            # print("\tSELL COMPONENTS:", chocolate, highestBidPrices[chocolate], strawberries, highestBidPrices[strawberries], roses, highestBidPrices[roses])

            # Appends the buy to the orders list
            # orders[chocolate].append(Order(chocolate, highestBidPrices[chocolate], -4))
            # orders[strawberries].append(Order(strawberries, highestBidPrices[strawberries], -6))
            # orders[roses].append(Order(roses, highestBidPrices[roses], -1))

        if sellSpread > 400: # buy basket
            # Prints how many were were worth buying, and at what value
            print("\tSELL BASKET:", baskets, highestBidPrices[baskets])

            # Appends the buy to the orders list
            orders[baskets].append(Order(baskets, highestBidPrices[baskets], -1))

        # print("SPREADS:", buySpread, self.highestBuySpread, self.lowestBuySpread, sellSpread, self.highestSellSpread, self.lowestSellSpread)

        # Returns the order
        return orders[product]
"""