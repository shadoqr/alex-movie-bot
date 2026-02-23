import telebot
import requests
from pymongo import MongoClient
import os

TOKEN = os.environ.get("7992693219:AAFyz11hi_DC8ro4vuIcgYmiDXu2gL91I6Q")
OMDB_KEY = os.environ.get("cluster0")
MONGO_URI = os.environ.get("mongodb+srv://Alexdb123:Alexdb123@cluster0.yzprwyx.mongodb.net/?appName=Cluster0")

bot = telebot.TeleBot(TOKEN)

client = MongoClient(MONGO_URI)
db = client["alex_movies"]
collection = db["movies"]

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎬 Welcome to Alex Movie Bot!\nSend movie name.")

@bot.message_handler(func=lambda message: True)
def search_movie(message):
    movie_name = message.text.lower()

    movie = collection.find_one({"name": movie_name})
    if movie:
        bot.reply_to(message, f"🎥 Watch here:\n{movie['link']}")
        return

    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDB_KEY}"
    response = requests.get(url).json()

    if response.get("Response") == "True":
        reply = f"🎬 {response['Title']}\n⭐ {response['imdbRating']}\n📅 {response['Year']}\n📝 {response['Plot']}"
    else:
        reply = "❌ Movie not found."

    bot.reply_to(message, reply)

bot.polling()
