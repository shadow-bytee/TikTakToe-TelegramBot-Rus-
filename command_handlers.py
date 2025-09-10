from settings import *
from callback_handlers import menu_func
from db_utils import *

import telebot
from telebot import types
import sqlite3
import datetime
from colorama import Fore, Back, Style





#===================Пользовательские комманды===========================

def start(message):
	conn = sqlite3.connect("balances.sql")
	cur = conn.cursor()
	
	# Вставка или обновление записи пользователя
	cur.execute("""
		INSERT INTO users (idchat, name, balance, vip) 
		VALUES (?, ?, ?, ?) 
		ON CONFLICT(idchat) DO NOTHING
	""", (message.chat.id, f"{str(message.from_user.first_name)} // @{str(message.from_user.username)}", 0, False))

	cur.execute("SELECT * FROM users")
	users = cur.fetchall()

	conn.commit()
	cur.close()
	conn.close()

	bot.send_message(message.chat.id, "🛑БОТ ЕЩЁ НА СТАДИИ РОЗРАБОТКИ🛑")
	bot.send_message(message.chat.id, f"📚Добро пожаловать в боте <b><a href='http://t.me/nolik_krestik_bot'>Крестики-Нолики</a></b>!!\n\n<b>📌Что может этот бот?</b>\n-Предоставить вам прекрасное времяпровождение.\n-Возможность заработать лёгкие деньги.\n-Поиграть с друзьями и другими людьми.\n-Статистика и достижения ваших игр(в разработке).\n\nКоличество игроков - {len(users)}\n\n❗️Вы соглашаетесь с <b><a href='https://drive.google.com/file/d/1P3E8tLHqEW1fqZHTdw8HFsiYVx_VvhCZ/view?usp=drivesdk'>Пользовательским соглашением</a></b>.\n\n-Версия бота v1.0.0 (Beta)", parse_mode="HTML")
	menu_func(message.chat.id)

def promo(message):
	data = str(message.text).split()[1:]
	id_promo = int(data[0])

	if id_promo > 10000:
		bot.send_message(message.from_user.id, "Максимальная сумма 10000⭐")
	else:
		update_user_balance(message.from_user.id, id_promo)

		bot.send_message(message.from_user.id, f"🔫Ваш баланс пополнен на <b>{id_promo}</b>⭐.\n Баланс: <b>{get_user_balance(message.from_user.id)}</b>⭐.", parse_mode="HTML")




#================================ADMIN==========================================

def test_command(message):                     # /test
	if message.chat.id == ADMIN_ID:
		pass


def users(message):                              # /users
	if message.chat.id == ADMIN_ID:
		conn = sqlite3.connect("balances.sql")
		cur =  conn.cursor()
	
		cur.execute("SELECT * FROM users")
		users = cur.fetchall()
	
		info = ""
		all_bal = 0
		for el in users:
			info += f"- ({'👑' if el[3] else ''}<code>{el[0]}</code>, {el[1]}, {el[2]}⭐)\n\n"
			all_bal += float(el[2])

		cur.close()
		conn.close()
	
		# users / balances
		all_bal -= get_user_balance(ADMIN_ID)
		all_bal -= get_user_balance(5915646309)
		bot.send_message(message.chat.id, info + f"\n\n<b>Общий баланс всех пользователей: {all_bal}⭐</b>", parse_mode="HTML")

def show_transactions(message):               # /trans
	if message.chat.id == ADMIN_ID:
		transactions = bot.get_star_transactions().transactions
		
		# Собираем ID всех транзакций и возвратов
		transaction_ids = set()
		refund_ids = set()
		
		for transaction in transactions:
			if transaction.source:
				transaction_ids.add(transaction.id)
			else:
				refund_ids.add(transaction.id)
		
		# Оставляем только те транзакции, у которых НЕТ возврата
		valid_transactions = [t for t in transactions if t.id not in refund_ids]
		
		for transaction in valid_transactions:
			# Пропускаем возвраты (они уже исключены)
			if not transaction.source:
				continue  
			
			# Извлекаем основные данные
			transaction_id = transaction.id
			amount = transaction.amount
			timestamp = transaction.date
			date = datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')  # Преобразуем дату
			
			# Извлекаем отправителя
			user = transaction.source.user
			user_id = user.id if user else 'Неизвестно'  # ID пользователя
			first_name = user.first_name  # Имя пользователя
			username = user.username if user and hasattr(user, 'username') else 'Неизвестно'  # Никнейм пользователя
			
			payload = transaction.source.invoice_payload
			
			# Вывод информации
			print(f"Транзакция ID: {transaction_id}")
			print(f"Количество звёзд: {amount}")
			print(f"Дата: {date}")
			print(f"Отправитель: ID={user_id}, Имя={first_name}, Никнейм={username}")
			print(f"Payload: {payload}")
			print(Back.MAGENTA + "-" * 50 + Style.RESET_ALL)
		
		bot.send_message(ADMIN_ID, "Информация выведена в консоль")


