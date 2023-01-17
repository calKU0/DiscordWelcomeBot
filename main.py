import discord
from discord import app_commands
from discord.ext import commands
import random
import json
import requests
from replit import Database
from datetime import datetime

def steamapigames(index):
  ID = db["Users"]["Steam_ID"][index]
  slink1 = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key="
  slink2 = "&steamid=" + str(ID) + "&include_appinfo=1&format=json"
  slink = slink1 + KEY + slink2

  #Sent API Get request and save respond to a variable
  r = requests.get(slink)

  #convert to JSON and save to another variable
  steam = r.json()
  return steam

def steamapiprofile(id):
  slink1 = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key="
  slink2 = "&steamids=" + str(id) + "&format=json"
  slink = slink1 + KEY + slink2
  r = requests.get(slink)
  steam = r.json()
  return steam

with open("config.json") as config:
    content = json.load(config)
    TOKEN = content["DISCORD_TOKEN"]
    KEY = content["STEAM_TOKEN"]
    DATABASE = content["DATABASE"]

db = Database(db_url=DATABASE)
bot = commands.Bot(command_prefix=">", intents = discord.Intents.all()) 


@bot.event
async def on_ready():
  print("We've logged in as {0.user}".format(bot))
  try:
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s)")
  except Exception as e:
    print(e)


#Roll command with not predefined range
@bot.tree.command(name="roll", description="Rolls a random number")
@app_commands.describe(range="Enter a range")
async def roll(interaction: discord.Interaction, range: int):
  await interaction.response.send_message(f"Rolled: {random.randint(1,range)}")


#Registering a user
@bot.tree.command(name="register", description="Register your steam profile")
@app_commands.describe(steam_id="Input your Steam ID")
async def register(interaction: discord.Interaction, steam_id: str):
  if str(interaction.user.id) in db["Users"]["User_ID"]:
    await interaction.response.send_message("You are already registered!")
  else:
    db["Users"]["User_ID"].append(str(interaction.user.id))
    db["Users"]["Steam_ID"].append(steam_id)
    await interaction.response.send_message("Succesfully registered!")

#Changing the user's steam ID
@bot.tree.command(name="change_steam_id", description="Change your steam ID")
@app_commands.describe(new_steam_id="Input your Steam ID",)
async def deleate(interaction: discord.Interaction, new_steam_id: str):
  if str(interaction.user.id) in db["Users"]["User_ID"]:
    index = list(db["Users"]["User_ID"]).index(str(interaction.user.id))
    del db["Users"]["User_ID"][index]
    del db["Users"]["Steam_ID"][index]
    db["Users"]["User_ID"].append(str(interaction.user.id))
    db["Users"]["Steam_ID"].append(new_steam_id)
    await interaction.response.send_message("Successfully changed!")
  else:
    await interaction.response.send_message("You are not even registered :/")


#Steam Games owned
@bot.tree.command(name="games", description="Owned games on steam")
async def games(interaction: discord.Interaction):
  try:
    if str(interaction.user.id) in str(db["Users"]["User_ID"]).split("'"):
      index = list(db["Users"]["User_ID"]).index(str(interaction.user.id))
      steam = steamapigames(index)

      #JSON output
      await interaction.response.send_message("Games owned: " + str(steam["response"]["game_count"]))
    else:
      await interaction.response.send_message("You have to register! (type /register)")
  except Exception as e:
    print(e)
    await interaction.response.send_message("Your steamID does not exists in steam. Did you registered with correct steamID?")

#Steam games playtime
@bot.tree.command(name="playtime", description="Shows your time spent in games")
@app_commands.choices(sorted = [app_commands.Choice(name="From highest",value="1"), app_commands.Choice(name="From lowest",value="0")])
async def totalplaytime(interaction: discord.Interaction,sorted: app_commands.Choice[str]):
    if str(interaction.user.id) in str(db["Users"]["User_ID"]).split("'"):
      index = list(db["Users"]["User_ID"]).index(str(interaction.user.id))
      steam = steamapigames(index)
      games = steam["response"]["games"]

      # Sort the games by playtime_forever
      if sorted.value=="1":
        games.sort(key=lambda x: x["playtime_forever"], reverse=True)
      else:
        games.sort(key=lambda x: x["playtime_forever"], reverse=False)

      x=1
      embed = discord.Embed(title="Playtime")
      for response in games:
          embed.add_field(name =f"{x}. {response['name']}",value="Hours played: " + str(round(response["playtime_forever"]/60,1)))
          x+=1
      await interaction.response.send_message(embed=embed)

    else:
        await interaction.response.send_message("You have to register! (type /register)")

#Profile information
@bot.tree.command(name="profile", description="Shows steam profile information")
@app_commands.describe(steam_id="Enter profile ID")
async def profile(interaction: discord.Interaction, steam_id: str):
  steam = steamapiprofile(steam_id)
  ts = steam['response']['players'][0]['timecreated']
  ts1 = steam['response']['players'][0]['lastlogoff']
  converted = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')
  converted1 = datetime.utcfromtimestamp(ts1).strftime('%Y-%m-%d')

  a = steam['response']['players'][0]['personastate']
  if a == 0:
    state = "Offline"
  elif a == 1:
    state = "Online"
  elif a == 2:
    state = "Busy"
  elif a == 3:
    state = "Away"
  elif a == 4:
    state = "Snooze"
  elif a == 5:
    state = "Looking to trade"
  else:
    state = "Looking to play"
    

  embed = discord.Embed(title="User Info")
  embed.set_thumbnail(url=f"{steam['response']['players'][0]['avatarmedium']}")
  embed.add_field(name ="Name",value=steam['response']['players'][0]['personaname'])
  embed.add_field(name ="State",value=state)
  if "gameid" in steam['response']['players'][0]:
    embed.add_field(name ="Currently playing",value=steam['response']['players'][0]['gameextrainfo'])
  else:
    embed.add_field(name ="Currently playing",value="Nothing")
  embed.add_field(name ="Joined at",value=converted)
  embed.add_field(name ="Last seen",value=converted1)
  await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
