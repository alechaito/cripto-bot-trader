from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import math
import backtrader as bt
from datetime import timedelta
from Signal import Signal as _SIGNAL



# Create a Stratey
class Strategy(bt.Strategy):

    params = (
        ('period', 21),
        ('pair', None),
        ('date', None)
    )

    def __init__(self):
        self.ao = bt.indicators.AroonOsc(self.datas[0])
        self.hig = bt.indicators.Highest(self.datas[0].high, period=2)
        self.close = self.datas[0].close
        self.high = self.datas[0].high
        self.date = self.datas[0].datetime


    def next(self):
        BUY_SIGNAL = self.ao[0] <= -100.0
        SELL_SIGNAL = self.high[0] >= self.hig[0]

        date = str(self.data.num2date(self.date[0]).date().isoformat())
        hour = str(self.data.num2date(self.date[0]).time().isoformat())

        if(str(self.p.date) == date+' '+hour):
            pair = str(self.p.pair).split("/")
            print("[+] COMPRA %s | Date:%s, AO:%.2f"% (pair, self.p.date, self.ao[0]))
            #print("[+] VENDA %s | Date:%s, Close:%.8f, Highest:%.8f"% (pair, self.p.date, self.high[0], self.hig[0]))
            #print("[+] SINAL DE VENDA:%s"% SELL_SIGNAL)
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
            print("[+] COMPRA | Date:%s, AO:%.2f"% (self.p.date, self.ao[0]))
    
    def sell_signal(self, pair):
        params = {
            'market': pair[1],
            'currency': pair[0],
            'strategy': sys.argv[1],
            'side': 1,
            'timeframe': '1h',
        }
        Signal = _SIGNAL(params)
        BUY_SIG = Signal.get_buy()
        if(Signal.new() and BUY_SIG[0] > 0 and self.delta_time(BUY_SIG[1][6])):
            signal = Signal.get_buy
            Signal.insert()
            print("[+] VENDA | Date:%s, Close:%.8f, Highest:%.8f"% (self.p.date, self.high[0], self.hig[0]))
        else:
            print("sinal invalido")

    # CHECKING DELTA TIME FROM BUY AND SELL SIGNAL
    # DELTA > 60 = True | Delta < 60 = False
    def delta_time(self, date_signal):
        date_utc = datetime.datetime.utcnow()
        elapsed = date_utc-date_signal
        print("[+] Checando delta time do sinal de venda e compra...")
        if(elapsed > timedelta(minutes=60)):
            print("[+] Sinal de venda checkado, permissao para inserir, moeda:, delta:%s"% (elapsed))
            return True
        print("[+] Sinal de venda concatenado com o de compra, moeda:, delta:%s"% (elapsed))
        return False






