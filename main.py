import discord
from discord import app_commands
from discord.ext import commands
import random
import requests


TOKEN = ""
KEY = ""
bot = commands.Bot(command_prefix=">", intents = discord.Intents.all()) 

@bot.event
async def on_ready():
    print("We've logged in as {0.user}".format(bot))
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

#Roll command with choice of 10 and 100
@bot.tree.command(name="roll", description="Rolls a random number")
@app_commands.choices(choices=[app_commands.Choice(name="100",value="100"), app_commands.Choice(name="10",value="10")])
async def roll(interaction: discord.Interaction, choices:app_commands.Choice[str]):
    if choices.value == "10":
        await interaction.response.send_message(f"Rolled: {random.randint(1,10)}")
    else:
        await interaction.response.send_message(f"Rolled: {random.randint(1,100)}")

#Steam Games owned
@bot.tree.command(name="games", description="Owned games on steam")
async def games(interaction: discord.Integration):
    ID = "76561198074294120"
    slink1 = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key="
    slink2 = "&steamid=" + ID + "&include_appinfo=1&format=json"
    slink = slink1 + KEY + slink2
    
    #Sent API Get request and save respond to a variable
    r = requests.get(slink)
    
    #convert to JSON and save to another variable
    steam = r.json()
    
    #JSON output with information about each game owned
    await interaction.response.send_message(f"Games owned:" + str(steam["response"]["game_count"]))


    
bot.run(TOKEN)
