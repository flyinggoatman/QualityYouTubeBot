import re
from re import search
import discord
from discord import app_commands
from sqlalchemy import  BigInteger, Column, Text, VARCHAR
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine
from discord.ext import commands
import openai
from functions import channel_pull, video_pull, env_pull, about_pull, open_ai_func, Channels, insert_channel



intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='! ', intents=intents)
tree = app_commands.CommandTree(client)





        
DEBUG_MODE = True         
TOKEN, PREFIX, DISCORD_CHANNEL, SQL_HOST, SQL_USER, SQL_PORT, SQL_DATABASE, SQL_PASS, SQL_TABLE, OPEN_AI, SQL_port_String, AI_ON, DEBUG_MODE = env_pull(DEBUG_MODE)
SQL_ENABLED = True


## CHANGE ME##


if SQL_ENABLED == True:
    
    engine = create_async_engine(
        f'postgresql+asyncpg://{SQL_USER}:{SQL_PASS}@{SQL_HOST}:{SQL_port_String}/{SQL_TABLE}')
    if DEBUG_MODE == True:
        print("Debug Mode Enabled")
        print(f"Connected to {SQL_HOST}'s database called {SQL_DATABASE} inside the table {SQL_TABLE} as {SQL_USER}")
    else:
        print("Debug Mode Disabled.")

    Base = declarative_base()
else:
    print("SQL Disabled")











token = TOKEN
OPENAI_API_KEY = OPEN_AI
prefix = PREFIX
discord_channel = DISCORD_CHANNEL
  



YouTubeDomain = "https://www.youtube.com/channel/"
  

# Boots up the bot


@bot.event
async def on_ready():
    bot.run
    discord_channel_int = int(discord_channel)
    discord_channel_name = bot.get_channel(discord_channel_int)
    
    hello = f" Welcome to the QualityYouTubeBot "
    print()

    welcome = " Welcome to the QualityYouTubeBot "
    debug_message = " If you would like to turn on input DEBUG MODE then please use the .env file as a template. "
    debug_message_2 = " After you've created a .env file from the template and set up all the values inside the file. You should be good to go! "
    debug_on = " Debug mode is ENABLED "
    bot_on = ' We have logged in as {0.user} '
    print(f"{'##':#^150}") 
    print(f"{welcome:#^150}")
    if DEBUG_MODE == False:
        print(f"{debug_message:#^150}")
        print(f"{debug_message_2:#^150}")
    else:
        print(f"{debug_on:#^150}")
    print(f"{'##':#^150}")
    print(f"{bot_on:#^135}".format(bot))
    print(f"{'##':#^150}")
   

   
    if DEBUG_MODE == True:
        print(f'Using Discord channel: ', discord_channel_name)
        print(f'The bot has now fully booted up and may be used. \nPlease be advised this bot only supports one Discord server at a time. Future updates will allow for more than one server to be active at a time.')
    print()



# Bot is checking messages
@bot.event
async def on_message(message):

# Defining all the



    guild_id = message.guild.id
    channel_description = None
    author = message.author
    timeOutMessage10 = " This message will be deleted in 10 seounds."
    timeOutMessage60 = " This message will be deleted in 60 seounds."
    timeOutWhenDone = " This message will be deleted when the process is done."
    noURL = " This does not contain a URL."
    invalidURL = " This URL is not supported. Please enter a valid URL."
    notYouTube = """***Make sure the channel follows one of the following formats starting with http or https.***```
* http(s)://youtube.com/user/username
* http(s)://youtube.com/channel/username
* http(S)://youtube.com/c/username
* http(s)://youtube.com/@username
* http(s)://www.youtube.com/watch?v=VIDEO_ID
* http(s)://youtu.be/VIDEO_ID\r\r```
    """
    timeStanpIncluded = "Please remove the time stamp from the URL.\nhttps://youtu.be/VIDEO_ID?t=100 *> https://youtu.be/VIDEO_ID\n Basically remove the ***?t=100***\n"
    youTubeViwers = 'You may also find sucess in repasting the channel inside chat, sometimes the bot bugs out and posts a channel called "YouTube Viwers" without reason'
    num60 = 60
    num10 = 10
    
    if message.author == bot.user:
        return

    discord_channel_int = int(discord_channel)
    
        
        
    if discord_channel_int == message.channel.id:
        channel_url = message.content
         
            
        if re.search("http://", message.content) or re.search("https://", message.content):
            if search("youtu", channel_url):
                await message.delete()
                if re.search("/channel/", channel_url) or re.search("@", channel_url) or re.search("/user/", channel_url) or re.search("/c/", channel_url) or not re.search("youtu.", channel_url) and re.search("com/watch", channel_url):

                    channel_name, channel_id_link, channel_about, channel_id = channel_pull(channel_url, DEBUG_MODE)
                

                elif re.search("com/watch", channel_url) or re.search("/shorts/", channel_url) or re.search("youtu.be", channel_url) or re.search("?list=", channel_url):

                    channel_name, channel_id_link, channel_about, channel_id = video_pull(channel_url, DEBUG_MODE)

            if re.search("UCMDQxm7cUx3yXkfeHa5zJIQ", channel_id_link):
                await message.channel.send(f"{timeStanpIncluded}{timeOutMessage10}\n\n\n{youTubeViwers}", delete_after=num10)

            else:
                delete_me_2 = await message.channel.send(f"Please stand by {author.mention}.{timeOutWhenDone}")
                if AI_ON == True:
                    channel_description = await open_ai_func(OPENAI_API_KEY, openai, channel_about, AI_ON, channel_name, message)
                    print(f"{channel_description}")
                print(f"{channel_name}\r{channel_id_link}")
                await message.channel.send(f"{channel_name}\r{channel_id_link}")
                await delete_me_2.delete()
                await insert_channel(channel_id, channel_name, channel_id_link, channel_description)
                
                


        elif re.search("How many channels are they?", channel_url):
            await message.delete()
            
            channel = bot.get_channel(discord_channel_int)
            count = 0

            async for _ in channel.history(limit=None, oldest_first=None):  
                count += 1
            print(f"{count} messages in this channel")

            await delete_me_1.delete()
            await message.channel.send(f"{count} messages in this channel.")

        elif re.search("Delete and post all links", channel_url):


            print(f"Delete support coming soon!")
        else:

            print(f"""Link not supported or wrong channel.
Link was posted inside channel {message.channel.name}""")
            
    else:
        return

bot.run(token)