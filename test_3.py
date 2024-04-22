#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 21 17:06:40 2024

@author: michellenguyen
"""
starfruit_cache=[ 5004.5, 5004.5, 5005, 5006.5]

def calc_next_price_starfruit(starfruit_cache):
    
    #price is mid price, the average price of highest buy offer and lowest sell offer in that iteration.

    coef = [0.189599, 0.211908, 0.259882, 0.338144]
    intercept = 2.35578

    nxt_price = 0
    nxt_price += intercept

    n=4

    for i, val in enumerate(reversed(starfruit_cache)): 
        nxt_price += val * coef[n-1-i]
            
    return int(round(nxt_price)) #the price sent must be an integer. round function with no specified number rounds to NEAREST INTEGER

print(calc_next_price_starfruit(starfruit_cache))