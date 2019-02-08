import ccxt as _CCXT
import sys
import pandas as pd
import User as _USER
import time
import Helper as _HELPER
import warnings
warnings.filterwarnings("always")
		
class Exchange():
	def __init__(self, params=None):
		self.binance = _CCXT.binance()

	def price_buy(self, pair):
		return self.binance.fetch_ticker(pair)['ask']
	
	def price_sell(self, pair):
		return self.binance.fetch_ticker(pair)['bid']

	def balance(self):
		balance = self.auth().fetch_balance()['free']
		result = { 
			'BTC': float(balance['BTC']),
			'USDT': float(balance['USDT']),
		}
		_HELPER.log("BTC Disponivel: %.8f"% (balance['BTC']))
		_HELPER.log("USDT Disponivel: %.2f"% (balance['USDT']))
		return result
	
	def send_buy_order(self, params):
		# Example
		# order = self.binance_auth().create_order('ADA/USDT', 'limit', 'buy', 100.0, 0.13)
		Order = self.auth().create_limit_buy_order(
			params['symbol'], 
			params['amount'], 
			params['price'],
			{'timeInForce': 'FOK'}
		)['info']
		_HELPER.log("Ordem real:%s"% Order)
		# 2 min delay to check Order Status
		time.sleep(30)
		# CHECK IF ORDER IS EXECUTED BY FOK: FILL OR KILL STATMENT
		if(Order['status'] == 'EXPIRED'):
			#self.auth().cancel_order(ID, params['symbol'])
			return False, None
		# Return order details if sucees in execute order
		return True, Order['orderId']
	
	def send_sell_order(self, params):
		# Example
		Order = self.auth().create_limit_sell_order(
			params['symbol'], 
			params['amount'], 
			params['price'],
			{'timeInForce': 'FOK'}
		)['info']
		_HELPER.log("Ordem real:%s"% Order)
		# 2 min delay to check Order Status
		time.sleep(20)
		# CHECK IF ORDER IS EXECUTED BY FOK: FILL OR KILL STATMENT
		if(Order['status'] == 'EXPIRED'):
			#self.auth().cancel_order(ID, params['symbol'])
			return False, None
		# Return order details if sucees in execute order
		return True, Order['orderId']
		

	def auth(self):
		User = _USER.User(sys.argv[2])
		_BINANCE = _CCXT.binance({
			'apiKey': User.key,
    		'secret': User.secret,
			#'recvWindow': 10000000,
		})
		# Adjust time for windows http head time security setup for binance API 3.0
		#_BINANCE.nonce = lambda: _BINANCE.milliseconds() - 1000
		return _BINANCE
	
	def get_order(self, idx, symbol):
		order = self.auth().fetch_order(idx, symbol)
		return order['info']

	def mov_profit(self, pair):
		ohlcv = self.binance.fetch_ohlcv(pair, '1h')
		candles = pd.DataFrame(ohlcv)
		HIGHS = []
		HIGHS.append(candles[2][candles.index[-2]]) # CANDLE 1 HOUR LATER
		HIGHS.append(candles[2][candles.index[-3]]) # CANDLE 2 HOUR LATER
		HIGH_NOW = candles[2][candles.index[-1]] # HIGH PRICE CANDLE IN REAL TIME
		_HELPER.log("Venda movel %s | LAST HIGH:%.8f | HIGHEST_SELL:%.8f"% (pair, HIGH_NOW, max(HIGHS)))
		if(HIGH_NOW >= max(HIGHS)):
			return True
		return False
	
	def fix_profit(self, pair, buy_value, profit):
		price = self.price_sell(pair)
		profit = buy_value*(1+profit)
		_HELPER.log("Venda fixa %s | PRICE:%.8f | ALVO:%.8f"% (pair, buy_value, profit))
		if(price >= profit):
			return True
		return False

	