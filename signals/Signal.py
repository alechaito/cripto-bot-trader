import pandas as pd
from datetime import datetime
from datetime import timedelta

import MySQLdb as mysql
import os
import sys

class Signal():
	
	def __init__(self, params={}):
		self.market = params['market']
		self.currency = params['currency']
		self.strategy = params['strategy']
		self.side = params['side']
		self.timeframe = params['timeframe']

	# Get instance connection with database
	def get_socket(self):
		db = mysql.connect(host="127.0.0.1", user="root", passwd="", db="protrader")
		cursor = db.cursor()
		return db, cursor

	def insert(self):
		db, cursor = self.get_socket()
		query = ("INSERT INTO signals (market, currency, strategy, side, date) VALUES (%s, %s, %s, %s, %s)")
		cursor.execute(query, (self.market, self.currency, self.strategy, self.side, self.time_now()))
		db.commit()
		cursor.close()
	
	
	def new(self):
		db, cursor = self.get_socket()
		query = ("SELECT * FROM signals WHERE market=%s AND currency=%s AND strategy=%s ORDER BY id desc")
		cursor.execute(query, (self.market, self.currency, self.strategy))
		count  = cursor.rowcount
		cursor.close()
		if(count > 0):
			return False
		return True
	
	def time_now(self):
		date = datetime.utcnow().replace(minute=00, second=00)
		return date.strftime('%Y-%m-%d %H:%M:%S')
	
	def get_buy(self):
		db, cursor = self.get_socket()
		query = ("SELECT FROM signals WHERE currency=(%s) AND strategy=(%s) ORDER BY id desc")
		cursor.execute(query, (self.currency, self.strategy))
		signal = cursor.fetchone()
		count  = cursor.rowcount
		cursor.close()
		return [count, signal]

