import discord
from discord import app_commands
from discord.ext import commands
import disnake
import random
import json
import requests
from replit import Database


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
@app_commands.describe(steam_id="Input your Steam ID",)
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
      ID = db["Users"]["Steam_ID"][index]
      slink1 = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key="
      slink2 = "&steamid=" + str(ID) + "&include_appinfo=1&format=json"
      slink = slink1 + KEY + slink2

      #Sent API Get request and save respond to a variable
      r = requests.get(slink)

      #convert to JSON and save to another variable
      steam = r.json()


      #JSON output
      await interaction.response.send_message("Games owned: " + str(steam["response"]["game_count"]))
    else:
      await interaction.response.send_message("You have to register! (type /register)")
  except Exception as e:
    await interaction.response.send_message("Your steamID does not exists in steam. Did you registered with correct steamID?")

#Steam games playtime
@bot.tree.command(name="playtime", description="Shows your time spent in games")
async def totalplaytime(interaction: discord.Interaction):
    if str(interaction.user.id) in str(db["Users"]["User_ID"]).split("'"):
      index = list(db["Users"]["User_ID"]).index(str(interaction.user.id))
      ID = db["Users"]["Steam_ID"][index]
      slink1 = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key="
      slink2 = "&steamid=" + str(ID) + "&include_appinfo=1&format=json"
      slink = slink1 + KEY + slink2

      #Sent API Get request and save respond to a variable
      r = requests.get(slink)

      #convert to JSON and save to another variable
      steam = r.json()

      games = steam["response"]["games"]

      # Sort the games by playtime_forever
      games.sort(key=lambda x: x["playtime_forever"], reverse=True)

      x=1
      embed = disnake.Embed(title="Playtime")
      for response in games:
          embed.add_field(name =f"{x}. {response['name']}",value=str(round(response["playtime_forever"]/60,1)) + "h")
          x+=1
      await interaction.response.send_message(embed=embed)

    else:
        await interaction.response.send_message("You have to register! (type /register)")


bot.run(TOKEN)
