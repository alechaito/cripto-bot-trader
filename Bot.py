import Database as _DATABASE
import Order as _ORDER
import Exchange as _EXCHANGE
from datetime import datetime as dt
from datetime import timedelta
import time
import pytz
import Helper as _HELPER
import User as _USER


		
class Bot():
	def __init__(self, params=None):
		self.id = params['id']
		self.user_id = params['user_id']
		self.exchange = params['exchange']
		self.strategy = params['strategy']
		self.pid = params['pid']
		self.status = params['status']
		self.binance = _EXCHANGE.Exchange()

		
	def buy_routine(self):
		_HELPER.log("Iniciando rotina de compra...")
		USER = _USER.User(self.user_id)
		# 1 - LOAD SIGNALS
		SIGNALS = self.load_signals(0)
		#PROCESSAR SINAIS
		for signal in SIGNALS:
			# 2 - CHECK BUY
			if(self.free_buy(signal['market'], signal['currency']) == 1):
				PAIR = signal['currency']+'/'+signal['market']
				PRICE_NOW = self.binance.price_buy(PAIR)
				if(self.status == 1):
					INVEST = USER.manage_balance(signal['market'])
				if(self.status == 2):
					if(signal['market'] == 'BTC'):
						INVEST = 0.01
					if(signal['market'] == 'USDT'):
						INVEST = 300.0
				AMOUNT = INVEST/float(PRICE_NOW)
				params = {
					'id': None,
					'bot_id': self.id,
					'market': signal['market'],
					'currency': signal['currency'],
					'buy_value': PRICE_NOW,
					'sell_value': None,
					'amount': AMOUNT,
					'status': 0,
					'date': None,
				}
				Order = _ORDER.Order(params)
				Order.execute_buy(self.status, self.id)

	def sell_routine(self):
		_HELPER.log("Iniciando rotina de venda...")
		ORDERS = self.load_orders()
		for Order in ORDERS:
			## FREE TO SELL ORDER
			if(self.free_sell() == 0):
				# Select the profit and stoploss bot mode
				profit = self.select_profit(Order)
				stoploss = self.select_stoploss(Order)
				PAIR = Order.currency+'/'+Order.market
				# Sell by stoploss, select and sell
				if(stoploss == 1 or profit == 1):
					Order.sell_value = self.binance.price_sell(PAIR)
					Order.status = 1
					Order.execute_sell(self.status)


	# CHECAGEM PARA LIBERACAO DE VENDA
	# 0: LIVRE | 1: IMPEDIDO
	def free_buy(self, market, currency):
		Database = _DATABASE.Database()
		USER = _USER.User(self.user_id)
		_HELPER.log("Checando se o sinal ja foi utilizado para %s-%s..."% (market, currency))

		# 2-STEP: CHECK IF EXIST OPEN ORDER FOR PAIR, RETURN 0 IF TRUE
		COUNT_ORDER = Database.get_order_pair(self.id, market, currency)
		# -STEP: CHECK IF THE SIGNAL FLAG USED, RETURN OBJ IF TRUE
		SIGNAL_USED = Database.check_queue(self.id)
		#INVEST = USER.manage_balance(market)

		if(COUNT_ORDER > 0):
			_HELPER.log("Temos uma ordem aberta de compra aberta para o par: %s-%s"% (market, currency))
			return 0

		# CHECK IF SIGNAL FLAG IS USED
		if(SIGNAL_USED != None):
			_HELPER.log("Venda ja concluida e sinal ja foi utilizado: %s-%s..."% (market, currency))
			return 0
		
		# CHECK BALANCE IF IS MORE THAN MIN VALUE 30USD
		#if(INVEST == 0 and self.status == 1):
		#return 0
			
		return 1


	# CHECAGEM PARA LIBERACAO DE COMPRA
	# 0: LIVRE | 1: IMPEDIDO
	def free_sell(self):
		# SEM NENHUMA REGRA DEFINIDA AINDA
		return 0
		#########################

	def load_signals(self, side):
		Database = _DATABASE.Database()
		_HELPER.log("Filtrando sinais...")
		Database.filter_queue(self.id)
		_HELPER.log("Carregando sinais...")
		SIGNALS = Database.get_signals(self.strategy, side)
		_HELPER.log("Sinais carregados com sucesso...")
		if(side == 0):
			_HELPER.log("--------SIGNAL BOOK BUY----------------")
		else:
			_HELPER.log("--------SIGNAL BOOK SELL----------------")
		_HELPER.log(str(SIGNALS))
		_HELPER.log("--------------------------------- ")
		return SIGNALS
	
	def load_orders(self):
		Database = _DATABASE.Database()
		_HELPER.log("Carregando ordens...")
		ORDERS = Database.get_open_orders(self.id)
		_HELPER.log("Ordens carregados com sucesso...")
		_HELPER.log("--------Ordens Abertas------------")
		if(ORDERS == None):
			return []
		for Order in ORDERS:
			PAIR = Order.currency+'/'+Order.market
			PRICE = self.binance.price_buy(PAIR)
			_HELPER.log("SYMBOL:%s/%s, BUY_VALUE:%.8f"% (Order.currency, Order.market, Order.buy_value))
		_HELPER.log("---------------------------------")
		return ORDERS
	

	def select_profit(self, Order):
		PAIR = Order.currency+'/'+Order.market
		#############
		if(self.strategy == 2):
			if(self.binance.mov_profit(PAIR)):
				_HELPER.log("Lucro movel ativado...")
				return 1
		if(self.strategy == 4):
			if(self.binance.fix_profit(PAIR, Order.buy_value, 0.005)):
				_HELPER.log("Lucro fixo ativado...")
				return 1
		return 0
	
	def select_stoploss(self, Order):
		PAIR = Order.currency+'/'+Order.market
		if(self.strategy == 2):
			stop = Order.buy_value*0.98
			_HELPER.log("Stop in %.8f..."% stop)
			if(stop >= self.binance.price_sell(PAIR)):
				_HELPER.log("Stop in loss 2%...")
				return 1
		if(self.strategy == 4):
			time_now = dt.strptime(str(_HELPER.time_now()), '%Y-%m-%d %H:%M:%S')
			time_order = dt.strptime(str(Order.date), '%Y-%m-%d %H:%M:%S')
			elapsed = time_now-time_order
			if(elapsed > timedelta(hours=3)):
				_HELPER.log("Stop in time ativado...")
				return 1
		return 0
