# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 21:34:46 2018

@author: teddy
"""

from yahoo_fin import stock_info as si
import numpy as np
import pandas as pd

def read_live_price(tickers):
    live_px = []
    for ticker in tickers:
        live_px.append(si.get_live_price(ticker))
        
    return live_px
