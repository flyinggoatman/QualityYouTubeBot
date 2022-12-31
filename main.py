import asyncio
import os
import discord
from discord.ext import commands
import sys

TOKEN = "token goes here"


_intents = discord.Intents.none()
_intents.guilds = True
_intents.members = True
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=_intents)



    
@bot.event  
async def on_ready():
    await print("The bot {0.user} has started".format(bot))
    
async def main() -> None:
    """Create and run the bot"""
    await bot.start(TOKEN)
    
    
if __name__ == "__main__":
    sys.exit(asyncio.run(main()))