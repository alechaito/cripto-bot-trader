#!/usr/bin/python

import os
import psutil
import MySQLdb as mysql
import shlex, subprocess
import time

def main():
	while(True):
		check_bots()
		time.sleep(20)

def check_bots():
	USERS = get_user_with_credits()
	BOT = get_bot_info(1)
	print(BOT)
	for b as BOT:
		if(bot_status(b[1]) == False):
			print("Iniciando, bot-id:%s, user_id:1"% (b[0]))
			command_line = "python /home/autobot/main.py "+str(b[0])+" 1 &>/dev/null &"
			os.system(command_line)
		else:
			print("Robo ja esta ligado pid:%s"% b[1])

def bot_status(pid):
	return psutil.pid_exists(pid)


def get_user_with_credits():
	try:
		db = mysql.connect(host="localhost", user="root", passwd="252528", db="protrader")
		cursor = db.cursor()
		query = ("SELECT id FROM users where credits > 0")
		cursor.execute(query)
		data = cursor.fetchall()
		cursor.close()
		return data
	except:
		print("erro get user with credits.")



def get_bot_info(idx):
	try:
		db = mysql.connect(host="127.0.0.1", user="root", passwd="252528", db="protrader")
		cursor = db.cursor()
		query = ("SELECT id, pid FROM bot WHERE user_id=1")
		cursor.execute(query)
		data = cursor.fetchall()
		cursor.close()
		return data
	except:
		print("erro get bot id.")


main()