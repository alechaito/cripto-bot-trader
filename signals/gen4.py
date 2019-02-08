from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
import ccxt
from Signal import Signal as _SIGNAL
import time
import os
import pandas as pd
from datetime import datetime as dt
import MySQLdb as mysql
from datetime import timedelta
import pytz

_BINANCE = ccxt.binance({'enableRateLimit':True})

PAIRS = {
    'BTC': ['ADA', 'BNB', 'XLM', 'EOS', 'ETH', 'ETC', 'XRP', 'VET', 'QKC', 'BCH', 'IOTA', 'LTC'],
    'USDT': ['BTC', 'ETH', 'XLM', 'BCH', 'EOS', 'TRX', 'XRP', 'IOTA', 'NEO'],
}


def main():
    write_pid()
    while(True):
        date_utc = dt.utcnow()
        date_end = time_now().replace(seconds=1)
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
        

def bt_prepare(symbol):
    # Loading data to backtrader from exchange using CCXT
    candles = get_candles(symbol, '1h')
    last_candle = candles[-2]
    # Verify if is a positive candle
    if(last_candle[1] < last_candle[4]):
        var = perc(last_candle[1], last_candle[4])
        log("[+] %s, var:%.8f"% (symbol, var))
        if(var >= 2):
            symbol = str(symbol).split("/")
            buy_signal(symbol)

def perc(entry, close):
    x = close*100/entry
    if x < 100:
        x = float(-1*(100-x))
    elif x > 100:
        x = float(x-100)
    else:
        x = float(0)
    return x

def buy_signal(symbol):
        params = {
            'market': symbol[1],
            'currency': symbol[0],
            'strategy': sys.argv[1],
            'side': 0,
            'timeframe': '1h',
        }
        Signal = _SIGNAL(params)
        if(Signal.new()):
            Signal.insert()

def log(msg):
    brasil = pytz.timezone('America/Sao_Paulo')
    now = dt.now(tz=brasil).strftime('%Y-%m-%d %H:%M:%S')
    file = open('/home/signals/logs/'+str(sys.argv[1])+'.log', 'a+')
    file.write('['+str(now)+'] ' + msg + "\n")

def write_pid():
    file = open('/home/signals/pids/'+str(sys.argv[1])+'.pid', 'w')
    file.write(str(os.getpid()))


def to_datetimeindex(unixtimestamp):
    t = dt.fromtimestamp(unixtimestamp / 1e3)
    return t.strftime("%Y-%m-%d %H:%M:%S")

def to_Timestamp (stringtime):
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
    query = ("DELETE FROM signals WHERE strategy=4")
    cursor.execute(query, )
    db.commit()
    cursor.close()



main()