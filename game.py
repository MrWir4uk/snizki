import random
import time
from db import load_db, save_db, get_user
from config import COOLDOWN
from telebot import types
import telebot

def generate_field():
    cells = ["❄️"] * 8 + ["💣"] * 2
    random.shuffle(cells)
    return cells


def can_play(user):
    return time.time() >= user["cooldown"]


def start_new_game(user):
    user["game"] = {
        "field": generate_field(),
        "opened": [],
        "alive": True
    }
    user["cooldown"] = time.time() + COOLDOWN


def show_game(bot: telebot.TeleBot, chat_id, user):
    keyboard = types.InlineKeyboardMarkup()
    buttons = []

    for i in range(10):
        if i in user["game"]["opened"]:
            val = user["game"]["field"][i]
            buttons.append(types.InlineKeyboardButton(val, callback_data="none"))
        else:
            buttons.append(types.InlineKeyboardButton(str(i + 1), callback_data=f"open_{i}"))

    keyboard.row(*buttons[:5])
    keyboard.row(*buttons[5:10])

    if user["game"]["alive"]:
        keyboard.add(types.InlineKeyboardButton("Забрати ❄️", callback_data="take"))

    bot.send_message(chat_id, "Ось твоє поле:", reply_markup=keyboard)
