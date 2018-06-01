# -*- coding: utf-8 -*-
"""
Created on Sun May 13 23:32:15 2018

@author: user
"""

import pandas as pd
import talib as ta
import numpy as np
import json
import requests
import time
import matplotlib.pyplot as plt

class Macd:
    def macdget(self):
        #crypt watchから5分足のohlcを取得
        periods = 300
        periods = str(periods)
        query = {"periods":periods}
        repeat = True
        counter = 0
        while repeat == True:
            try:
                res = json.loads(requests.get("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc",params=query).text)["result"]
                data = pd.DataFrame(res['300'], columns = ["datetime","open","high","low","close","volume",'sum'])
                repeat = False
            except:
                print ('Cryptwatch data get error.')
                counter +=1
                #5分データ取れなかったらポジション解消
                if counter > 100:
                    print ('Cryptwatch data get Time OUT!!')
                    #return 'Exit'
                else:
                    time.sleep(3)

        #終値をnumpyのndarray形式に変更
        close = np.array(data['close'], dtype='f8')
        macd, macdsignal, macdhist = ta.MACD(close, fastperiod = 12, slowperiod = 26, signalperiod = 9)
        
        print (macd, macdsignal, macdhist)

MACD = Macd()
MACD.macdget()

def d(itv,src):
   from scipy.stats import rankdata
   sum = 0.0
   for i in range(itv, 0, -1):
       date_rank = itv - i + 1
       price_rank = (itv - rankdata(src)[i-1] + 1)
       sum = sum + pow( (date_rank - price_rank) ,2)
       #pprint("hiduke = {},  price={},  juni={},  goukei={}".format(date_rank, src[i-1], price_rank, sum) )

   return sum

def calc_rci(src, term):

    listnull = [None]
    itv = term
    rcinull = listnull * itv
    for i in range(itv,len(src)):
        rci_tmp = [   (1.0 - 6.0 * d(itv,src[i-itv:i]) / (itv * itv * itv - itv)) * 100.0]
        print(rci_tmp)
        rci = rcinull + rci_tmp
    return rci

def calc_rci(src, term):

    listnull = [None]
    itv = term
    rcinull = listnull * itv
    rci_tmp = [   (1.0 - 6.0 * d(itv,src[i-itv:i]) / (itv * itv * itv - itv)) * 100.0   for i in range(itv,len(src))]
    rci = rcinull + rci_tmp

    return rci