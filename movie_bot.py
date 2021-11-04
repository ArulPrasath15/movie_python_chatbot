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

@bot.message_handler(commands=['know'])
def start(message):
    sent_msg = bot.send_message(message.chat.id, "<b>Enter the movie name you want to know 🎬 🎥 ! </b>")
    bot.register_next_step_handler(sent_msg, get_movie_name)

def get_movie_name(message):
    movie_name=message.text
    if movie_name in ['/get']:
        start(message)
    else:
        bot.send_chat_action(message.chat.id, "typing")
        data=scrapeIMDbData("https://www.imdb.com/find?q="+movie_name , "table", {"class": "findList"})
        if data ==None:
            bot.send_message(message.chat.id, "Movie not Found!")
        else:
            movies,movies_string = getMoviesData(data)
            sent_msg = bot.send_message(message.chat.id, movies_string)
            bot.register_next_step_handler(sent_msg, send_movie_detail,movies)

def send_movie_detail(message,movies):
    try:
        movie_number=int(message.text)
        if movie_number>len(movies):
            raise ValueError()
        bot.send_chat_action(message.chat.id, "typing")
        movie_data = json.loads("".join( scrapeIMDbData(movies[movie_number - 1][1],"script", {"type": "application/ld+json"}).contents))
        message_string=send_movie_detail_template(movie_data)
        if 'image' in movie_data.keys():
            bot.send_photo(message.chat.id, photo=movie_data['image'], caption=message_string)
        else:
            bot.send_message(message.chat.id, message_string)
    except ValueError as e:
           bot.send_message(message.chat.id, "Invalid Request, Enter /get to start over.")



def send_movie_detail_template(movie_data):
    message_string = '''<b><i><u> {name} {year} </u></i></b>\n
⭐<b>{rating}</b>
🕓 <b>{duration}  \n
<b> 🎭 Gener : </b>  {gener}\n
<b> 📺 Description : </b>  {des}\n
<b> 🎬 Director : </b>  {direction}\n
<b> 📝 Writer : </b>  {writer}\n
<b> 👥 Actors : </b> {actors}
'''
    message_string= message_string.format(
        name=movie_data['name'],
        year=movie_data['datePublished'][:4],
        rating=str(movie_data['aggregateRating']['ratingValue']) + '/10' if 'aggregateRating' in movie_data.keys() else '',
        duration=movie_data['duration'].replace('PT', '').lower() + '</b>' if 'duration' in movie_data.keys() else '',
        gener=', '.join(movie_data['genre']) if 'genre' in movie_data.keys() else '',
        des=movie_data['description'] if 'description' in movie_data.keys() else '',
        direction=', '.join(directorname['name'] for directorname in movie_data["director"]) if 'director' in movie_data.keys() else '',
        writer=', '.join(writername['name'] for writername in movie_data["creator"] if writername['@type'] == 'Person') if 'creator' in movie_data.keys() else '',
        actors=', '.join(actorname['name'] for actorname in movie_data["actor"] if actorname['@type'] == 'Person') if 'actor' in movie_data.keys() else ''
    )
    return message_string

def scrapeIMDbData(URL,name,attribute):
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'html5lib')
    data = soup.find(name,attribute )
    return data

def getMoviesData(data):
    count=1
    movies=[]
    movies_string = '<b>Enter the number to know about the movie 🎬🎥</b>\n\n'
    for row in data.findAll("tr"):
        movies.append([row.findAll("td")[1].text, 'https://www.imdb.com' + row.findAll("td")[1].a['href']])
        movies_string = movies_string + "<b>" + str(count) + ".</b>" + '\t' + row.findAll("td")[1].text + '\n'
        count += 1
    return movies,movies_string


print("Bot is Running")
bot.polling()