from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import math
import backtrader as bt
from Signal import Signal as _SIGNAL
import logging
import pytz
from datetime import datetime as dt

# Create a Stratey
class Strategy(bt.Strategy):

    params = (
        ('period',21),
        ('pair', None),
        ('date', None)
    )
    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.close = self.datas[0].close
        self.low = self.datas[0].low
        self.high = self.datas[0].high
        self.date = self.datas[0].datetime
        self.rsi_lag = bt.indicators.LaguerreRSI(self.datas[0])

    def next(self):
        global COUNT

        BUY_SIGNAL = self.rsi_lag[0] <= 0.0


        date = str(self.data.num2date(self.date[0]).date().isoformat())
        hour = str(self.data.num2date(self.date[0]).time().isoformat())
        if(str(self.p.date) == date+' '+hour):
            pair = str(self.p.pair).split("/")
            self.log("COMPRA %s | Date:%s, LAG:%.2f"% (pair, self.p.date, self.rsi_lag[0]))
            if(BUY_SIGNAL):
                self.buy_signal(pair)
    
    def buy_signal(self, pair):
        params = {
            'market': pair[1],
            'currency': pair[0],
            'strategy': sys.argv[1],
            'side': 0,
            'timeframe': '1h',
        }
        Signal = _SIGNAL(params)
        if(Signal.new()):
            Signal.insert()
            self.log("Inserindo sinal...")

    def log(self, msg):
        brasil = pytz.timezone('America/Sao_Paulo')
        now = dt.now(tz=brasil).strftime('%Y-%m-%d %H:%M:%S')
        file = open('/home/signals/logs/'+str(sys.argv[1])+'.log', 'a+')
        file.write('['+str(now)+'] ' + msg + "\n")