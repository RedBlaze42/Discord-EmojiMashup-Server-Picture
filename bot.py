import discord,json,emoji_mashup
from random import choice
from PIL import Image, ImageChops, ImageDraw
import requests

bot=discord.Client(max_messages=None)

def load_config():
    with open("config.json","r") as f:
        bot.config=json.load(f)

def save_config():
    with open("config.json","w") as f:
        json.dump(bot.config,f)

@bot.event
async def on_ready():
    print("Starting")
    mashup=emoji_mashup.EmojiMashupBot(bot.config["twitter"])
    if "already_used" not in bot.config.keys(): bot.config["already_used"]=list()
    tweet=choice(mashup.get_top_tweets(40,exclude_ids=bot.config["already_used"]))
    bot.config["already_used"].append(tweet["id"])

    image = Image.open(requests.get(tweet["image"], stream=True).raw)
    image=emoji_mashup.transparency(image)
    image=emoji_mashup.trim(image)
    image.save("image.png")

    with open('image.png', 'rb') as f:
        icon = f.read()

    guild=bot.get_guild(bot.config["guild_id"])
    await guild.edit(icon=icon)
    print("Picture changed")

    if "previous_emoji" in bot.config.keys():
        try:
            previous_emoji=await guild.fetch_emoji(bot.config["previous_emoji"])
            await previous_emoji.delete()
        except discord.errors.NotFound:
            print("previous_emoji not found")
        del bot.config["previous_emoji"] 

    if "add_emote" in bot.config.keys() and bot.config["add_emote"]:
        emoji=await guild.create_custom_emoji(name="daily_emote",image=icon)
        bot.config["previous_emoji"]=emoji.id

    if "channel" in bot.config.keys():
        channel = await bot.fetch_channel(bot.config["channel"])
        if channel is not None:
            await channel.send("Nouvel photo de serveur:\nhttps://twitter.com/EmojiMashupBot/status/{}".format(tweet["id"]))

    save_config()
    await bot.close()

load_config()
bot.run(bot.config["token"])
