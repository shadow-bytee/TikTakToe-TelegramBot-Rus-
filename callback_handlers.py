from settings import *
from db_utils import *
from utils import *

import telebot
from telebot import types
from telebot.types import LabeledPrice
import sqlite3
import datetime
import random
from colorama import Fore, Back, Style
import json
 
not_id = None

def callback_processing(callback):
	global not_id

	print(f"[{str(datetime.datetime.now())}] Игрок @{callback.from_user.username} (id-{callback.from_user.id}) нажал на кнопку " + Fore.YELLOW + callback.data + Style.RESET_ALL)

	if callback.data == "balance":
		bot.delete_message(callback.from_user.id, callback.message.message_id)
		
		balance = get_user_balance(callback.from_user.id)

		markup = create_markup([
			[("Пополнить", "deposit"), ("Вывести", "withdrawal")],
			[("🔙Назад в меню", "menu")]
		])

		bot.send_message(
			callback.from_user.id,
			f"🖍id: <code>{callback.from_user.id}</code>\n\n"
			f"💳Ваш текущий баланс: <b>{balance}</b>⭐",
			reply_markup=markup,
			parse_mode="HTML"
		)

	elif callback.data == "game":
		bot.delete_message(callback.from_user.id, callback.message.message_id)
		balance = get_user_balance(callback.from_user.id)
		if balance >= 100:
			user_id = callback.from_user.id
			room_id = find_or_create_room(user_id)
			if room_id != None:
				room_info = get_room_info(room_id)
	
				print(Fore.BLUE + f"[{str(datetime.datetime.now())}] Игрок @{callback.from_user.username} (id-{user_id}) присоеденился к комнате id-{room_id}" + Style.RESET_ALL)
		
				if room_info[1] is None:
					markup = types.InlineKeyboardMarkup()
					btn1 = types.InlineKeyboardButton("🔙Назад", callback_data="leave_wait")
					markup.row(btn1)
					m = bot.send_message(callback.from_user.id, f"Ожидаем соперника...", reply_markup=markup)
					save_bot_message(callback.from_user.id, m.message_id)

					n = bot.send_message(ADMIN_GROUP, f"Игрок @{callback.from_user.username} (id-{user_id}) ищет соперника", reply_markup=create_markup([("Начать игру", "game")]))
					not_id = n.message_id
				else:
					print(room_info)
					bot.delete_message(room_info[0], get_last_bot_message_id(room_info[0]))

					update_user_balance(room_info[0], -100)
					update_user_balance(room_info[1], -100)

					bot.send_message(callback.from_user.id, f"Игра начинается! Соперник - {bot.get_chat(room_info[0]).first_name}")
					bot.send_message(room_info[0], f"Игра начинается! Соперник - {callback.from_user.first_name}")

					text = (
						f"💎Банк <b>195⭐</b>\n\n"
						f"❌ - {'👑' if check_vip_status(callback.from_user.id) else ''}{callback.from_user.first_name} {'👈' if room_info[2] == callback.from_user.id else ''}\n"
						f"⭕️ - {'👑' if check_vip_status(room_info[0]) else ''}{bot.get_chat(room_info[0]).first_name} {'👈' if room_info[2] == room_info[0] else ''}"
					)
					m1 = bot.send_message(callback.from_user.id, text, reply_markup=create_plits(room_id), parse_mode="HTML")
					m2 = bot.send_message(room_info[0], text, reply_markup=create_plits(room_id), parse_mode="HTML")
					save_bot_message(callback.from_user.id, m1.message_id)
					save_bot_message(room_info[0], m2.message_id)
					print(Fore.MAGENTA + f"[{str(datetime.datetime.now())}] Игра в комнате id-{room_id} начинается" + Style.RESET_ALL)

					if not_id is not None:
						bot.delete_message(ADMIN_GROUP, not_id)
						not_id = None
			else:
				bot.answer_callback_query(callback.id, text="Вы находитесь уже в игре!")
		else:
			markup = create_markup([("Пополнить счёт", "deposit")])
			bot.send_message(callback.from_user.id, f"На вашем счету недостаточно средств!\nБаланс: {balance}⭐", reply_markup=markup)

	elif callback.data == "leave_wait":
		bot.delete_message(callback.from_user.id, callback.message.message_id)

		room_id = get_room_id(callback.from_user.id)

		conn = sqlite3.connect("tictactoe.db")
		cursor = conn.cursor()
		cursor.execute("DELETE FROM rooms WHERE player1_id = ?", (callback.from_user.id,))
		conn.commit()
		conn.close()

		print(Fore.BLUE + f"[{str(datetime.datetime.now())}] Игрок @{callback.message.chat.username} (id-{callback.from_user.id}) покинул комнату id-{room_id}" + Style.RESET_ALL)
		print(Fore.MAGENTA + f"[{str(datetime.datetime.now())}] Комната id-{room_id} удалена" + Style.RESET_ALL)
		# bot.send_message(ADMIN_GROUP, f"Игрок @{callback.message.chat.username} (id-{callback.from_user.id}) покинул поиск")
		if not_id is not None:
			bot.delete_message(ADMIN_GROUP, not_id)
			not_id = None

		menu_func(callback.from_user.id)
 
	elif callback.data == "menu":
		bot.delete_message(callback.from_user.id, callback.message.message_id)
		menu_func(callback.from_user.id)

	elif callback.data == "deposit":
		bot.delete_message(callback.from_user.id, callback.message.message_id)
		markup = create_markup([
			[("10⭐", "*10"), ("50⭐", "*50")],
			[("100⭐", "*100"), ("200⭐", "*200")],
			[("500⭐", "*500"), ("🔙Назад", "balance")]
		])
		bot.send_message(
			callback.from_user.id,
			f"❗️Выберите сумму пополнения:\n",
			reply_markup=markup,
			parse_mode="HTML"
		)

	elif callback.data == "withdrawal":
		bot.delete_message(callback.from_user.id, callback.message.message_id)
		balance = get_user_balance(callback.from_user.id)
		markup = create_markup([("🔙Назад в меню", "menu")])
		bot.send_message(
			callback.from_user.id,
			f"💳Ваш текущий баланс: <b>{balance}</b>$.\n\n"
			f"<b>Напишите Администратору для вывода:</b> @KrestikiNolikiAdmin\n"
			f"(Учитывайте возможную комиссию)",
			reply_markup=markup,
			parse_mode="HTML"
		)

	elif callback.data == "vip":
		bot.delete_message(callback.from_user.id, callback.message.message_id)
		user_id = callback.from_user.id

		is_vip = check_vip_status(user_id)  # Получаем значение столбца vip (True или False)
		if is_vip:
			markup = create_markup([("🔙Назад в меню", "menu")])
			bot.send_message(user_id, "Вы уже являетесь <b>VIP-пользователем</b>! 🎉", reply_markup=markup, parse_mode="HTML")
		else:
			markup = create_markup([[("Купить VIP👑", "buy_vip"), ("🔙Назад в меню", "menu")]])
			bot.send_message(user_id,
				"У вас пока нет <b>VIP-статуса</b>. Вы можете его приобрести за 1000⭐!\n\n"
				"<b>Преимущества:</b>\n"
				"-Значок VIP-пользователя 👑\n"
				"-Статистика пользователя (в разработке)\n",
				reply_markup=markup,
				parse_mode="HTML"
			)
	elif callback.data == "buy_vip":
		bot.delete_message(callback.from_user.id, callback.message.message_id)
		send_invoice(callback.from_user.id, 1000, "vip", "Покупка VIP-статуса")