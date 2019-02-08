import MySQLdb as mysql
import os
from datetime import datetime
from datetime import timedelta
import datetime as dt
import pytz
import sys
import Bot as _BOT
import Order as _ORDER
import Helper as _HELPER

class Database():

	def __init__(self):
		self.db = mysql.connect(host="127.0.0.1", user="root", passwd="252528", db="protrader")
		self.cursor = self.db.cursor()


	def open_order(self, Order, idx):
		query = ("INSERT INTO transactions (bot_id, market, currency, buy_value, amount, date_open, buy_uuid) VALUES (%s, %s, %s, %s, %s, %s, %s)")
		self.cursor.execute(query, (
			Order.bot_id,
			Order.market,
			Order.currency,
			Order.buy_value,
			Order.amount,
			_HELPER.time_now(),
			str(idx)
			)
		)
		self.db.commit()

	def close_order(self, Order, idx):
		query = ("UPDATE transactions SET sell_value=(%s), status=(%s), date_close=(%s), sell_uuid=(%s) WHERE id=(%s)")
		self.cursor.execute(query, (
			Order.sell_value, 
			Order.status,
			_HELPER.time_now(),
			str(idx),
			Order.id
			)
		)
		self.db.commit()


	def get_open_orders(self, bot_id):
		query = ("SELECT * FROM transactions WHERE bot_id = %s AND status = %s order by id desc")
		self.cursor.execute(query, (bot_id, 0))
		Orders = []
		if(self.cursor.rowcount > 0):
			for trans in self.cursor:
				params = {
					'id': trans[0],
					'bot_id': trans[1],
					'market': trans[2],
					'currency': trans[3],
					'buy_value': trans[4],
					'sell_value': trans[5],
					'amount': trans[6],
					'status': trans[7],
					'date': trans[8]
				}
				Order = _ORDER.Order(params)
				Orders.append(Order)
			return Orders	
		else:
			return None

	# VERIFICA SE EXISTE UMA ORDEM PENDENTE PARA O PAR SOLICITADO
	# PAIR: MARKET-CURRENCY
	def get_order_pair(self, bot_id, market, currency):
		query = ("SELECT * FROM transactions WHERE bot_id=%s AND market=%s AND currency=%s AND status=0 order by id desc")
		self.cursor.execute(query, (bot_id, market, currency))
		count = self.cursor.rowcount
		return count

	
	def get_order(self, order_id):
		query = ("SELECT * FROM transactions WHERE id = %s")
		self.cursor.execute(query, (bot_id, 0))
		trans = self.cursor.fetchone()
		params = {
			'id': trans[0],
			'bot_id': trans[1],
			'market': trans[2],
			'currency': trans[3],
			'buy_value': trans[4],
			'sell_value': trans[5],
			'amount': trans[6],
			'status': trans[7]
		}
		Order = _ORDER.Order(params)
		self.db.commit()
		count = self.cursor.rowcount
		return count


	def get_user(self, user_id):
		try:
			query = ("SELECT * FROM users WHERE id = %s")
			self.cursor.execute(query, (user_id,))
			data = self.cursor.fetchone()
			self.db.commit()
			obj = {
					'id': data[0],
					'key': data[7],
					'secret': data[8],
					'credits': data[9],
					'balance_btc': data[10],
					'balance_usdt': data[11],
				}
			return obj
		except:
			_HELPER.log.error("Error no get_user.")
			sys.exit()

	def get_bot(self, bot_id):
		query = ("SELECT * FROM bot WHERE id = %s")
		self.cursor.execute(query, (bot_id,))
		data = self.cursor.fetchone()
		self.db.commit()
		params = {
			'id': data[0],
			'user_id': data[1],
			'exchange': data[2],
			'strategy': data[3],
			'pid': data[4],
			'status': data[5],
		}
		return _BOT.Bot(params)

	def get_signals(self, strategy, side):
		db = mysql.connect(host="127.0.0.1", user="root", passwd="252528", db="protrader")
		cursor = db.cursor()
		SIGNALS = []
		query = ("SELECT * FROM signals WHERE strategy=(%s) AND side=(%s)")
		cursor.execute(query, (strategy, side))
		for sig in cursor:
			signal = {
				'id': sig[0],
				'market': sig[1],
				'currency': sig[2],
				'strategy': sig[3],
				'side': sig[4],
				'date': sig[5],
			}
			SIGNALS.append(signal)
		return SIGNALS

	
	def apply_fee(self, fee, credit):
		query = ("UPDATE users SET credits=(%s)")
		if(credit >= fee):
			# If credit are bigger than fee he update the credits with credits-fee
			self.cursor.execute(query, (credit-fee,))
		else:
			# If credit are smaller than fee he apply 0
			self.cursor.execute(query, (0,))
		self.db.commit()


	def set_pid(self, bot_id):
		try:
			pid = os.getpid()
			query = ("UPDATE bot SET pid=(%s) WHERE id=(%s)")
			self.cursor.execute(query, (pid, bot_id))
			self.db.commit()
			self.cursor.close()
		except:
			_HELPER.log.error("Erro no set_pid.")
			sys.exit()
	
	def check_queue(self, bot_id):
		query = ("SELECT id, date FROM queue WHERE bot_id=(%s)")
		self.cursor.execute(query, (bot_id, ))
		data = self.cursor.fetchone()
		return data

	def insert_queue(self, bot_id):
		_HELPER.log("Sinal adicionado na queue para previnir duplicacao.")
		query = ("INSERT INTO queue (bot_id, date) VALUES (%s, %s)")
		self.cursor.execute(query, (
			bot_id,
			_HELPER.time_replace(),
			)
		)
		self.db.commit()
	
	def filter_queue(self, bot_id):
		SIGNAL = self.check_queue(bot_id)
		if(SIGNAL != None):
			UTC = datetime.utcnow()
			elapsed = UTC - SIGNAL[1]
			_HELPER.log("Checando queue, ultimo sinal: %s"% (elapsed))
			if(elapsed > timedelta(minutes=60)):
				_HELPER.log("[+] Queu pode ser limpa, deletando, passaram: %s"% (elapsed))
				query = ("DELETE FROM queue WHERE id=%s")
				self.cursor.execute(query, (SIGNAL[0], ) )
				self.db.commit()
		else:
			_HELPER.log("Nao ha sinais em queue...")