import sqlite3
import datetime
import random
from colorama import Fore, Back, Style
import json

initial_board_state = [" " for _ in range(9)]
# Конвертация в JSON-строку
board_state_json = json.dumps(initial_board_state)

conn = sqlite3.connect("tictactoe.db")
cursor = conn.cursor()

# Создание таблицы комнат
cursor.execute("""
	CREATE TABLE IF NOT EXISTS rooms (
		room_id INTEGER PRIMARY KEY AUTOINCREMENT,
		player1_id INTEGER,
		player2_id INTEGER,
		current_turn INTEGER,
		board_state TEXT,
		winner INTEGER
	)
""")

# Создание таблицы сообщений бота
cursor.execute("""
	CREATE TABLE IF NOT EXISTS bot_messages (
		chat_id INTEGER PRIMARY KEY,
		message_id INTEGER
	)
""")

cursor.execute("DELETE FROM rooms")
conn.commit()
conn.close()

conn = sqlite3.connect("balances.sql")
cur = conn.cursor()

# Создание таблицы, если она не существует
cur.execute("""
	CREATE TABLE IF NOT EXISTS users (
		idchat INTEGER PRIMARY KEY,
		name VARCHAR(128),
		balance REAL,
		vip BOOLEAN
	)
""")

conn.commit()
conn.close()

def find_or_create_room(user_id):
	conn = sqlite3.connect("tictactoe.db")
	cursor = conn.cursor()

	# проверка находится ли игрок в игре
	cursor.execute("""
		SELECT room_id
		FROM rooms
		WHERE player1_id = ? OR player2_id = ?
	""", (user_id, user_id))
	result = cursor.fetchone()
	if result:
		return None
	else:
		# Проверяем, есть ли комната с пустым местом
		cursor.execute("""
			SELECT room_id, player1_id, player2_id FROM rooms WHERE player2_id IS NULL
		""")
		room = cursor.fetchone()

		if room:
			# Присоединяем игрока ко второй позиции
			room_id = room[0]
			# Рандомный выбор первого хода между двумя игроками
			current_turn = random.choice([room[1], user_id])

			cursor.execute("""
				UPDATE rooms
				SET player2_id = ?, current_turn = ?
				WHERE room_id = ?
			""", (user_id, current_turn, room_id))
			conn.commit()
		else:
			# Создаем новую комнату
			cursor.execute("""
				INSERT INTO rooms (player1_id, player2_id, current_turn, board_state)
				VALUES (?, NULL, ?, ?)
			""", (user_id, user_id, board_state_json))
			conn.commit()
			room_id = cursor.lastrowid

			print(Fore.MAGENTA + f"[{str(datetime.datetime.now())}] Создана комната id-{room_id}" + Style.RESET_ALL)

		conn.close()
		return room_id

def get_room_id(player_id):
	conn = sqlite3.connect("tictactoe.db")
	cursor = conn.cursor()
	cursor.execute("""
		SELECT room_id
		FROM rooms
		WHERE player1_id = ? OR player2_id = ?
	""", (player_id, player_id))
	result = cursor.fetchone()
	conn.close()
	return result[0] if result else None

def get_room_info(room_id):
	conn = sqlite3.connect("tictactoe.db")
	cursor = conn.cursor()
	cursor.execute("""
		SELECT player1_id, player2_id, current_turn, board_state FROM rooms WHERE room_id = ?
	""", (room_id,))
	room = cursor.fetchone()
	conn.close()
	return room

def get_user_balance(user_id):
	"""Получает баланс пользователя из базы данных."""
	with sqlite3.connect("balances.sql") as conn:
		cur = conn.cursor()
		cur.execute("SELECT balance FROM users WHERE idchat = ?", (user_id,))
		result = cur.fetchone()
		return result[0] if result else 0

def update_user_balance(user_id, amount):
	"""Обновляет баланс пользователя в базе данных."""
	with sqlite3.connect("balances.sql") as conn:
		cur = conn.cursor()
		cur.execute("UPDATE users SET balance = ? WHERE idchat = ?", (get_user_balance(user_id) + amount, user_id))
		conn.commit()

def update_vip_status(user_id, is_vip):
	"""Функция обновления VIP-статуса пользователя."""
	try:
		# Подключение к базе данных
		conn = sqlite3.connect("balances.sql")
		cur = conn.cursor()

		# Проверяем, есть ли пользователь в базе
		cur.execute("SELECT idchat FROM users WHERE idchat = ?", (user_id,))
		result = cur.fetchone()

		if result:
			# Обновляем статус VIP
			cur.execute("UPDATE users SET vip = ? WHERE idchat = ?", (is_vip, user_id))
			conn.commit()
		else:
			# Если пользователя нет, отправляем сообщение
			print(f"Пользователь с ID {user_id} не найден в базе.")
	except sqlite3.Error as e:
		print(f"Ошибка базы данных: {e}")
	finally:
		# Закрываем соединение
		conn.close()

def check_vip_status(user_id):
	# Подключение к базе данных
	conn = sqlite3.connect("balances.sql") 
	cur = conn.cursor()

	# Проверяем, есть ли у пользователя VIP
	cur.execute("SELECT vip FROM users WHERE idchat = ?", (user_id,))
	result = cur.fetchone()

	# Закрываем соединение
	conn.close()

	return result[0]

def save_bot_message(chat_id, message_id):
	"""Сохраняет ID последнего сообщения бота в базу данных."""
	conn = sqlite3.connect("tictactoe.db")
	cursor = conn.cursor()
	
	# Вставка или обновление последнего ID сообщения
	cursor.execute("""
		INSERT INTO bot_messages (chat_id, message_id)
		VALUES (?, ?)
		ON CONFLICT(chat_id) DO UPDATE SET message_id = excluded.message_id
	""", (chat_id, message_id))
	
	conn.commit()
	conn.close()

def get_last_bot_message_id(chat_id):
	"""Получает ID последнего сообщения бота для указанного чата."""
	conn = sqlite3.connect("tictactoe.db")
	cursor = conn.cursor()
	
	cursor.execute("SELECT message_id FROM bot_messages WHERE chat_id = ?", (chat_id,))
	result = cursor.fetchone()
	conn.close()
	
	return result[0] if result else None