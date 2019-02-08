import Database as _DATABASE
import Exchange as _EXCHANGE
import Helper as _HELPER
		
class User():
	def __init__(self, user_id):
		user = _DATABASE.Database().get_user(user_id)
		self.id = user['id']
		self.key = user['key']
		self.secret = user['secret']
		self.credits = user['credits']
		self.balance_btc = user['balance_btc']
		self.balance_usdt = user['balance_usdt']
		self.binance = _EXCHANGE.Exchange()
	
	def manage_balance(self, market):
		Balance = self.binance.balance()
		_HELPER.log("Disponivel na conta: %.8f"% Balance[market])
		PCT = [0.05, 0.1, 0.25, 0.5, 0.75, 1.0]
		if(market == 'BTC'):
			invest = self.balance_btc*0.3
		else:
			invest = self.balance_usdt*0.3
		# 1 - Primeira tentativa e de investir 25% e assim sucessivamente
		for p in PCT:
			invest = invest*p
			# Checamos o total do balance para abrir ordens sempre de no minimo 20USD
			_HELPER.log("Dimensionamos o capital para %.8f"% invest)
			if(self.check_amount(invest, market) == True):
				# No primeiro positivo partindo dos 25% faremos o retorno do total
				_HELPER.log("Sucesso vou investir: %.8f"% invest)
				return invest
		else:
			# Retornar 0 para bloquear uma compra
			_HELPER.log("Erro no dimensionamento de capital")
			return 0
	
	def check_amount(self, invest_value, market):
		if(market == 'BTC'):
			usdt = invest_value*self.binance.price('BTC/USDT')
			if(usdt < 20.0):
				_HELPER.log("BTC - Saldo baixo menor que $20:%.2f"% usdt)
				return False
		if(market == 'USDT'):
			if(invest_value < 20.0):
				_HELPER.log("USDT - Saldo baixo menor que $20:%.2f"% invest_value)
				return False
		return True
	
	def fee(self, Order):
		profit = (Order.sell_value-Order.buy_value)*Order.amount
		# Retirar lucro somente se o trader for vencedor
		if(profit > 0):
			fee = 0
			Database = _DATABASE.Database()
			if(Order.market == 'BTC'):
				# Conveting profit value satochi to usdt
				fee = (profit*self.binance.price_buy('BTC/USDT'))*0.2
			else:
				fee = profit*0.2
			# Apply fee direct in database, in a user account
			_HELPER.log("Fee aplicado, ordem com lucro:%.2f"% fee)
			Database.apply_fee(fee, self.credits)

