from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
import ccxt
import backtrader as bt
import backtrader.feeds as btfeed
import Signal as _SIGNAL
import time
import stt2
import pandas as pd
from datetime import datetime as dt
import MySQLdb as mysql
from datetime import timedelta
import logging
import pytz
import os

_BINANCE = ccxt.binance({'enableRateLimit':True})

PAIRS = {
    'BTC': [],
    'USDT': ['ADA', 'XLM', 'BNB', 'IOTA', 'NEO', 'XRP', 'EOS', 'ETC', 'ICX', 'LTC', 'BTC', 'ETH', 'BCH'],
}

def main():
    write_pid()
    while(True):
        date_utc = dt.utcnow()
        date_end = time_now().replace(minute=5)
        elapsed = date_end-date_utc
        log("Gerador de sinais time:%s"% elapsed)
        time.sleep(10)
        if(date_utc < date_end):
            delete()
            for currency in PAIRS['BTC']:
                pair = str(currency+"/BTC")
                bt_prepare(pair)

            for currency in PAIRS['USDT']:
                pair = str(currency+"/USDT")
                bt_prepare(pair)
            log("Gerei os sinais vou aguardar 10 minutos.")
            time.sleep(600)

def bt_prepare(pair):
    cerebro = bt.Cerebro(stdstats=False)
    _STRATEGY = stt2.Strategy

    cerebro.addstrategy(_STRATEGY)
    cerebro.addsizer(bt.sizers.SizerFix, stake=1)

    # Loading data to backtrader from exchange using CCXT
    matrix = get_candles(pair, '1h')
    candles = pd.DataFrame(matrix)
    candles[0] = candles[0].apply(to_datetimeindex)
    candles[0] = candles[0].apply(to_timestamp)
    date = candles[0][candles.index[-2]]

    cerebro.addstrategy(_STRATEGY, date=date, pair=pair)
    cerebro.addsizer(bt.sizers.SizerFix, stake=1)

    data = data_feed(dataname=candles, nocase=False)
    cerebro.adddata(data)
    # Run over everything
    cerebro.run()
    #cerebro.plot()


def log(msg):
    brasil = pytz.timezone('America/Sao_Paulo')
    now = dt.now(tz=brasil).strftime('%Y-%m-%d %H:%M:%S')
    file = open('/home/signals/logs/'+str(sys.argv[1])+'.log', 'a+')
    file.write('['+str(now)+'] ' + msg + "\n")


def write_pid():
    file = open('/home/signals/pids/'+str(sys.argv[1])+'.pid', 'w')
    file.write(str(os.getpid()))


class data_feed(btfeed.PandasData):
    params = (
        ('nocase', False),
        ('datetime', 0),
        ('open', 1),
        ('high', 2),
        ('low', 3),
        ('close', 4),
        ('volume', 5),
        ('openinterest', -1)
    )


def to_datetimeindex(unixtimestamp):
    t = dt.fromtimestamp(unixtimestamp / 1e3)
    return t.strftime("%Y-%m-%d %H:%M:%S")

def to_timestamp (stringtime):
    return pd.Timestamp(stringtime)


def get_candles(pair=None, timeframe=None):
    delay = int(_BINANCE.rateLimit / 1000)
    time.sleep(delay)
    return _BINANCE.fetch_ohlcv(pair, timeframe)

def time_now():
    return dt.utcnow().replace(minute=00, second=00)

			
def delete():
    db = mysql.connect(host="127.0.0.1", user="root", passwd="252528", db="protrader")
    cursor = db.cursor()
    query = ("DELETE FROM signals WHERE strategy=2")
    cursor.execute(query, )
    db.commit()
    cursor.close()

main()