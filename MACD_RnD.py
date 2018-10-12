# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 21:34:46 2018

@author: teddy
"""

import numpy as np
import pandas as pd
from yahoo_fin import stock_info as si
import datetime
from read_live_price import read_live_price
import time

#%% build tickers to trade
tickers = ['AAPL', 'MU', 'AMD']


#%% set porfolio from yesterday
portfolio = pd.read_csv('D:/Trading/portfolio/portfolio_20181009.csv')

#%% main function of MACD
macd_table = pd.DataFrame(columns=tickers)
price_table = pd.DataFrame(columns=tickers)
shares_tracking = pd.DataFrame(columns=tickers)
shares_tracking.loc[datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)] = [0,0,0]
money_tracking = pd.DataFrame(columns=tickers)

open_time = datetime.datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
trade_start = datetime.datetime.now().replace(hour=10, minute=00, second=0, microsecond=0)
trade_close = datetime.datetime.now().replace(hour=23, minute=50, second=0, microsecond=0)

money = {}

for ticker in tickers:
    money[ticker] = float(portfolio[ticker])

while datetime.datetime.now() >= open_time:
    start_time_record = time.time()
    
    shares_buy = 0
    shares_sell = 0
    
    time_now = datetime.datetime.now().strftime("%H:%M")
    # get price
    price_table.loc[time_now] = read_live_price(tickers)
    
    # calculating the MACD
    macd_line = pd.ewma(price_table, 12) - pd.ewma(price_table, 25)
    macd_table = macd_line - pd.ewma(macd_line, 5)
    
    shares_now = []
    
    print_context = []
    
    if datetime.datetime.now() >= trade_start:
        
        if len(macd_table) > 1:
        
            for ticker in tickers:
                
                if macd_table.ix[-1, ticker] < 0 and macd_table.ix[-2,ticker] > 0:
                    signal_now = 'BUY'
                    
                elif macd_table.ix[-1, ticker] > 0 and macd_table.ix[-2,ticker] < 0:
                    signal_now = 'SELL'
                    
                else:
                    signal_now = 'HOLD'
                    
                if signal_now == 'BUY':
                    shares_buy = int(money[ticker] / price_table.ix[-1, ticker])
                    shares_now.append(shares_tracking.ix[-1,ticker]+shares_buy)
                    money[ticker] = money[ticker] - shares_buy*price_table.ix[-1, ticker]
                    print(time_now)
                    print(ticker + ' -BUY- ' + str(shares_buy))
                    print(money)
                    
                elif signal_now == 'SELL':
                    shares_sell = shares_tracking.ix[-1, ticker]
                    shares_now.append(shares_tracking.ix[-1,ticker]-shares_sell)
                    money[ticker] = money[ticker] + shares_sell*price_table.ix[-1, ticker]
                    print(time_now)
                    print(ticker + ' -SELL- ' + str(shares_sell))
                    print(money)
                    
                else:
                    #shares_tracking.loc[time_now]
                    shares_now.append(shares_tracking.ix[-1,ticker])
                        
            shares_tracking.loc[time_now] = shares_now
            money_tracking.loc[time_now] = list(money.values())
        
    now_ = datetime.datetime.now().hour*60+datetime.datetime.now().minute
    time_now_int = int(time_now.split(':')[0])*60+int(time_now.split(':')[1])
    
    while now_ <= time_now_int:
        now_ = datetime.datetime.now().hour*60+datetime.datetime.now().minute
        time.sleep(1)
        
    if datetime.datetime.now() >= trade_close:
        for ticker in tickers:
            if shares_tracking.ix[-1,ticker] > 0:
                shares_sell = shares_tracking.ix[-1, ticker]
                shares_now.append(shares_tracking.ix[-1,ticker]-shares_sell)
                money[ticker] = money[ticker] + shares_sell*price_table.ix[-1, ticker]
                print(time_now)
                print(ticker+' -SELL- '+shares_sell)
                print(money)
        break
    
print(money)
            
            


