import discord
from discord import app_commands
from discord.ext import commands
import random
import json
import requests
import mysql.connector



with open("config.json") as config:
    content = json.load(config)
    TOKEN = content["DISCORD_TOKEN"]
    KEY = content["STEAM_TOKEN"]
bot = commands.Bot(command_prefix=">", intents = discord.Intents.all()) 
Database = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="teststeam"
)

Cursor = Database.cursor()




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
@app_commands.describe(range = "Input your Steam ID")
async def roll(interaction: discord.Interaction, range:int):
    await interaction.response.send_message(f"Rolled: {random.randint(1,range)}")



#Registering a user

@bot.tree.command(name="register",description="Register your steam profile")
@app_commands.describe(steam_id = "Input your Steam ID")
async def register(interaction:discord.Interaction, steam_id:str):
    sql = "INSERT INTO users (user_ID, steam_ID) VALUES (%s,%s)"
    val = (str(interaction.user.id), str(steam_id))
    Cursor.execute(sql, val)
    await interaction.response.send_message("Succesfully registered")


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
