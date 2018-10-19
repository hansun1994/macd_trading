# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 21:34:46 2018

@author: teddy
"""

from yahoo_fin import stock_info as si
import numpy as np
import pandas as pd

def read_live_price_all(tickers):
    live_px = []
    for ticker in tickers:
        result = None
        while result is None:
            try:
                result = si.get_live_price(ticker)
                live_px.append(result)
            except:
                pass
        
        
    return live_px

def read_live_price_single(ticker):
    
    result = None
    
    while result is None:
        try:
            result = si.get_live_price(ticker)
        except:
            pass
    
    return result