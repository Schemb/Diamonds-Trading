#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 18:43:08 2024

@author: michellenguyen
"""

import numpy as np 
import sympy as sy 
  
  
def f(x): 
    return x/95000

def definite_integral(low_limit,high_limit):
    x = sy.Symbol("x")
    return sy.integrate(  f(x) , (x, low_limit, high_limit)  )

print(definite_integral(900,1000), "check whether it is equal to 1")

def profit_per_item(low_bid,high_bid):
    result=definite_integral(900,low_bid)*(1000-low_bid) +definite_integral(low_bid,high_bid)*(1000-high_bid)
    return result


values_array=np.zeros([3,1]) #a 2-D array with 3 rows and 1 column.
#First row: the profit of each item
#second and third row: a pair of low bid and high bid with each corresponding profit

for low_bid in range(900,999,1): #low_bid can only range from 900 to 998
    for high_bid in range((low_bid+1),1000,1): #for each low_bid, high_bid ranges from low_bid+1 to 999
        pseudo=np.array([[float(profit_per_item(low_bid,high_bid))],
                         [low_bid],
                         [high_bid]])
        values_array=np.append(values_array, pseudo, axis=1)

highest_profit=max(values_array[0,:])


for column in range(values_array.shape[1]):
    if (values_array[0,column]==highest_profit):
        print("The highest profit is ", values_array[0,column]," with lowest bid ",values_array[1,column]," and highest bid", values_array[2,column])

        