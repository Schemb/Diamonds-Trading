import numpy as np
import pandas as pd
import statistics
import math
from typing import Dict, List
import jsonpickle
from datamodel import OrderDepth, UserID, TradingState, Order


# weighted average 
class Trader:

    def __init__(self):
        self.position_limit = {"AQUATIC AMETHYST": 20, "STAR FRUIT": 20}
        self.long_weigted_average = {"AQUATIC AMETHYST": 10000, "STAR FRUIT": }
