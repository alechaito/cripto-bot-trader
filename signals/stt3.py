from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import math
import backtrader as bt
from Signal import Signal as _SIGNAL

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

        self.vortex = bt.indicators.Vortex(self.datas[0])
        self.cross = bt.indicators.CrossOver(self.vortex.vi_plus, self.vortex.vi_minus)
        self.highest = bt.indicators.Highest(self.high, period=2)

    def next(self):
        global COUNT

        BUY_SIGNAL = self.cross[0] > 0
        #print(self.cross[0])


        date = str(self.data.num2date(self.date[0]).date().isoformat())
        hour = str(self.data.num2date(self.date[0]).time().isoformat())
        if(str(self.p.date) == date+' '+hour):
            pair = str(self.p.pair).split("/")
            #print("C:%s,hour:%s,pair:%s"% (self.cross[0], hour, pair))
            if(BUY_SIGNAL):
                params = {
                    'market': pair[1],
                    'currency': pair[0],
                    'strategy': 2,
                    'signal': 0,
                    'timeframe': '1h',
                }
                Signal = _SIGNAL(params)
                if(Signal.new()):
                    Signal.insert()
                    print("Date:%s, RSI_LAG:%.8f"% (self.p.date, self.cross[0]))