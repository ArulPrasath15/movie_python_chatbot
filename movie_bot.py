import telebot
import requests
import json
from bs4 import BeautifulSoup
from dotenv import dotenv_values
from telebot import types

config = dotenv_values(".env")
API_KEY=config['API_KEY']
bot=telebot.TeleBot(API_KEY, parse_mode='HTML')

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,"Welcome! /know to know about a Movie")

@bot.message_handler(commands=['know'])
def start(message):
    sent_msg = bot.send_message(message.chat.id, "<b>Enter the movie name you want to know 🎬 🎥 ! </b>")
    bot.register_next_step_handler(sent_msg, get_movie_name)
def get_movie_name(message):
    movie_name=message.text
    if movie_name in ['/know']:
        start(message)
    else:
        bot.send_chat_action(message.chat.id, "typing")
        data=scrapeIMDbData("https://www.imdb.com/find?q="+movie_name , "table", {"class": "findList"})
        if data ==None:
            bot.send_message(message.chat.id, "Movie not Found!")
        else:
            movies = getMoviesData(data)
            inline = types.InlineKeyboardMarkup()
            for movie in movies:
                click_button = types.InlineKeyboardButton(movie[0], callback_data=movie[1])
                inline.row(click_button)
            bot.send_message(message.chat.id, "<b>Select a Movie to know more </b>", parse_mode="HTML", reply_markup=inline, disable_web_page_preview=True)

@bot.message_handler(commands=['top10'])
def get_top10_movie(message):
    bot.send_chat_action(message.chat.id, "typing")
    data = scrapeIMDbData("https://www.imdb.com/chart/top", "tbody", {"class": "lister-list"})
    if data == None:
        bot.send_message(message.chat.id, "Movie not Found!")
    else:
        movies=getTopMoviesData(data,10)
        inline = types.InlineKeyboardMarkup()
        for movie in movies:
            click_button = types.InlineKeyboardButton(movie[0], callback_data=movie[1])
            inline.row(click_button)
        bot.send_message(message.chat.id, "<b>Top 10 Ranked Movies</b>", parse_mode="HTML", reply_markup=inline, disable_web_page_preview=True)

@bot.message_handler(commands=['top25'])
def get_top10_movie(message):
    bot.send_chat_action(message.chat.id, "typing")
    data = scrapeIMDbData("https://www.imdb.com/chart/top", "tbody", {"class": "lister-list"})
    if data == None:
        bot.send_message(message.chat.id, "Movie not Found!")
    else:
        movies=getTopMoviesData(data,25)
        inline = types.InlineKeyboardMarkup()
        for movie in movies:
            click_button = types.InlineKeyboardButton(movie[0], callback_data=movie[1])
            inline.row(click_button)
        bot.send_message(message.chat.id, "<b>Top 10 Ranked Movies</b>", parse_mode="HTML", reply_markup=inline, disable_web_page_preview=True)

# Callback
@bot.callback_query_handler(func=lambda call:call.data)
def send_movie_detail(call):
    bot.send_chat_action(call.message.chat.id, "typing")
    movie_data = json.loads(
        "".join(scrapeIMDbData(call.data, "script", {"type": "application/ld+json"}).contents))
    message_string = send_movie_detail_template(movie_data)
    if 'image' in movie_data.keys():
        bot.send_photo(call.message.chat.id, photo=movie_data['image'], caption=message_string)
    else:
        bot.send_message(call.message.chat.id, message_string)



def send_movie_detail_template(movie_data):
    message_string = '''<b><i><u> {name} {year} </u></i></b>\n
⭐<b>{rating}</b>
🕓 <b>{duration} </b>\n
<b> 🎭 Gener : </b>  {gener}\n
<b> 📺 Description : </b>  {des}\n
<b> 🎬 Director : </b>  {direction}\n
<b> 📝 Writer : </b>  {writer}\n
<b> 👥 Actors : </b> {actors}\n
<b> 🔗 IMDb : </b> {link}
'''
    message_string= message_string.format(
        name=movie_data['name'],
        year=movie_data['datePublished'][:4],
        rating=str(movie_data['aggregateRating']['ratingValue']) + '/10' if 'aggregateRating' in movie_data.keys() else '',
        duration=movie_data['duration'].replace('PT', '').lower()   if 'duration' in movie_data.keys() else '',
        gener=', '.join(movie_data['genre']) if 'genre' in movie_data.keys() else '',
        des=movie_data['description'] if 'description' in movie_data.keys() else '',
        direction=', '.join(directorname['name'] for directorname in movie_data["director"]) if 'director' in movie_data.keys() else '',
        writer=', '.join(writername['name'] for writername in movie_data["creator"] if writername['@type'] == 'Person') if 'creator' in movie_data.keys() else '',
        actors=', '.join(actorname['name'] for actorname in movie_data["actor"] if actorname['@type'] == 'Person') if 'actor' in movie_data.keys() else '',
        link= 'https://www.imdb.com'+movie_data['url']
    )
    return message_string

def scrapeIMDbData(URL,name,attribute):
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'html5lib')
    data = soup.find(name,attribute )
    return data

def getMoviesData(data):
    movies=[]
    for row in data.findAll("tr"):
        movies.append([row.findAll("td")[1].text, 'https://www.imdb.com' + row.findAll("td")[1].a['href']])
    return movies

def getTopMoviesData(data,limit):

    movies=[]
    index=1
    for row in data.findAll("tr") :
        movies.append([row.findAll('a')[1].text, 'https://www.imdb.com' + row.findAll('a')[1]['href']])
        if index == limit:
            break
    return movies

print("Bot is Running")
bot.polling()