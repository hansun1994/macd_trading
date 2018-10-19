# -*- coding: utf-8 -*-
"""
Created on Tue Oct  9 21:34:46 2018

@author: teddy
"""

import numpy as np
import pandas as pd
import datetime
from read_live_price import read_live_price_all, read_live_price_single
import time
#from yahoo_fin import stock_info as si

#%% set porfolio from yesterday
portfolio = pd.read_csv('H:/Private/trading/macd_trading/portfolio_20181009.csv')
#portfolio = pd.read_csv('D:/Trading/macd_trading/portfolio_20181009.csv')
#parameter = pd.read_csv('D:/Trading/macd_trading/parameter.csv', index_col = 0)
parameter = pd.read_csv('H:/Private/trading/macd_trading/parameter.csv', index_col = 0)
tickers = list(parameter.index)
            
#%%
macd_table = pd.DataFrame(columns=tickers)
price_table = pd.DataFrame(columns=tickers)
shares_tracking = pd.DataFrame(columns=tickers)
shares_tracking.loc[datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)] = [0]*len(tickers)
money_tracking = pd.DataFrame(columns=tickers)
money = {}

open_time = datetime.datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
trade_start = datetime.datetime.now().replace(hour=9, minute=45, second=0, microsecond=0)
trade_close = datetime.datetime.now().replace(hour=15, minute=50, second=0, microsecond=0)

for ticker in tickers:
    money[ticker] = float(portfolio[ticker])
    
while datetime.datetime.now() < open_time:
    time.sleep(0.0001)

while datetime.datetime.now() >= open_time:
    
    start_time_record = time.time()
    
    shares_buy = 0
    shares_sell = 0
    
    time_now = datetime.datetime.now().strftime("%H:%M:%S")
    #print(time_now)
    print(datetime.datetime.now().strftime("%H:%M:%S:%f"))
    
    # get price
    price_table.loc[time_now] = read_live_price_all(tickers)
    
    macd_table_dic = {}
    
    # calculating the MACD
    for ticker in tickers:
        fast = parameter.loc[ticker, 'Fast']
        slow = parameter.loc[ticker, 'Slow']
        signal = parameter.loc[ticker, 'Signal']
        macd_line = pd.ewma(price_table[ticker], fast) - pd.ewma(price_table[ticker], slow)
        macd_table_dic[ticker] = macd_line - macd_line.rolling(window = signal).mean()
    
    macd_table = pd.DataFrame(macd_table_dic)
    
    shares_now = []
    
    print_context = []
    
    if datetime.datetime.now() >= trade_start:
        
        if len(macd_table) > 1:
        
            for ticker in tickers:
                
                if macd_table.ix[-1, ticker] < 0 and macd_table.ix[-1, ticker] > macd_table.ix[-2,ticker]:
                    signal_now = 'BUY'
                    
                elif macd_table.ix[-1, ticker] > 0 and macd_table.ix[-1, ticker] < macd_table.ix[-2,ticker]:
                    signal_now = 'SELL'
                    
                else:
                    signal_now = 'HOLD'
                    
                if signal_now == 'BUY':
                    shares_buy = int(money[ticker] / price_table.ix[-1, ticker])
                    shares_now.append(shares_tracking.ix[-1,ticker]+shares_buy)
                    
                    time.sleep(3)
                    
                    money[ticker] = money[ticker] - shares_buy*read_live_price_single(ticker)
                    if shares_buy > 0:
                        print(time_now)
                        print(ticker + ' -BUY- ' + str(shares_buy))
                        print(money)
                    
                elif signal_now == 'SELL':
                    shares_sell = shares_tracking.ix[-1, ticker]
                    shares_now.append(shares_tracking.ix[-1,ticker]-shares_sell)
                    
                    time.sleep(3)
                    
                    money[ticker] = money[ticker] + shares_sell*read_live_price_single(ticker)
                    if shares_sell > 0:
                        print(time_now)
                        print(ticker + ' -SELL- ' + str(shares_sell))
                        print(money)
                    
                else:
                    shares_now.append(shares_tracking.ix[-1,ticker])
                        
            shares_tracking.loc[str(time_now)] = shares_now
            money_tracking.loc[str(time_now)] = list(money.values())
    
    now_ = datetime.datetime.now().hour*3600+datetime.datetime.now().minute*60+datetime.datetime.now().second
    time_now_int = int(time_now.split(':')[0])*3600+int(time_now.split(':')[1])*60+int(time_now.split(':')[2])+29.5
    
    while now_ <= time_now_int:
        now_ = datetime.datetime.now().hour*3600+datetime.datetime.now().minute*60+datetime.datetime.now().second
        time.sleep(0.1)
        
    if datetime.datetime.now() >= trade_close:
        for ticker in tickers:
            if shares_tracking.ix[-1,ticker] > 0:
                shares_sell = shares_tracking.ix[-1, ticker]
                shares_now.append(shares_tracking.ix[-1,ticker]-shares_sell)
                
                time.sleep(3)
                
                money[ticker] = money[ticker] + shares_sell*read_live_price_single(ticker)
                print(time_now)
                print(ticker+' -SELL- '+str(shares_sell))
                print(money)
        break
    
