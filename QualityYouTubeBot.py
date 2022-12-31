import re
from re import search
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import re
import json
import base64
import os
import webbrowser
import pyperclip
import win32com.client as comclt
import time
import pyautogui
from configparser import ConfigParser
import discord
from pytube import YouTube
from pytube import Channel
from discord import app_commands
import pytube
from sqlalchemy import create_engine, BigInteger, Column, Text, VARCHAR
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import asyncpg
from discord.ext import commands
from discord import interactions

intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)
tree = app_commands.CommandTree(client)



YouTubeDomain = "https://www.youtube.com/channel/"

# Adding command function


# Create the engine


## CHANGE ME##
engine = create_async_engine('postgresql+asyncpg://postgres:rootfly@localhost:5432/QualityYouTubeBot')
## CHANGE ME##


# Create a session to manage the connection to the database
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
        
Base = declarative_base()


# Creates or checks for config
if os.path.exists(os.getcwd() + "/config.json"):
    with open("./config.json") as f:
        configData = json.load(f) 
else:
    print("Please enter your token and the channel ID of the Discord channel you'd like to use.")
    print("If left blank, you'll need to go to the config.json to set them.")
    token = str(input("Bot Token: ") or "token goes here...")
    discord_channel = str(input("Channel ID:  ") or "000000000000000000")
    configTemplate = {"Token": (token), "Prefix": "/","discord_channel": (discord_channel)}
    print("The script will now crash and show an error. Run 'python QualityYouTube.py' again.")
    with open(os.getcwd() + "/config.json", "w+") as f:
        json.dump(configTemplate, f) 
    
    
    
       
            
            
    
token = configData["Token"]
prefix = configData["Prefix"]
discord_channel = configData["discord_channel"]

# Boots up the bot 
@bot.event

async def on_ready():
    bot.run
    discord_channel_int = int(discord_channel)
    discordName = bot.get_channel(discord_channel_int)
    print('We have logged in as {0.user}'.format(bot))
    print('Using Discord channel: ', discordName)
    print('The bot has now fully booted up and may be used. \nPlease be advised this bot only supports one Discord server at a time. Future updates will allow for more than one server to be active at a time.')
    print("test")
    
    
    

    

    
# Bot is checking messages
@bot.event
async def on_message(message):
    author = message.author
    timeOutMessage10 = " This message will be deleted in 10 seounds."
    timeOutMessage60 = " This message will be deleted in 60 seounds."
    noURL = " This does not contain a URL."
    invalidURL = " This URL is not supported. Please enter a valid URL."
    notChannel =  """Make sure the channel follows one of the following formats starting with http or https. 
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
                if re.search ("/channel/", channel_url) or re.search ("@", channel_url) or re.search ("/user/", channel_url) or re.search ("/c/", channel_url):
                # Defining the function for when the link is a channel.                    
                    def channel_pull(channel_url):    
                        c = Channel(channel_url)
                        channel_name = c.channel_name
                        
                        channel_id =  c.channel_id
                        channel_id_link = "https://youtube.com/channel/"+channel_id
                        if re.search ("UCMDQxm7cUx3yXkfeHa5zJIQ", channel_id_link):
                            print("######## Blocked Channel ########")
                        print("Channel Name: "+channel_name)
                        print("Channel ID: "+channel_id) 
                        print("Channel Link: "+channel_id_link)
                        if re.search ("UCMDQxm7cUx3yXkfeHa5zJIQ", channel_id_link):
                            print("#################################")
                            
                        return channel_name, channel_id_link
                    
                    channel_name, channel_id_link = channel_pull(channel_url)
                    
                    
                elif re.search ("com/watch", channel_url) or re.search ("/shorts/", channel_url) or re.search ("youtu.be", channel_url) or re.search("?list=", channel_url):
                    
                    # This code checks to see if the link is a video.
                    
                    def video_pull(channel_url):    
                        YTV = YouTube(channel_url)
                        channel_id = YTV.channel_id
                        channel_id_link = YTV.channel_url

                        c = Channel(channel_id_link)
                        channel_name =c.channel_name
                        channel_id = c.channel_id
                        
                            
                        print("Channel ID: "+channel_id)
                        print("Channel Name: "+channel_name)
                        print("channel Link: "+channel_id_link)
                        return channel_name, channel_id_link
                    channel_name, channel_id_link = video_pull(channel_url)
            
            if re.search ("UCMDQxm7cUx3yXkfeHa5zJIQ", channel_id_link):
                await message.channel.send(timeStanpIncluded+timeOutMessage10+"\n\n\n"+youTubeViwers, delete_after=num10)
                
            else:
                
                
                
                await message.channel.send(channel_name+" - "+channel_id_link)
                
                
                    
                    
        else:
    
                print("""Link not supported or wrong channel.
Link was posted insice channel """+message.channel.name)
    else:
        return        
@bot.command(
    name="my_first_command",
    description="This is the first command I made!",
    scope=938207947425710110,
)
async def my_first_command(ctx: interactions.Interaction):
    await ctx.send("Hi there!")
        
# 
bot.run(token)
