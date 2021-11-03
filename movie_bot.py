import telebot
import requests
import json
from bs4 import BeautifulSoup
from dotenv import dotenv_values

config = dotenv_values(".env")
API_KEY=config['API_KEY']
bot=telebot.TeleBot(API_KEY, parse_mode='HTML')


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,"Welcome! /get to know about a Movie")


@bot.message_handler(commands=['get'])
def start(message):
    sent_msg = bot.send_message(message.chat.id, "<b>Enter the movie name you want to know 🎬🎥 ! </b>")
    bot.register_next_step_handler(sent_msg, get_movie_name)

def get_movie_name(message):
    movie_name=message.text
    if movie_name in ['/get']:
        start(message)
    else:
        bot.send_chat_action(message.chat.id, "typing")
        URL = "https://www.imdb.com/find?q="+movie_name
        r = requests.get(URL)
        soup = BeautifulSoup(r.content,'html5lib')
        table = soup.find("table", {"class": "findList"})
        movies = []
        movies_string='<b>Enter the number to know about the movie 🎬🎥</b>\n\n'
        count=1
        if table ==None:
            bot.send_message(message.chat.id, "Movie not Found!")
        else:
            for row in table.findAll("tr"):
                movies.append([row.findAll("td")[1].text ,'https://www.imdb.com' + row.findAll("td")[1].a['href']])
                movies_string = movies_string + "<b>"+str(count)+".</b>" +'\t'+ row.findAll("td")[1].text + '\n'
                count+=1
            # print(movies)
            sent_msg = bot.send_message(message.chat.id, movies_string)
            bot.register_next_step_handler(sent_msg, send_movie_detail,movies)

def send_movie_detail(message,movies):
    try:
        movie_number=int(message.text)
        if movie_number>len(movies):
            raise ValueError()
        bot.send_chat_action(message.chat.id, "typing")
        URL = movies[movie_number - 1][1]
        r = requests.get(URL)
        soup = BeautifulSoup(r.content, 'html5lib')
        movie_data = json.loads("".join(soup.find("script", {"type": "application/ld+json"}).contents))
        message_string = ''
        # print(movie_data)
        message_string += '<b><i><u>'+movies[int(movie_number) - 1][0] +'</u></i></b>'+ '\n\n'  # Movie name with year
        message_string += "⭐ " + '<b>'+str(movie_data['aggregateRating'][ 'ratingValue']) + '/' + '10' + '</b>'+ '\n' if 'aggregateRating' in movie_data.keys() else ''  # Movie rating
        message_string += '🕓 ' + '<b>'+movie_data['duration'].replace('PT', '').lower() + '</b>\n\n' if 'duration' in movie_data.keys() else ''  # duration
        message_string += '<b> 🎭 Gener : </b>' + ', '.join(movie_data['genre']) + '\n\n' if 'genre' in movie_data.keys() else ''  # Genre
        message_string += '<b> 📺 Description : </b>' + movie_data['description'] + '\n\n' if 'description' in movie_data.keys() else ''
        message_string += "<b> 🎬 Director : </b>" + ', '.join(directorname['name'] for directorname in movie_data[  "director"]) + '\n\n' if 'director' in movie_data.keys() else ''
        message_string += "<b> 📝 Writer : </b>" + ', '.join(writername['name'] for writername in movie_data["creator"] if writername['@type'] == 'Person') + '\n\n' if 'creator' in movie_data.keys() else ''
        message_string += "<b> 👥 Actors : </b>" + ', '.join(actorname['name'] for actorname in movie_data["actor"] if actorname['@type'] == 'Person') if 'actor' in movie_data.keys() else ''
        # print(message_string)
        if 'image' in movie_data.keys():
            bot.send_photo(message.chat.id, photo=movie_data['image'], caption=message_string)
        else:
            bot.send_message(message.chat.id, message_string)

    except ValueError as e:
           bot.send_message(message.chat.id, "Invalid Request, Enter /get to start over.")


print("Bot is Running")
bot.polling()