#--- handlers.py ---
import time
import telebot
from db import load_db, save_db, get_user
from game import start_new_game, show_game, can_play
from config import TOKEN

bot = telebot.TeleBot(TOKEN)


# --- Команда: почати гру ---
@bot.message_handler(func=lambda m: m.text.lower() == "!спіймати сніжинку")
def catch_start(message):
    db = load_db()
    user = get_user(db, message.from_user)
    save_db(db)

    if not can_play(user):
        remain = int(user["cooldown"] - time.time())
        return bot.reply_to(message, f"⏳ Грати можна через {remain // 60} хв.")

    start_new_game(user)
    save_db(db)

    bot.reply_to(message, "🎮 Починаємо грати!")
    show_game(bot, message.chat.id, user)


# --- Команда баланс ---
@bot.message_handler(func=lambda m: m.text.lower() == "!баланс")
def balance(message):
    db = load_db()
    user = get_user(db, message.from_user)
    save_db(db)  # оновлення username
    bot.reply_to(message, f"Баланс ❄️: {user['balance']}")


# --- Обробка кнопок гри ---
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    db = load_db()
    user = get_user(db, call.from_user)
    save_db(db)


    if user["game"] is None:
        return bot.answer_callback_query(call.id, "Гра не запущена!")

    data = call.data

    # --- Натискання "Забрати" ---
    if data == "take":
        reward = sum(
            1 for i in user["game"]["opened"]
            if user["game"]["field"][i] == "❄️"
        )
        user["balance"] += reward

        bot.edit_message_text(
            f"🎉 Ти забрав {reward} ❄️!\n❄️ Баланс: {user['balance']}",
            call.message.chat.id,
            call.message.message_id
        )

        user["game"] = None
        save_db(db)
        return

    # --- Відкриття клітинки ---
    if data.startswith("open_"):
        index = int(data.split("_")[1])

        if index in user["game"]["opened"]:
            return bot.answer_callback_query(call.id, "Вже відкрито!")

        user["game"]["opened"].append(index)

        # Міна → програш
        if user["game"]["field"][index] == "💣":
            bot.edit_message_text(
                "💥 Ти натрапив на міну! Гру закінчено.",
                call.message.chat.id,
                call.message.message_id
            )
            user["game"] = None
            save_db(db)
            return

        # Якщо все норм — оновлюємо ігрове поле
        save_db(db)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        show_game(bot, call.message.chat.id, user)


# --- Топ 10 ---
@bot.message_handler(func=lambda m: m.text.lower() == "!топ")
def top10(message):
    db = load_db()
    user = get_user(db, message.from_user)
    save_db(db)


    players = []
    for uid, data in db.items():
        username = data.get("username")
        balance = data.get("balance", 0)

        if username:
            name = username
        else:
            name = uid  # fallback

        players.append((name, balance))

    # сортуємо
    players = sorted(players, key=lambda x: x[1], reverse=True)[:10]

    text = "🏆 Топ 10 гравців:\n\n"

    for i, (name, bal) in enumerate(players, 1):
        text += f"{i}. {name}: {bal} ❄️\n"

    bot.reply_to(message, text)


# --- Інфо ---
@bot.message_handler(commands=["info"])
def info(message):
    bot.reply_to(
        message,
        "ℹ Інформація про бота:\n"
        "• !спіймати сніжинку — мінігра\n"
        "• !баланс — твій баланс\n"
        "• !топ — топ 10 гравців\n"
        "• Грати можна раз на 10 хв\n"
    )
