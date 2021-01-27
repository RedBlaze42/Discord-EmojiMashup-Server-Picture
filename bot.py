import discord,json,emoji_mashup
from random import choice
from PIL import Image, ImageChops
import requests

bot=discord.Client()

def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    else:
         return im

def load_config():
    with open("config.json","r") as f:
        bot.config=json.load(f)

def save_config():
    with open("config.json","w") as f:
        json.dump(bot.config,f)

@bot.event
async def on_ready():
    mashup=emoji_mashup.EmojiMashupBot(bot.config["twitter"])
    if "already_used" not in bot.config.keys(): bot.config["already_used"]=list()
    tweet=choice(mashup.get_top_tweets(100,exclude_ids=bot.config["already_used"]))
    bot.config["already_used"].append(tweet["id"])

    image = Image.open(requests.get(tweet["image"], stream=True).raw)
    image=trim(image)
    image.save("image.jpg")

    with open('image.jpg', 'rb') as f:
        icon = f.read()

    guild=bot.get_guild(bot.config["guild_id"])
    await guild.edit(icon=icon)
    print("Picture changed")

    if "previous_emoji" in bot.config.keys():
        previous_emoji=await guild.fetch_emoji(bot.config["previous_emoji"])
        await previous_emoji.delete()
        del bot.config["previous_emoji"]

    if "add_emote" in bot.config.keys() and bot.config["add_emote"]:
        emoji=await guild.create_custom_emoji(name="daily_emote",image=icon)
        bot.config["previous_emoji"]=emoji.id

    save_config()
    await bot.close()

load_config()
bot.run(bot.config["token"])