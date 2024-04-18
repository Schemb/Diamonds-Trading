from typing import Dict, List
from datamodel import Listing, OrderDepth, Trade, TradingState, ConversionObservation,  Observation, Order
#import collections #ordered dict
#from collections import defaultdict #defaultdict(def_value)
import math 
#import copy #deep copy
import numpy as np

#empty_dict = {'AMETHYSTS' : 0, 'STARFRUIT' : 0}

#def def_value():
    #return copy.deepcopy(empty_dict)

class Trader:
    #position = copy.deepcopy(empty_dict)
    #volume_traded = copy.deepcopy(empty_dict)
    position= {'AMETHYSTS' : 0, 'STARFRUIT' : 0}
    volume_traded= {'AMETHYSTS' : 0, 'STARFRUIT' : 0}
    POSITION_LIMIT = {'AMETHYSTS' : 20, 'STARFRUIT' : 20}

    #person_position = defaultdict(def_value)
    #person_actvalof_position = defaultdict(def_value)
    person_position = {'AMETHYSTS' : 0, 'STARFRUIT' : 0} #no need
    person_actvalof_position = {'AMETHYSTS' : 0, 'STARFRUIT' : 0} #no need
    
    #cpnl = defaultdict(lambda : 0) #meaning later if new products are added the value will be automatically 0. but we just put all products and initialise to be 0
    cpnl = {'AMETHYSTS' : 0, 'STARFRUIT' : 0}

    starfruit_cache = []
    starfruit_dim = 4
    steps = 0
    
    halflife_diff = 5
    alpha_diff = 1 - np.exp(-np.log(2)/halflife_diff)

    halflife_price = 5
    alpha_price = 1 - np.exp(-np.log(2)/halflife_price)

    halflife_price_dip = 20
    alpha_price_dip = 1 - np.exp(-np.log(2)/halflife_price_dip)

    INF = int(1e9)
    begin_diff_dip = -INF
    begin_diff_bag = -INF
    begin_bag_price = -INF
    begin_dip_price = -INF

    std = 25
    basket_std = 117

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        #state: TradingState -> name the input object belonging to class TradingState "state"
        #can also do the same with def run(self, a: int) for example to specify the data type of a
        #-> Dict[str, List[Order]]: to specify the output data type. However, this is not necessary.
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {'AMETHYSTS' : [], 'STARFRUIT' : []}

        for key, val in self.position.items():
            print(f'{key} position: {val}')


        timestamp = state.timestamp

        if len(self.starfruit_cache) == self.starfruit_dim:
            self.starfruit_cache.pop(0) #pop(0) modifies the list but also returns the element that is removed from the list

        _, bs_starfruit = self.values_extract(state.order_depths['STARFRUIT'].sell_orders,buy=0)
        #bs is best sell of starfruit, meaning best ask/ best sell offer/ the lowest that people sell to us
        _, bb_starfruit = self.values_extract(state.order_depths['STARFRUIT'].buy_orders, buy=1)
        #bb is is best bid/ best buy offer: the highest people want to buy from us

        self.starfruit_cache.append((bs_starfruit+bb_starfruit)/2)

        INF = 1e9
    
        starfruit_lb = -INF
        starfruit_ub = INF

        if len(self.starfruit_cache) == self.starfruit_dim:
            starfruit_lb = self.calc_next_price_starfruit()-1
            starfruit_ub = self.calc_next_price_starfruit()+1

        AMETHYSTS_lb = 10000
        AMETHYSTS_ub = 10000

        # CHANGE FROM HERE

        acc_bid = {'AMETHYSTS' : AMETHYSTS_lb, 'STARFRUIT' : starfruit_lb} # we want to buy at slightly below
        acc_ask = {'AMETHYSTS' : AMETHYSTS_ub, 'STARFRUIT' : starfruit_ub} # we want to sell at slightly above

        self.steps += 1

        for product in state.market_trades.keys():
            for trade in state.market_trades[product]:
                if trade.buyer == trade.seller:
                    continue
                self.person_position[trade.buyer][product] = 1.5
                self.person_position[trade.seller][product] = -1.5
                self.person_actvalof_position[trade.buyer][product] += trade.quantity
                self.person_actvalof_position[trade.seller][product] += -trade.quantity

        
        for product in ['AMETHYSTS', 'STARFRUIT']:
            order_depth: OrderDepth = state.order_depths[product]
            #LHS: create a new variable called order_depth belonging to class OrderDepth
            #RHS: object state of class TradingState has a data attribute called order_depths of class OrderDepth
            #each OrderDepth object has two data members, self.buy_orders like {9: 5, 10: 4} and self.sell_orders.
            #they are outstanding buy and sell offers of this iteration.
            #each state.order_depths[product] is an object of class OrderDepth and has 2 datamembers, .buy_orders and .sell_orders (Refer to Notion)
            orders = self.compute_orders(product, order_depth, acc_bid[product], acc_ask[product])
            #acc_bid = {'AMETHYSTS' : AMETHYSTS_lb, 'STARFRUIT' : starfruit_lb} # we want to buy at slightly below
            #acc_ask = {'AMETHYSTS' : AMETHYSTS_ub, 'STARFRUIT' : starfruit_ub} # we want to sell at slightly above
            result[product] += orders #[]+[ , ] -> becomes a new list

        for product in state.own_trades.keys():
            for trade in state.own_trades[product]:
                if trade.timestamp != state.timestamp-100:
                    continue
                # print(f'We are trading {product}, {trade.buyer}, {trade.seller}, {trade.quantity}, {trade.price}')
                self.volume_traded[product] += abs(trade.quantity)
                if trade.buyer == "SUBMISSION":
                    self.cpnl[product] -= trade.quantity * trade.price
                else:
                    self.cpnl[product] += trade.quantity * trade.price

        totpnl = 0

        for product in state.order_depths.keys():
            try:
              self.position[product]
            except:
                continue  
            settled_pnl = 0
            best_sell = min(state.order_depths[product].sell_orders.keys())
            best_buy = max(state.order_depths[product].buy_orders.keys())
            
            if self.position[product] < 0:
                settled_pnl += self.position[product] * best_buy
            else:
                settled_pnl += self.position[product] * best_sell
            totpnl += settled_pnl + self.cpnl[product]
            print(f"For product {product}, {settled_pnl + self.cpnl[product]}, {(settled_pnl+self.cpnl[product])/(self.volume_traded[product]+1e-20)}")

        """"
        for person in self.person_position.keys():
            for val in self.person_position[person].keys():
                
                if person == 'Olivia':
                    self.person_position[person][val] *= 0.995
                if person == 'Pablo':
                    self.person_position[person][val] *= 0.8
                if person == 'Camilla':
                    self.person_position[person][val] *= 0
        """

        print(f"Timestamp {timestamp}, Total PNL ended up being {totpnl}")
        
        # print(f'Will trade {result}')
        print("End transmission")

        traderData = "SAMPLE"

        conversions=0
        
        #initialise random Orders for other products
        for product in ["GIFT_BASKET","CHOCOLATE","STRAWBERRIES","ROSES","ORCHIDS"]:
            result[product]=[Order(product,10,0), Order(product,11,0) ] #a list of Order objects

        return result, conversions, traderData        
    
    def compute_orders(self, product, order_depth, acc_bid, acc_ask):

        if product == "AMETHYSTS":
            return self.compute_orders_AMETHYSTS(product, order_depth, acc_bid, acc_ask)
        if product == "STARFRUIT":
            return self.compute_orders_regression(product, order_depth, acc_bid, acc_ask, self.POSITION_LIMIT[product])

    #self.compute_orders(product, order_depth, acc_bid[product], acc_ask[product])
    #acc_bid = {'AMETHYSTS' : AMETHYSTS_lb, 'STARFRUIT' : starfruit_lb} # we want to buy at slightly below
    #acc_ask = {'AMETHYSTS' : AMETHYSTS_ub, 'STARFRUIT' : starfruit_ub} # we want to sell at slightly above
    #acc_bid: AMETHYSTS_lb
    #acc_ask: AMETHYSTS_ub
    def compute_orders_AMETHYSTS(self, product, order_depth, acc_bid, acc_ask): #this is how to market make and market take around 10k considering the no. of positions
        orders: list[Order] = [] #create a new variable "orders", specify the data type which is a list of objects belonging to the "Order" class, and this funtion returns this "orders" variable.

        #osell = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
        #obuy = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))
        
        #each OrderDepth object for 1 producthas two data members, self.buy_orders. they are outstanding buy and sell offers of this iteration.
        #eg. buy_orders like {9: 5, 10: 4} and eg. sell_orders {12: -3, 11: -2}
        #{9:5, 10:4}.items() -> Out: dict_items( [ (9, 5), (10, 4) ] )
        #The sorted() function returns a sorted list of the specified iterable object.
        #You can specify ascending or descending order. Strings are sorted alphabetically, and numbers are sorted numerically.
        #sorted(): reverse	Optional. A Boolean. False will sort ascending, True will sort descending. Default is False



        sell_vol, best_sell_pr = self.values_extract(order_depth.sell_orders,buy=0)
        buy_vol, best_buy_pr = self.values_extract(order_depth.buy_orders, buy=1)

        osell =sorted(order_depth.sell_orders.items(), reverse=True) #selling price to us in descending order
        obuy = sorted(order_depth.buy_orders.items(), reverse=False) #buy_price from us in increasing order

        #product='AMETHYSTS' #the value right now
        #position= {'AMETHYSTS' : 0, 'STARFRUIT' : 0} #this is the starting value of position dictionary
        cpos = self.position[product] #cpos is the absolute value of the position right now

        mx_with_buy = -1

        #----------------generate sell orders for AMETHYSTS------------------

        for ask, vol in osell:
            #for amethys acc_bid is 10k, acc_ask is also 10k
            if (  (ask < acc_bid)   or   ( (self.position[product]<0) and (ask == acc_bid) )  ) and cpos < self.POSITION_LIMIT['AMETHYSTS']:
                mx_with_buy = max(mx_with_buy, ask)
                order_for = min(-vol, self.POSITION_LIMIT['AMETHYSTS'] - cpos)
                cpos += order_for
                assert(order_for >= 0)
                orders.append(Order(product, ask, order_for))

        mprice_actual = (best_sell_pr + best_buy_pr)/2
        mprice_ours = (acc_bid+acc_ask)/2

        undercut_buy = best_buy_pr + 1
        undercut_sell = best_sell_pr - 1

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

        #----------------generate buy orders for AMETHYSTS------------------

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

    def calc_next_price_starfruit(self):
        #1 Day: from 0 to 1M time stamp, 
        # bananas cache stores price from 1 day ago, current day resp
        #but I see from your code, stanford, that the dimension of the bananas cache is 4, meaning the list stores 4 values. so you predict the value of this iteration based on the values of the last 4 iterations?
        # by price, here we mean mid price; which is the average price 

        coef = [0.189599, 0.211908, 0.259882, 0.338144]
        intercept = 2.35578

        nxt_price = intercept
        for i, val in enumerate(self.starfruit_cache):
            nxt_price += val * coef[i]

        return int(round(nxt_price))

    #osell = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
    #obuy = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))
    #sell_vol, best_sell_pr = self.values_extract(osell)
    #buy_vol, best_buy_pr = self.values_extract(obuy, 1)
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