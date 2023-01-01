import re
from re import search
import json
import os
import discord
from pytube import YouTube
from pytube import Channel
from discord import app_commands
from sqlalchemy import create_engine, BigInteger, Column, Text, VARCHAR
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from discord.ext import commands
from discord import interactions
import requests
import html
from decouple import config
from os import environ
import openai
from time import sleep
import functions



intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='! ', intents=intents)
tree = app_commands.CommandTree(client)





        
              
TOKEN = config('TOKEN') 
PREFIX = config('PREFIX') 
DISCORD_CHANNEL = config('DISCORD_CHANEL ', default='938207947878703187') 
SQL_HOST = config('SQL_HOST', default='localhost')
SQL_USER = config('SQL_USER') 
SQL_PASS = config('SQL_PASS') 
SQL_PORT = config('SQL_PORT', cast=int)
SQL_DATABASE = config('SQL_DATABASE')
SQL_TABLE = config('SQL_TABLE')
OPEN_AI = config('OPEN_AI')

print()  
print(f'discord_token: {TOKEN}')
print(f'open_ai_token: {OPEN_AI}')
print(f'prefix:  {PREFIX}')
print(f'sql_host: {SQL_HOST}')
print(f'sql_user: {SQL_USER}')
print(f'sq_pass:  {SQL_PASS}')
print(f'sql_port: {SQL_PORT}')
print(f'sql_database: {SQL_DATABASE}')
print(f'sql_table: {SQL_TABLE}')
print()
SQL_port_String = str(SQL_PORT)
## CHANGE ME##
engine = create_async_engine(
    f'postgresql+asyncpg://{SQL_USER}:{SQL_PASS}@{SQL_HOST}:{SQL_port_String}/{SQL_TABLE}')

Base = declarative_base()










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
    discordName = bot.get_channel(discord_channel_int)
    print()
    print('We have logged in as {0.user}'.format(bot))
    print(f'Using Discord channel: ', discordName)
    print(f'The bot has now fully booted up and may be used. \nPlease be advised this bot only supports one Discord server at a time. Future updates will allow for more than one server to be active at a time.')
    print()