print(money)
portfolio_return = round((sum(money.values())-float(portfolio.sum(1)))*100/float(portfolio.sum(1)),2)
print('Daily portfolio return: ' + str(portfolio_return)+'%')

daily_return = {}

for ticker in tickers:
    dr = round(float((money[ticker]-portfolio[ticker])*100/portfolio[ticker]),2)
    daily_return[ticker] = dr

#%% plot result
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm

ticker = 'AMD'

points = np.array([range(len(price_table)), price_table[ticker]]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)

cmap = ListedColormap(['r', 'g'])
norm = BoundaryNorm([-1, 0, 1], cmap.N)
lc = LineCollection(segments, cmap=cmap, norm=norm)
lc.set_array(macd_table[ticker].diff())
lc.set_linewidth(2)

fig = plt.figure()
plt.gca().add_collection(lc)

plt.xlim(0, len(price_table)-1)
plt.ylim(price_table[ticker].min(), price_table[ticker].max())
plt.legend('Daily Return: ' + str(daily_return[ticker])+'%', loc = 'upper left')
plt.show()


#%%
tickers = ['AAPL','MU','AMD']
macd_table_t = pd.DataFrame(columns=tickers)
price_table_t = pd.DataFrame(columns=tickers)
shares_tracking_t = pd.DataFrame(columns=tickers)
shares_tracking_t.loc[datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)] = [0]*len(tickers)
money_tracking_t = pd.DataFrame(columns=tickers)
money = {}

price_table = pd.read_csv('D:/Trading/macd_trading/price_20181017.csv', index_col = 0)

open_time = datetime.datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
trade_start = datetime.datetime.now().replace(hour=10, minute=00, second=0, microsecond=0)
trade_close = datetime.datetime.now().replace(hour=23, minute=50, second=0, microsecond=0)

for ticker in tickers:
    money[ticker] = float(portfolio[ticker])

n = 0

