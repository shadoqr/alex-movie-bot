import telebot
import requests
from pymongo import MongoClient
import os

TOKEN = os.environ.get("BOT_TOKEN")
OMDB_KEY = os.environ.get("OMDB_KEY")
MONGO_URI = os.environ.get("MONGO_URI")

CHANNEL_USERNAME = "@SHADOW_movie23"
ADMIN_ID = 8458894963

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
client = MongoClient(MONGO_URI)
db = client["alex_movies"]
collection = db["movies"]

# ===== JOIN CHECK =====
def is_joined(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ===== START =====
@bot.message_handler(commands=['start'])
def start(message):
    if not is_joined(message.from_user.id):
        markup = telebot.types.InlineKeyboardMarkup()
        join_btn = telebot.types.InlineKeyboardButton(
            "📢 Join Channel",
            url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}"
        )
        markup.add(join_btn)
        bot.send_message(message.chat.id,
                         "🚫 You must join our channel first!",
                         reply_markup=markup)
        return

    welcome = f"""
🎬 <b>WELCOME TO ALEX MOVIE BOT</b> 🎬

🔥 Unlimited Movie Search  
⭐ IMDb Ratings  
🎞 Posters + Info  
📂 Channel Movies  

Type any movie name to start searching.

Commands:  
/add MovieName Link  → Add movie (Admin only)  
/delete MovieName     → Delete movie (Admin only)  
/stats               → Total movies  

Enjoy 🎬🔥
"""
    # Trending & Top 10 Buttons
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("🔥 Trending Movies", callback_data="trending"),
        telebot.types.InlineKeyboardButton("⭐ Top 10 IMDb", callback_data="top10")
    )
    bot.send_message(message.chat.id, welcome, reply_markup=markup)

# ===== CALLBACK BUTTONS =====
@bot.callback_query_handler(func=lambda call: True)
def callback_buttons(call):
    if call.data == "trending":
        trending_list = ["Avatar", "Jawan", "Fast & Furious 10", "Guardians of the Galaxy Vol.3"]
        text = "🔥 <b>Trending Movies</b> 🔥\n\n" + "\n".join(trending_list)
        bot.send_message(call.message.chat.id, text)
    elif call.data == "top10":
        top10_list = ["The Shawshank Redemption", "The Godfather", "The Dark Knight",
                      "12 Angry Men", "Schindler's List", "The Lord of the Rings: Return of the King",
                      "Pulp Fiction", "The Good, The Bad and The Ugly", "Fight Club", "Forrest Gump"]
        text = "⭐ <b>Top 10 IMDb Movies</b> ⭐\n\n" + "\n".join(top10_list)
        bot.send_message(call.message.chat.id, text)

# ===== ADMIN ADD =====
@bot.message_handler(commands=['add'])
def add_movie(message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        data = message.text.split(" ", 2)
        name = data[1].lower()
        link = data[2]

        collection.insert_one({"name": name, "link": link})
        bot.reply_to(message, "✅ Movie added successfully!")
    except:
        bot.reply_to(message, "Usage:\n/add MovieName Link")

# ===== DELETE =====
@bot.message_handler(commands=['delete'])
def delete_movie(message):
    if message.from_user.id != ADMIN_ID:
        return

    name = message.text.split(" ", 1)[1].lower()
    collection.delete_one({"name": name})
    bot.reply_to(message, "🗑 Movie deleted.")

# ===== STATS =====
@bot.message_handler(commands=['stats'])
def stats(message):
    total = collection.count_documents({})
    bot.reply_to(message, f"📊 Total Movies: {total}")

# ===== SEARCH =====
@bot.message_handler(func=lambda message: True)
def search_movie(message):
    if not is_joined(message.from_user.id):
        bot.reply_to(message, "🚫 Join channel first.")
        return

    movie_name = message.text.lower()
    movie = collection.find_one({"name": movie_name})
    if movie:
        bot.reply_to(message, f"🎥 Watch Here:\n{movie['link']}")
        return

    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={OMDB_KEY}"
    response = requests.get(url).json()

    if response.get("Response") == "True":
        text = f"""
🎬 <b>{response['Title']}</b>
📅 {response['Year']}
⭐ IMDb: {response['imdbRating']}
📝 {response['Plot']}
"""
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(
            "🎞 IMDb Page",
            url=f"https://www.imdb.com/title/{response['imdbID']}"
        )
        markup.add(btn)
        bot.send_photo(message.chat.id, response['Poster'], caption=text, reply_markup=markup)
    else:
        bot.reply_to(message, "❌ Movie not found.")

bot.polling()
