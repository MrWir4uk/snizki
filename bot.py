from handlers import bot
from telebot.types import BotCommand

bot.set_my_commands([
    BotCommand("info", "Інформація про бота"),
])
print("Bot is running...")
bot.polling(none_stop=True)
