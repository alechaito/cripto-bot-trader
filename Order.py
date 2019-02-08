import Database as _DATABASE
import Exchange as _EXCHANGE
import Helper as _HELPER
import User as _USER
import sys
		
class Order():
	def __init__(self, params=None):
		self.id = params['id']
		self.bot_id = params['bot_id']
		self.market = params['market']
		self.currency = params['currency']
		self.buy_value = params['buy_value']
		self.sell_value = params['sell_value']
		self.amount = params['amount']
		self.status = params['status']
		self.date = params['date']
		self.binance = _EXCHANGE.Exchange()

	def execute_buy(self, bot_status, bot_id):
		Database = _DATABASE.Database()
		symbol = self.currency+"/"+self.market
		print("BOTAO STATUS E:%s"% bot_status)
		if(bot_status == 2):
			_HELPER.log("[execute_buy] Abrindo uma ordem simulada para o par: %s-%s"% (self.market, self.currency))
			Database.open_order(self, '2')
			Database.insert_queue(bot_id)
			return
		Success, ID = self.binance.send_buy_order({
			'symbol': symbol,
			'amount': self.amount,
			'price': self.buy_value,
		})
		if(Success == False):
			_HELPER.log.warning("[execute_buy] Ordem nao executada pelo livro: %s-%s"% (self.market, self.currency))
			return
		else:
			_HELPER.log("[execute_buy] Abrindo uma ordem real para o par: %s-%s"% (self.market, self.currency))
			Database.open_order(self, ID)
			Database.insert_queue(bot_id)
	
	def execute_sell(self, bot_status):
		Database = _DATABASE.Database()
		symbol = self.currency+"/"+self.market
		User = _USER.User(sys.argv[2])
		if(bot_status == 2):
			_HELPER.log("[execute_sell] Fechando uma ordem simulada para o par: %s-%s"% (self.market, self.currency))
			Database.close_order(self, '3')
			# Apply fee to user if trade as winner
			User.fee(self)
			return
		Success, ID = self.binance.send_sell_order({
			'symbol': symbol,
			'amount': self.amount*0.99,
			'price': self.sell_value,
		})
		if(Success == False):
			_HELPER.log.warning("[execute_sell] Ordem nao executada pelo livro: %s-%s"% (self.market, self.currency))
			return
		else:
			_HELPER.log("[execute_sell] Fechando uma ordem real para o par: %s-%s"% (self.market, self.currency))
			Database.close_order(self, ID)
			# Apply fee to user if trade as winner
			User.fee(self)

		
	def queue_signal(self):
		Database = _DATABASE.Database()
		Database.insert_queue(self.bot_id)
		return
	
	def get_precision(self):
		self.binance.load_markets()
		precision = self.binance.market(self.currency+"/"+self.market)['precision']['amount']
		return precision

	def check_precision(self):
		precision = float(self.get_precision())

		if (precision == 1):
			return int(self.amount)
		elif (precision == 2):
			self.amount = str(self.amount)[:4]
			return float(self.amount)
		elif(precision == 3):
			self.amount = str(self.amount)[:5]
			return float(self.amount)
		else:
			self.amount = str(self.amount)[:9]
			return float(self.amount)

		
