import discord
from discord import app_commands
from discord.ext import commands
import random

TOKENN = process.env.TOKENN
bot = commands.Bot(command_prefix=">", intents = discord.Intents.all()) 

@bot.event
async def on_ready():
    print("We've logged in as {0.user}".format(bot))
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


@bot.tree.command(name="roll", description="Rolls a random number")
@app_commands.choices(choices=[app_commands.Choice(name="100",value="100"), app_commands.Choice(name="10",value="10")])
async def roll(interaction: discord.Interaction, choices:app_commands.Choice[str]):
    if choices.value == "10":
        await interaction.response.send_message(f"Rolled: {random.randint(1,10)}")
    else:
        await interaction.response.send_message(f"Rolled: {random.randint(1,100)}")

    
bot.run(TOKENN)