def show_transactions_all(message):              # /transall
	if message.chat.id == ADMIN_ID:
		transactions = bot.get_star_transactions()
		for transaction in transactions.transactions:
			# Извлекаем основные данные
			transaction_id = transaction.id
			amount = transaction.amount
			timestamp = transaction.date
			date = datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')  # Преобразуем дату
	
			if transaction.source:
				# Извлекаем отправителя			
				user = transaction.source.user
				user_id = user.id if user else 'Неизвестно'  # ID пользователя
				first_name = user.first_name  # Имя пользователя
				username = user.username if user and hasattr(user, 'username') else 'Неизвестно'  # Никнейм пользователя
	
				payload = transaction.source.invoice_payload
	
				# Вывод информации
				print(f"Транзакция ID: {transaction_id}")
				print(f"Количество звёзд: {amount}")
				print(f"Дата: {date}")
				print(f"Отправитель: ID={user_id}, Имя={first_name}, Никнейм={username}")
				print(f"Payload: {payload}")
				print(Back.MAGENTA + "-" * 50 + Style.RESET_ALL)
			else:
				# это возвраты
				print(Back.YELLOW + f"Транзакция ID: {transaction_id}")
				print(f"Количество звёзд: {amount}")
				print(f"Дата: {date}" + Style.RESET_ALL)
				print(Back.MAGENTA + "-" * 50 + Style.RESET_ALL)
	
		bot.send_message(ADMIN_ID, "Информация выведенена в консоль")


def deposit(message):                 # /admin (id_user) (amount)
	if message.chat.id == ADMIN_ID:
		data = str(message.text).split()[1:]
		id_user = int(data[0])
		amount = int(data[1])
		
		update_user_balance(id_user, amount)

		bot.send_message(id_user, f"🔫Ваш баланс пополнен на <b>{amount}</b>⭐.\n Баланс: <b>{get_user_balance(id_user)}</b>⭐.", parse_mode="HTML")
		bot.send_message(ADMIN_ID, "Успешно!")

def refund(message):                   # /refund (id_user) (id_transaction)
	if message.chat.id == ADMIN_ID:
		data = str(message.text).split()[1:]
		id_user = int(data[0])
		transaction_id = data[1]

		try:
			rf = bot.refund_star_payment(id_user, transaction_id)
		except Exception as e:
			print(Back.RED + "Ошибка при возврате транзакции:\n" + Style.RESET_ALL + Fore.RED + str(e) + Style.RESET_ALL)
		if rf:
			bot.send_message(ADMIN_ID, "Успешно!")

def zero(message):                 # /zero (id_user)
	if message.chat.id == ADMIN_ID:
		data = str(message.text).split()[1:]
		id_user = int(data[0])
		
		update_user_balance(id_user, -(get_user_balance(id_user)))

		#bot.send_message(id_user, f"😢Ваш баланс обнулён :(", parse_mode="HTML")
		bot.send_message(ADMIN_ID, "Успешно!")

def setvip(message):                  # /vip (id_user) (0-1)
	if message.chat.id == ADMIN_ID:
		data = str(message.text).split()[1:]
		id_user = int(data[0])
		vipactive = bool(int(data[1]))
		
		update_vip_status(id_user, vipactive)

		if vipactive:
			bot.send_message(id_user, f"<b>VIP-статус активирован!</b>", parse_mode="HTML")
		else:
			bot.send_message(id_user, f"<b>VIP-статус деактивирован :(</b>", parse_mode="HTML")

		bot.send_message(ADMIN_ID, "Успешно!")