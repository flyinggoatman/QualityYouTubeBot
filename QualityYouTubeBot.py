import re
from re import search
import discord
from discord import app_commands
from sqlalchemy import BigInteger, Column, Text, VARCHAR
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine
from discord.ext import commands
from functions import channel_pull, video_pull, env_pull, Channels, insert_channel, check_channel_exists, delete_channel
import datetime
import pickle
import urllib.error
from pytube.exceptions import *
import time
import asyncio

intents = discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='! ', intents=intents)
tree = app_commands.CommandTree(client)

DEBUG_MODE = True         
TOKEN, PREFIX, DISCORD_CHANNEL, SQL_HOST, SQL_USER, SQL_PORT, SQL_DATABASE, SQL_PASS, SQL_TABLE, OPEN_AI, SQL_port_String, AI_ON, DEBUG_MODE, processing_message = env_pull(DEBUG_MODE)
SQL_ENABLED = True

if SQL_ENABLED:
    engine = create_async_engine(
        f'postgresql+asyncpg://{SQL_USER}:{SQL_PASS}@{SQL_HOST}:{SQL_port_String}/{SQL_TABLE}')
    Base = declarative_base()
    
    debug_message = (
        "Debug Mode Enabled\n"
        f"Connected to {SQL_HOST}'s database called {SQL_DATABASE} inside the table {SQL_TABLE} as {SQL_USER}"
        if DEBUG_MODE else "Debug Mode Disabled."
    )
else:
    engine = None
    Base = None
    debug_message = "SQL Disabled"

print(debug_message)

token = TOKEN
OPENAI_API_KEY = OPEN_AI
prefix = PREFIX
discord_channel = DISCORD_CHANNEL
YouTubeDomain = "https://www.youtube.com/channel/"

