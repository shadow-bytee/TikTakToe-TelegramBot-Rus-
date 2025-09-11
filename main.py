print("Импорт settings")
from settings import *
print("Импорт command_handlers")
from command_handlers import *
print("Импорт game_logiс")
from game_logic import *
print("Импорт db_utils")
from db_utils import *
print("Импорт callback_handlers")
from callback_handlers import *
print("Импорт utils")
from utils import *

import telebot
from telebot import types
from telebot.types import LabeledPrice
import sqlite3
import datetime
import random
from colorama import Fore, Back, Style
import json



@bot.message_handler(commands=["start"])
def start_handler(message):	
	start(message)	
	logs(message)

@bot.message_handler(commands=["promo"])
def promo_handler(message):	
	#promo(message)
	bot.send_message(message.from_user.id, "")	
	logs(message)





@bot.message_handler(commands=["users"])
def check_users(message):
	users(message)

@bot.message_handler(commands=["admin"])
def iddd(message):
	deposit(message)

@bot.message_handler(commands=["test"])
def test_handler(message):
	test_command(message)

@bot.message_handler(commands=["trans"])
def trans_handler(message):
	show_transactions(message)

@bot.message_handler(commands=["transall"])
def trans_handler(message):
	show_transactions_all(message)

@bot.message_handler(commands=["refund"])
def test_handler(message):
	refund(message)

@bot.message_handler(commands=["zero"])
def zero_handler(message):
	zero(message)
@bot.message_handler(commands=["vip"])
def vip_handler(message):
	setvip(message)



# Обработчик фото
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
	# Пересылка фото
	bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
	bot.send_message(ADMIN_ID, f"{message.from_user.first_name} / @{message.chat.username} (id-{message.chat.id})")

# Обработчик видео
@bot.message_handler(content_types=['video'])
def handle_video(message):
	# Пересылка видео
	bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
	bot.send_message(ADMIN_ID, f"{message.from_user.first_name} / @{message.chat.username} (id-{message.chat.id})")


@bot.message_handler()
def m(message):
	logs(message)

	user_id = message.from_user.id
	room_id = get_room_id(user_id)
	if room_id is not None:
		room_info = get_room_info(room_id)
		if user_id == room_info[0]:
			bot.send_message(room_info[1], f"{bot.get_chat(room_info[0]).first_name} 👉 {message.text}")
		else:
			bot.send_message(room_info[0], f"{bot.get_chat(room_info[1]).first_name} 👉 {message.text}")


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
	callback_processing(callback)

	if callback.data[0] == "#":
		move_processing(callback)

	elif callback.data[0] == "*":
		bot.delete_message(callback.message.chat.id, callback.message.message_id)
		send_invoice(callback.message.chat.id, int(callback.data[1:]), f"s{int(callback.data[1:])}", "Покупка звёзд")
	


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
	bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):
	bot.send_message(
		message.chat.id,
		"Спасибо за покупку! Приятной игры!",
		message_effect_id="5046509860389126442"
	)
	# Обработка оплаты
	print(Back.MAGENTA + "Принята транзакция:" + Style.RESET_ALL)
	print(Style.BRIGHT + Fore.MAGENTA + f"Пользователь: {message.from_user.first_name} // @{message.from_user.username} id:{message.chat.id}")
	print(Style.BRIGHT + Fore.MAGENTA + f"payload:{message.successful_payment.invoice_payload}")
	print(f"id:{message.successful_payment.telegram_payment_charge_id}" + Style.RESET_ALL)
 	
	if message.successful_payment.invoice_payload == "vip":
		update_vip_status(message.chat.id, True)
		bot.send_message(message.from_user.id, f"<b>VIP-статус активирован!</b>", parse_mode="HTML")
	elif message.successful_payment.invoice_payload[0] == "s":
		update_user_balance(message.from_user.id, int(message.successful_payment.invoice_payload[1:]))
		bot.send_message(message.from_user.id, f"🔫Ваш баланс пополнен на <b>{int(message.successful_payment.invoice_payload[1:])}</b>⭐.\n Баланс: <b>{get_user_balance(message.from_user.id)}</b>⭐.", parse_mode="HTML")


if __name__ == "__main__":
	# bot started
	bot.send_message(ADMIN_ID, "Бот успешно запущен! /start")
	print(Back.GREEN + f"[{str(datetime.datetime.now())}] Бот успешно запущен!" + Style.RESET_ALL)

	bot.infinity_polling()
