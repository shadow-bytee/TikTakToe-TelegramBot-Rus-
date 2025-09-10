from settings import *
from db_utils import *
from utils import *

import telebot
from telebot import types
import sqlite3
import datetime
from colorama import Fore, Back, Style
import json
import time
import threading

initial_board_state = [" " for _ in range(9)]
# Конвертация в JSON-строку
board_state_json = json.dumps(initial_board_state)

WIN_COMBINATIONS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # строки
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # столбцы
    (0, 4, 8), (2, 4, 6)              # диагонали
]

def end_game(room_id):
	conn = sqlite3.connect("tictactoe.db")
	cursor = conn.cursor()

	# Удаляем комнату из базы данных
	cursor.execute("DELETE FROM rooms WHERE room_id = ?", (room_id,))
	conn.commit()
	conn.close()

	print(Fore.MAGENTA + f"[{str(datetime.datetime.now())}] Комната id-{room_id} удалена, игра завершена" + Style.RESET_ALL)

def check_winner(board_state):
    for x, y, z in WIN_COMBINATIONS:
        if board_state[x] == board_state[y] == board_state[z] and board_state[x] != " ":
            return board_state[x]  # Возвращает символ победителя
    return None

# # Функция, которая отсчитывает время на ход
# def time_turn(player_id):
# 	time_left = 30  # время на ход (в секундах)
	
# 	while time_left > 0:
# 		if time_left == 10:
# 			# Отправить сообщение, когда остается 10 секунд
# 			bot.send_message(player_id, "Осталось 10 секунд!")
		
# 		time.sleep(1)
# 		time_left -= 1

# 		# Когда время истекло, сообщаем о переходе хода
# 	bot.send_message(player_id, "Время вышло! Переход хода.")



#==================== Обработчик хода ====================
def move_processing(callback):
	cell_index = int(callback.data[1:]) - 1
	user_id = callback.message.chat.id
	room_id = get_room_id(user_id)
	room_info = get_room_info(room_id)

	if user_id == room_info[2]:  # Проверяем, что сейчас ход этого игрока
		# Получаем текущее состояние поля
		board_state = json.loads(room_info[3])
		
		if board_state[cell_index] == " ":  # Проверяем, свободна ли клетка
			bot.delete_message(room_info[0], get_last_bot_message_id(room_info[0]))
			bot.delete_message(room_info[1], get_last_bot_message_id(room_info[1]))
			
			# Обновляем состояние поля
			symbol = "⭕️" if user_id == room_info[0] else "❌"
			board_state[cell_index] = symbol
			board_state_json = json.dumps(board_state)
			
			# Сохраняем новое состояние в БД
			conn = sqlite3.connect("tictactoe.db")
			cursor = conn.cursor()
			cursor.execute("""
			    UPDATE rooms SET board_state = ?, current_turn = ? WHERE room_id = ?
			""", (board_state_json, room_info[0] if user_id == room_info[1] else room_info[1], room_id))
			conn.commit()
			conn.close()
			  
			# проверка нечейной позиции
			empty = 0
			for i in range(9):
				if board_state[i] == " ":
					empty += 1
				i += 1

			# Проверяем победителя
			winner = check_winner(board_state)
			if winner:
				update_user_balance(callback.message.chat.id, 195)

				for i in range(9):
					if board_state[i] == " ":
						board_state[i] = "⬜️"
					i += 1
				bot.send_message(room_info[0],
					f"🎉 Победитель: {winner} - {callback.from_user.first_name}\n"
					f"💎И он забирает 195⭐!\n\n"

					f"╔════ ▓█▓ ════╗\n\n"
					f"       {board_state[0]}     {board_state[1]}     {board_state[2]}\n\n"
					f"       {board_state[3]}     {board_state[4]}     {board_state[5]}\n\n"
					f"       {board_state[6]}     {board_state[7]}     {board_state[8]}\n\n"
					f"╚════ ▓█▓ ════╝\n\n"

					f"Ваш баланс: {get_user_balance(room_info[0])}⭐"
				)
				bot.send_message(room_info[1],
					f"🎉 Победитель: {winner} - {callback.from_user.first_name}\n"
					f"💎И он забирает 195⭐!\n\n"

					f"╔════ ▓█▓ ════╗\n\n"
					f"       {board_state[0]}     {board_state[1]}     {board_state[2]}\n\n"
					f"       {board_state[3]}     {board_state[4]}     {board_state[5]}\n\n"
					f"       {board_state[6]}     {board_state[7]}     {board_state[8]}\n\n"
					f"╚════ ▓█▓ ════╝\n\n"

					f"Ваш баланс: {get_user_balance(room_info[1])}⭐"
				)
				menu_func(room_info[0])
				menu_func(room_info[1])
				
				end_game(room_id)
			elif empty == 0:
				update_user_balance(room_info[0], 97.5)
				update_user_balance(room_info[1], 97.5)

				bot.send_message(room_info[0],
					f"Ничья, никто не выиграл!〽️\n"
					f"⚖️Деньги поделены поровну\n\n"

					f"╔════ ▓█▓ ════╗\n\n"
					f"       {board_state[0]}     {board_state[1]}     {board_state[2]}\n\n"
					f"       {board_state[3]}     {board_state[4]}     {board_state[5]}\n\n"
					f"       {board_state[6]}     {board_state[7]}     {board_state[8]}\n\n"
					f"╚════ ▓█▓ ════╝\n\n"

					f"Ваш баланс: {get_user_balance(room_info[0])}⭐"
				)
				bot.send_message(room_info[1],
					f"Ничья, никто не выиграл!〽️\n"
					f"⚖️Деньги поделены поровну\n\n"

					f"╔════ ▓█▓ ════╗\n\n"
					f"       {board_state[0]}     {board_state[1]}     {board_state[2]}\n\n"
					f"       {board_state[3]}     {board_state[4]}     {board_state[5]}\n\n"
					f"       {board_state[6]}     {board_state[7]}     {board_state[8]}\n\n"
					f"╚════ ▓█▓ ════╝\n\n"

					f"Ваш баланс: {get_user_balance(room_info[1])}⭐"
				)
				menu_func(room_info[0])
				menu_func(room_info[1])
				
				end_game(room_id)
			else:
				text = (
					f"💎Банк <b>195⭐</b>\n\n"
					f"❌ - {'👑' if check_vip_status(bot.get_chat(room_info[1]).id) == 1 else ''}{bot.get_chat(room_info[1]).first_name} {'👈' if room_info[2] == room_info[0] else ''}\n"
					f"⭕️ - {'👑' if check_vip_status(bot.get_chat(room_info[0]).id) == 1 else ''}{bot.get_chat(room_info[0]).first_name} {'👈' if room_info[2] == room_info[1] else ''}"
				)
				# Обновляем игровое поле для обоих игроков
				m1 = bot.send_message(room_info[1], text, reply_markup=create_plits(room_id), parse_mode="HTML")
				m2 = bot.send_message(room_info[0], text, reply_markup=create_plits(room_id), parse_mode="HTML")
				save_bot_message(room_info[1], m1.message_id)
				save_bot_message(room_info[0], m2.message_id)
		else:
			bot.answer_callback_query(callback.id, text="Эта клетка уже занята!")
	else:
		bot.answer_callback_query(callback.id, text="Сейчас не Ваш ход!")