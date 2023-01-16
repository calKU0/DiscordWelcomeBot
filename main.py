import discord
from discord import app_commands
from discord.ext import commands
import random
import json
import requests
from replit import Database


db = Database(db_url="https://kv.replit.com/v0/eyJhbGciOiJIUzUxMiIsImlzcyI6ImNvbm1hbiIsImtpZCI6InByb2Q6MSIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjb25tYW4iLCJleHAiOjE2NzQwMTY2MDUsImlhdCI6MTY3MzkwNTAwNSwiZGF0YWJhc2VfaWQiOiJlNWVmODBlMS1kYzA0LTQ3OTUtYjhhNS1lMjQ4MTk2NWEzMTQiLCJ1c2VyIjoiS3J6eXN6dG9mS3Vyb3dzIiwic2x1ZyI6IldlbGNvbWVyQm90In0.oDx6MyImy01qZ3qFKS-Qoc4VLNFktdOf4Ta60ZPcVlTE03oN8cvPE2vfm65QFqsFDFKYTuCgwwAtLvnmDXKsIQ")

with open("config.json") as config:
    content = json.load(config)
    TOKEN = content["DISCORD_TOKEN"]
    KEY = content["STEAM_TOKEN"]
bot = commands.Bot(command_prefix=">", intents = discord.Intents.all()) 
db["Users"] = {
              "User_ID":[],
              "Steam_ID":[]
              }


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
    if interaction.user.id in db["Users"]["User_ID"]:
      await interaction.response.send_message("You have already registered!")
    else:
        db["Users"]["User_ID"].append(str(interaction.user.id))
        db["Users"]["Steam_ID"].append(steam_id)
        await interaction.response.send_message("Succesfully registered")
    print(db["Users"])

#Steam Games owned
@bot.tree.command(name="games", description="Owned games on steam")
async def games(interaction: discord.Integration):
  if str(interaction.user.id) in str(db["Users"]["User_ID"]).split("'"):
    index = list(db["Users"]["User_ID"]).index(str(interaction.user.id))
    ID = db["Users"]["Steam_ID"][index]
    slink1 = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key="
    slink2 = "&steamid=" + str(ID) + "&include_appinfo=1&format=json"
    slink = slink1 + KEY + slink2
    print(ID)
        
    #Sent API Get request and save respond to a variable
    r = requests.get(slink)
      
    #convert to JSON and save to another variable
    steam = r.json()
      
    #JSON output
    await interaction.response.send_message(f"Games owned: " + str(steam["response"]["game_count"]))
  else:
    await interaction.response.send_message("You have to register! (type /register)")


bot.run(TOKEN)
