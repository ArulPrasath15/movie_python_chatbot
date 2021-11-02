import os

import telebot

bot=telebot.TeleBot(os.getenv('API_KEY'))

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,"Welcome !")

@bot.message_handler(commands=['hello'])
def hello(message):
    bot.reply_to(message,"Hello !")

print("Bot started")
bot.polling()