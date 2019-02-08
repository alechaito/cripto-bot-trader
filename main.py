import sys
import Bot as _BOT
import Database as _DATABASE
import time
import Exchange as _EXCHANGE

def main():
	Database = _DATABASE.Database()
	BOT_ID = sys.argv[1]
	Bot = Database.get_bot(BOT_ID)
	Database.set_pid(BOT_ID)
	#Binance = _EXCHANGE.Exchange({'exchange':'binance'}).binance
	#Binance.load_markets()
	#data = Binance.market('ETH/BTC')['precision']['amount']
	#print(data)
	#print(Binance.fetchTradingFees(params = {}))
	while(True):
		print("Robo ativo...")
		Bot.buy_routine()
		Bot.sell_routine()
		time.sleep(30)

	

main()