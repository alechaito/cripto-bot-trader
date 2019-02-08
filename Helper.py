from datetime import datetime as dt
import pytz
import Exchange as _EXCHANGE
import sys
import logging

'''def log():
	LOG_FORMAT = "[+] %(levelname)s %(asctime)s - %(message)s"
	logging.basicConfig(filename = '/home/autobot/logs/'+sys.argv[1],
						level = logging.DEBUG,
						format = LOG_FORMAT,
						filemode = 'w')

	logger = logging.getLogger()
	return logging.getLogger()'''

def log(msg):
	file = open('/home/autobot/logs/'+str(sys.argv[1])+'.log', 'a+')
	file.write('['+str(time_now())+'] ' + msg + "\n")



def time_now():
	brasil = pytz.timezone('America/Sao_Paulo')
	return dt.now(tz=brasil).strftime('%Y-%m-%d %H:%M:%S')

def time_replace():
	return dt.utcnow().replace(minute=00, second=00)