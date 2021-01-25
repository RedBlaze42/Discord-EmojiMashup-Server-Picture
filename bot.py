import discord,json,emoji_mashup
from random import choice
from PIL import Image
import requests

bot=discord.Client()

def load_config():
    with open("config.json","r") as f:
        bot.config=json.load(f)

def save_config():
    with open("config.json","w") as f:
        json.dump(bot.config,f)

@bot.event
async def on_ready():
    mashup=emoji_mashup.EmojiMashupBot(bot.config["twitter"])

    tweet=choice(mashup.get_top_tweets(50,exclude_ids=bot.config["already_used"]))
    bot.config["already_used"].append(tweet["id"])
    save_config()

    image = Image.open(requests.get(tweet["image"], stream=True).raw)
    image=image.crop(image.getbbox())
    image.save("image.jpg")

    with open('image.jpg', 'rb') as f:
        icon = f.read()

    await bot.get_guild(bot.config["guild_id"]).edit(icon=icon)
    print("Picture changed")
    await bot.close()

load_config()
bot.run(bot.config["token"])