@bot.event
async def on_ready():
    bot.run
    discord_channel_int = int(discord_channel)
    discord_channel_name = bot.get_channel(discord_channel_int)
    global allowed_channels
    
    # Load allowed channels from file or initialize empty if not found
    try:
        with open("allowed_channels.pkl", "rb") as f:
            allowed_channels = pickle.load(f)
    except FileNotFoundError:
        allowed_channels = []

    # Styled messages with emojis
    welcome = " ★ QualityYouTubeBot ★ "
    debug_message = (
        " 🌐 DEBUG MODE OFF - Configure your .env to enable additional features 🌐 "
        if not DEBUG_MODE else " ⚙️ DEBUG MODE ACTIVATED - System diagnostics enabled ⚙️ "
    )
    bot_on = f" 🌟 Successfully Connected as {bot.user} 🌟 "
    discord_info = f"🎉 Connected to Channel: {discord_channel_name} 🎉"

    # Print styled boot-up messages
    print("=" * 80)
    print(f"{welcome:^80}")
    print("=" * 80)
    print(f"{debug_message:^80}")
    print("=" * 80)
    print(f"{bot_on:^80}")
    print("=" * 80)
    
    if DEBUG_MODE:
        print(f"{discord_info:^80}")
        print("🔒 The bot is ready for action. Currently limited to a single server.\nFuture updates may support multiple server connections.")
    print()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if int(discord_channel) != message.channel.id:
        return

    guild_id = message.guild.id
    author = message.author
    current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    channel_url = message.content.strip()

    delete_me_1 = None
    timeOutMessage10 = " This message will be deleted in 10 seconds."
    timeOutWhenDone = " This message will be deleted when the process is done."
    timeStanpIncluded = "Please remove the time stamp from the URL.\nhttps://youtu.be/VIDEO_ID?t=100 *> https://youtu.be/VIDEO_ID\n Basically remove the ***?t=100***\n"
    youTubeViwers = 'You may also find success in repasting the channel inside chat, sometimes the bot bugs out and posts a channel called "YouTube Viwers" without reason'
    something_went_wrong = f"Something went wrong. We could not add \"{channel_url}\". Please try again, or use a different link to the same channel."
    num10 = 10

    def is_youtube_link(url):
        return re.search("http://", url) or re.search("https://", url) and search("youtu", url)

    async def delete_channel_messages(channel_id):
        last_message_id = None
        while True:
            messages_to_delete = []
            async for msg in message.channel.history(limit=100, before=discord.Object(id=last_message_id) if last_message_id else None):
                
                if channel_id in msg.content or any(channel_id in embed.to_dict().get('description', '') for embed in msg.embeds):
                    messages_to_delete.append(msg)

            if not messages_to_delete:
                break

            for msg in messages_to_delete:
                try:
                    await msg.delete()
                    print(f"Deleted message with channel ID: {channel_id}")
                    await asyncio.sleep(1)  # Add a delay to avoid hitting rate limits
                except discord.errors.NotFound:
                    print(f"Message with channel ID: {channel_id} not found for deletion.")
            
            last_message_id = messages_to_delete[-1].id if messages_to_delete else None
            if last_message_id is None:
                break

    try:
        if channel_url.startswith("!delete "):
            channel_url_to_delete = channel_url.split("!delete ")[1].strip()
            channel_name, channel_id_link, channel_id = (
                channel_pull(channel_url_to_delete, DEBUG_MODE) 
                if re.search("/channel/|@|/user/|/c/|(?<!youtu.)com/watch", channel_url_to_delete) 
                else video_pull(channel_url_to_delete, DEBUG_MODE)
            )
            
            print(f"Extracted channel ID for deletion: {channel_id}")

            if await delete_channel(channel_id):
                await message.channel.send(f"Successfully deleted the channel with ID: {channel_id}", delete_after=num10)
                await delete_channel_messages(channel_id)
            else:
                await message.channel.send(f"Failed to delete the channel with ID: {channel_id}. It might not exist.", delete_after=num10)
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
        
        elif is_youtube_link(channel_url):
            if processing_message == True:
                try:
                    delete_me_1 = await message.channel.send(f"Please stand by {author.mention}.{timeOutWhenDone}", delete_after=num10)
                except discord.errors.NotFound:
                    pass
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            channel_name, channel_id_link, channel_id = (
                channel_pull(channel_url, DEBUG_MODE) 
                if re.search("/channel/|@|/user/|/c/|(?<!youtu.)com/watch", channel_url) 
                else video_pull(channel_url, DEBUG_MODE)
            )

            if re.search("UCMDQxm7cUx3yXkfeHa5zJIQ", channel_id_link):
                await message.channel.send(f"{timeStanpIncluded}{timeOutMessage10}\n\n\n{youTubeViwers}", delete_after=num10)
            else:
                if await check_channel_exists(channel_id):
                    await message.channel.send(f"The channel ***{channel_name}*** is already in the database.", delete_after=num10)
                else:
                    await insert_channel(channel_id, channel_name, channel_id_link)
                    await message.channel.send(f"{channel_name}\r{channel_id_link}\rPosted by {author.display_name}")
                    print(f"{channel_name}\r{channel_id_link}\rPosted by {author.name}\r")
                    if delete_me_1:
                        try:
                            await delete_me_1.delete()
                        except discord.errors.NotFound:
                            pass
                print(f"{channel_name}\r{channel_id_link}")

        elif re.search("!channels", channel_url):
            try:
                await message.delete()
            except discord.errors.NotFound:
                pass
            count = 0
            async for _ in message.channel.history(limit=None):
                count += 1
            print(f"{count} messages in this channel")
            if delete_me_1:
                try:
                    await delete_me_1.delete()
                except discord.errors.NotFound:
                    pass
            await message.channel.send(f"{count} messages in this channel.", delete_after=num10)
        
        elif re.search("Delete and post all links", channel_url):
            print(f"Delete support coming soon!")
        
        else:
            print(f"Link not supported or wrong channel. Link was posted inside channel {message.channel.name}")

    except urllib.error.HTTPError as e:
        print(e)
        await message.channel.send(f"The URL {channel_url} returned a 404 Not Found error.", delete_after=num10)
        await message.channel.send(f"Please note video links are currently broken. Please use a channel link instead.", delete_after=num10)
    
    except AttributeError as e:
        print(f"There has been an error at {current_time}.")
        print(f"{channel_url}")
        await message.channel.send("There has been an error. Please try the same link again.", delete_after=num10)
    
    except (RegexMatchError, VideoUnavailable, PytubeError) as e:
        print(f"Something went wrong with processing the link {channel_url} at {current_time}.")
        await message.channel.send(something_went_wrong, delete_after=num10)
    
    else:
        print("there has been an error.")

bot.run(token)
