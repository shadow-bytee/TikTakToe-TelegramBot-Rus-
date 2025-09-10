from settings import *

import telebot
from telebot import types
from telebot.types import LabeledPrice
import sqlite3
import datetime
import random
from colorama import Fore, Back, Style
import json

def logs(m):
	print(Fore.CYAN + f"[{str(datetime.datetime.now())}] id:" + str(m.chat.id) + " @" + str(m.from_user.username) + Fore.WHITE + " => \"" + Fore.YELLOW + str(m.text) + Style.RESET_ALL + "\"")
	#bot.send_message(996597238, ("[" + str(datetime.datetime.now()) + "] id:" + str(m.chat.id) + " @" + str(m.from_user.username) + " => \"" + str(m.text) + "\""))
	with open("logs.txt", "a+", encoding="utf-8") as logs_file:
		logs_file.write("[" + str(datetime.datetime.now()) + "] id:" + str(m.chat.id) + " @" + str(m.from_user.username) + " => \"" + str(m.text) + "\"\n")

def send_invoice(chat_id, count, payload, title):
	prices = [LabeledPrice(label="XTR", amount=count)]  
	bot.send_invoice(
		chat_id,
		title=f"{title}",
		description=f"Вы заплатите {count}⭐",
		provider_token="",
		currency="XTR",
		prices=prices,
		start_parameter="buy-stars",
		invoice_payload=f"{payload}"
	)

def menu_func(chatid):
	markup = create_markup([
		[("Играть 100⭐", "game"), ("Баланс", "balance")],
		[("👑VIP", "vip")]
	])
	bot.send_message(chatid, "🧩С чего бы ты хотел(а) начать?", reply_markup=markup)

def create_markup(rows):
	markup = types.InlineKeyboardMarkup()
	for row in rows:
		# Если row является кортежем с двумя элементами, превращаем его в список
		if isinstance(row, tuple) and len(row) == 2:
			markup.row(types.InlineKeyboardButton(row[0], callback_data=row[1]))
		elif isinstance(row, list):  # Если передан список кортежей
			markup.row(*[types.InlineKeyboardButton(text, callback_data=data) for text, data in row])
		else:
			print(Back.RED + f"[{str(datetime.datetime.now())}] Invalid row format: {row}" + Style.RESET_ALL)  # Логируем некорректные строки
	return markup

def create_plits(rm):
	# Подключение к базе данных
	conn = sqlite3.connect("tictactoe.db")
	cursor = conn.cursor()

	# Извлечение состояния игрового поля для указанной комнаты
	cursor.execute("""
		SELECT board_state FROM rooms WHERE room_id = ?
	""", (rm,))
	result = cursor.fetchone()
	
	if not result:
		conn.close()
		raise ValueError(f"Комната с id {rm} не найдена")
	
	# Преобразуем JSON-строку в список
	board_state = json.loads(result[0])
	conn.close()

	markup = types.InlineKeyboardMarkup()
	for row in range(3):
		buttons = [
			types.InlineKeyboardButton(
				board_state[i], callback_data=f"#{i+1}"
			) for i in range(row * 3, (row + 1) * 3)
		]
		markup.row(*buttons)
	return(markup)