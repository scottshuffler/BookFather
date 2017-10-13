import os
import telebot 

bot = telebot.TeleBot(os.environ['BOT_API_TOKEN'])

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, u"Hello, welcome to this bot!")

@bot.message_handler(commands=['finished'])
def send_congrats(message):
    bot.reply_to(message, u"Nice! I'll mark you as done!")


bot.polling()


