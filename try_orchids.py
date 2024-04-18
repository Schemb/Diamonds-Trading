for product in ['AMETHYSTS', 'STARFRUIT']:
    order_depth: OrderDepth = state.order_depths[product]
    orders = self.compute_orders(product, order_depth, acc_bid[product], acc_ask[product])
    result[product] += orders #[]+[ , ] -> becomes a new list
        


def compute_orders(self, product, order_depth, acc_bid, acc_ask):

    if product == "AMETHYSTS":
        return self.compute_orders_AMETHYSTS(product, order_depth, acc_bid, acc_ask)
    if product == "STARFRUIT":
        return self.compute_orders_regression(product, order_depth, acc_bid, acc_ask, self.POSITION_LIMIT[product])
    

starfruit_cache=[]
starfruit_dim=4
#if len(self.starfruit_cache) is already equal to 4 we have to pop the first elementn to append the new one
if len(self.starfruit_cache) == self.starfruit_dim:
self.starfruit_cache.pop(0) #pop(0) modifies the list but also returns the element that is removed from the list

_, bs_starfruit = self.values_extract(state.order_depths['STARFRUIT'].sell_orders,buy=0)
#bs is best sell of starfruit, meaning best ask/ best sell offer/ the lowest that people sell to us
_, bb_starfruit = self.values_extract(state.order_depths['STARFRUIT'].buy_orders, buy=1)
#bb is is best bid/ best buy offer: the highest people want to buy from us

self.starfruit_cache.append((bs_starfruit+bb_starfruit)/2)
        
#from here onwards, starfruit_cache either have 1 element, 2 elements, 3 elements, or 4 elements

starfruit_lb = self.calc_next_price_starfruit()-1
starfruit_ub = self.calc_next_price_starfruit()+1

acc_bid = {'AMETHYSTS' : AMETHYSTS_lb, 'STARFRUIT' : starfruit_lb} # we want to buy at slightly below
acc_ask = {'AMETHYSTS' : AMETHYSTS_ub, 'STARFRUIT' : starfruit_ub} # we want to sell at slightly above

def calc_next_price_starfruit(self):

        coef = [0.189599, 0.211908, 0.259882, 0.338144]
        intercept = 2.35578

        nxt_price = 0
        nxt_price += intercept

        if len(self.starfruit_cache)==self.starfruit_dim:
            for i, val in enumerate(self.starfruit_cache):
                nxt_price += val * coef[i]
        else:#for the case in the beginning where en(self.starfruit_cache)<self.starfruit_dim
            for i, val in enumerate(reversed(self.starfruit_cache)): 
                #val goes in the reverse order of starfruit_cache list but but i. i still goes from 0
                #adjust index: index of coeff should go from 3 to 2 to 1
                #when i=0, we want index 3 of coef. when i=1, we want index 2. => use index 3-i
                nxt_price += val * coef[3-i]
                
        return int(round(nxt_price))

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