while n <= 379:
    
    start_time_record = time.time()
    
    shares_buy = 0
    shares_sell = 0
    
    time_now = datetime.datetime.now().strftime("%H:%M:%S")
    #print(time_now)
    #print(datetime.datetime.now().strftime("%H:%M:%S:%f"))
    
    # get price
    price_table_t.loc[str(n)] = price_table.iloc[n]
    
    macd_table_dic_t = {}
    
    # calculating the MACD
    for ticker in tickers:
        fast = parameter.loc[ticker, 'Fast']
        slow = parameter.loc[ticker, 'Slow']
        signal = parameter.loc[ticker, 'Signal']
        macd_line_t = pd.ewma(price_table_t[ticker], fast) - pd.ewma(price_table_t[ticker], slow)
        macd_table_dic_t[ticker] = macd_line_t - macd_line_t.rolling(window = signal).mean()
    
    macd_table_t = pd.DataFrame(macd_table_dic_t)
    macd_pct_t = macd_table_t.pct_change()
    
    shares_now = []
    
    print_context = []
    
    if n >= 30:
        
        if len(macd_table_t) > 1:
        
            for ticker in tickers:
                
                if macd_table_t.ix[-1, ticker] < 0 and macd_table_t.ix[-1, ticker] > macd_table_t.ix[-2,ticker]:
                    signal_now = 'BUY'
                    
                elif macd_table_t.ix[-1, ticker] > 0 and macd_table_t.ix[-1, ticker] < macd_table_t.ix[-2,ticker]:
                    signal_now = 'SELL'
                    
                else:
                    signal_now = 'HOLD'
                    
                if signal_now == 'BUY':
                    shares_buy = int(money[ticker] / price_table_t.ix[-1, ticker])
                    shares_now.append(shares_tracking_t.ix[-1,ticker]+shares_buy)
                    
                    #time.sleep(3)
                    
                    money[ticker] = money[ticker] - shares_buy*price_table_t.ix[-1,ticker]
                    if shares_buy > 0:
                        #print(time_now)
                        print(ticker + ' -BUY- ' + str(shares_buy))
                        print(money)
                    
                elif signal_now == 'SELL':
                    shares_sell = shares_tracking_t.ix[-1, ticker]
                    shares_now.append(shares_tracking_t.ix[-1,ticker]-shares_sell)
                    
                    #time.sleep(3)
                    
                    money[ticker] = money[ticker] + shares_sell*price_table_t.ix[-1,ticker]
                    if shares_sell > 0:
                        #print(time_now)
                        print(ticker + ' -SELL- ' + str(shares_sell))
                        print(money)
                    
                else:
                    shares_now.append(shares_tracking_t.ix[-1,ticker])
                        
            shares_tracking_t.loc[str(n)] = shares_now
            money_tracking_t.loc[str(n)] = list(money.values())
    
    #now_ = datetime.datetime.now().hour*3600+datetime.datetime.now().minute*60+datetime.datetime.now().second
    #time_now_int = int(time_now.split(':')[0])*3600+int(time_now.split(':')[1])*60+int(time_now.split(':')[2])+29.5
    
    #while now_ <= time_now_int:
    #    now_ = datetime.datetime.now().hour*3600+datetime.datetime.now().minute*60+datetime.datetime.now().second
    #    time.sleep(0.1)
        
    if n>=369:
        for ticker in tickers:
            if shares_tracking_t.ix[-1,ticker] > 0:
                shares_sell = shares_tracking_t.ix[-1, ticker]
                shares_now.append(shares_tracking_t.ix[-1,ticker]-shares_sell)
                
                #time.sleep(3)
                
                money[ticker] = money[ticker] + shares_sell*price_table_t.ix[-1,ticker]
                #print(time_now)
                print(ticker+' -SELL- '+str(shares_sell))
                print(money)
        break
    
    n += 1
    
print(money)



#%%
ticker_t = 'AAPL'

points = np.array([range(370), price_table_t[ticker_t]]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)

cmap = ListedColormap(['r', 'g'])
norm = BoundaryNorm([-1, 0, 1], cmap.N)
lc = LineCollection(segments, cmap=cmap, norm=norm)
lc.set_array(macd_table_t[ticker_t].diff())
lc.set_linewidth(2)

fig = plt.figure()
plt.gca().add_collection(lc)

plt.xlim(0, 369)
plt.ylim(price_table_t[ticker_t].min(), price_table_t[ticker_t].max())
plt.legend(['Daily Return: ' + str(round(float((money[ticker_t]-portfolio[ticker_t])*100/portfolio[ticker_t]),2))+'%'],loc='upper left')
plt.show()