# Bot is checking messages
@bot.event
async def on_message(message):

    # Variables Section


    guild_id = message.guild.id
    author = message.author
    timeOutMessage10 = " This message will be deleted in 10 seounds."
    timeOutMessage60 = " This message will be deleted in 60 seounds."
    noURL = " This does not contain a URL."
    invalidURL = " This URL is not supported. Please enter a valid URL."
    notChannel = """Make sure the channel follows one of the following formats starting with http or https. 
    \r - http:://youtube.com/user/username
    \r - http://youtube.com/channel/username
    \r - http://youtube.com/@username\r\r
    ***We hope to add video support soon***"""
    timeStanpIncluded = "Please remove the time stamp from the URL.\nhttps://youtu.be/agEapr94odU?t=100 -> https://youtu.be/agEapr94odU\n Basically remove the ***?t=100***\n"
    youTubeViwers = 'You may also find sucess in repasting the channel inside chat, sometimes the bot bugs out and posts a channel called "YouTube Viwers" without reason'
    num60 = 60
    num10 = 10
    if message.author == bot.user:
        return

    # Checking if the discord channel matches the one set in the config
    discord_channel_int = int(discord_channel)
    if discord_channel_int == message.channel.id:
        channel_url = message.content

        # Checking to see if the link is actally a URL
        if re.search("http", message.content):
            

            # Checking to see if the link is a youtube link
            if re.search("http", channel_url) and search("://", channel_url) and search("youtu", channel_url):
                await message.delete()
                # Checking to see if the link is a channel link
                if re.search("/channel/", channel_url) or re.search("@", channel_url) or re.search("/user/", channel_url) or re.search("/c/", channel_url) or not re.search("youtu.", channel_url) and re.search("com/watch", channel_url):
                    # Defining the function for when the link is a channel.
                    def channel_pull(channel_url):
                        c = Channel(channel_url)
                        channel_name = c.channel_name
                        channel_id = c.channel_id
                        channel_id_link = f"https://youtube.com/channel/{channel_id}"
                        url = c.about_url

                        # Send an HTTP GET request to the URL
                        response = requests.get(
                            url, cookies={'CONSENT':'YES+42'})

                        # Get the content of the response
                        text = response.text

                        # Use the regular expression to match the content for the meta tag with the itemprop="description" attribute
                        pattern = r'itemprop="description"\s+content="([^"]+)"'

                        match = re.search(pattern, text)
                        print()
                        if match:
                            content = match.group(1)
                            channel_about = html.unescape(content)
                        else:
                            print(f"No match found.")
                        print()
                        
                        
                        
                        
                        
                        if re.search("UCMDQxm7cUx3yXkfeHa5zJIQ", channel_id_link):
                            print(f"######## Blocked Channel ########")
                        print(f"Channel Name: {channel_name}")
                        print(f"Channel ID: {channel_id}")
                        print(f"Channel Link: {channel_id_link}")
                        if re.search("UCMDQxm7cUx3yXkfeHa5zJIQ", channel_id_link):
                            print(f"#################################")

                        return channel_name, channel_id_link

                    channel_name, channel_id_link, = channel_pull(channel_url)

                elif re.search("com/watch", channel_url) or re.search("/shorts/", channel_url) or re.search("youtu.be", channel_url) or re.search("?list=", channel_url):

                    # This code checks to see if the link is a video.

                    def video_pull(channel_url):
                        YTV = YouTube(channel_url)
                        channel_id = YTV.channel_id
                        channel_id_link = YTV.channel_url

                        c = Channel(channel_id_link)
                        channel_name = c.channel_name
                        channel_id = c.channel_id
                        channel_html = c._about_html
                        
                        
                        
                        
                        url = c.about_url

                        # Send an HTTP GET request to the URL and passes the cookie check.
                        response = requests.get(
                            url, cookies={'CONSENT':'YES+42'})

                        # Get the content of the response
                        text = response.text

                        # Use the regular expression to match the content for the meta tag with the itemprop="description" attribute
                        pattern = r'itemprop="description"\s+content="([^"]+)"'

                        match = re.search(pattern, text)
                        print()
                        if match:
                            content = match.group(1)
                            channel_about = html.unescape(content)
                        else:
                            print(f"No match found.")
                        print()  
                        # This prints out the channel information to the Console.
                        print(f"Channel ID: {channel_id}")
                        print(f"Channel Name: {channel_name}")
                        print(f"channel Link: {channel_id_link}")
                        return channel_name, channel_id_link
                    channel_name, channel_id_link = video_pull(channel_url)

            if re.search("UCMDQxm7cUx3yXkfeHa5zJIQ", channel_id_link):
                await message.channel.send(f"{timeStanpIncluded}{timeOutMessage10}\n\n\n{youTubeViwers}", delete_after=num10)

            else:    
                
                await message.channel.send(f"{channel_name}\r{channel_id_link}")
                    
            
            # Open AI code, will be added back in future.
            
            
            #     openai.api_key = OPENAI_API_KEY
            #     text_input = str(input(channel_about))
            #     text_input = text_input.strip()
            
            #     response = openai.Completion.create(
            #             engine="text-davinci-002",
            #             prompt="\nDescription\n\ndescribe the following in 20 words that MUST start with\n \n\n\""+channel_name+" - A channel that...'\"\n\n\n"+channel_about+"\n\n\n\n",
            #             temperature=0.9,
            #             max_tokens=256,
            #             top_p=1,
            #             frequency_penalty=0,
            #             presence_penalty=0
            #             )


            # print(response["choices"][0]["text"])
            
                









        elif re.search("How many channels are they?", channel_url):
            await message.delete()
            delete_me_1 = await message.channel.send(f"Give me a moment {author.mention}, I need to think really hard!")

            channel = bot.get_channel(discord_channel_int)
            count = 0
            async for _ in channel.history(limit=None, oldest_first=None):  
                count += 1
            print(f"{count} messages in this channel")
            
            await delete_me_1.delete()
            await message.channel.send(f"{count} messages in this channel.")

        elif re.search("Delete and post all links", channel_url):
            

            print(f"placeholder")

        else:

            print(f"""Link not supported or wrong channel.
Link was posted insice channel {message.channel.name}""")
    else:
        return
# @bot.command(
#     name="my_first_command",
#     description="This is the first command I made!",
#     scope=938207947425710110,
# )
# async def my_first_command(ctx: interactions.Interaction):
#     await ctx.send("Hi there!")

#
bot.run(token)


