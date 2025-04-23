import re
from pytube import YouTube
from pytube import Channel
import requests
import html
from decouple import config
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import Column, Text, VARCHAR, DateTime, select, delete
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import datetime
import asyncio
import colorama
from colorama import Fore

Base = declarative_base()

class Channels(Base):
    __tablename__ = "ChannelList"

    channel_id = Column("Channel ID", VARCHAR, primary_key=True)
    channel_name = Column("Channel Name", Text)
    channel_id_link = Column("Channel URL", Text)
    channel_description = Column("Channel Description", Text)
    channel_logo = Column("Channel Logo", Text, nullable=True, default=None)
    created_at = Column(DateTime, nullable=False)

engine = create_async_engine('postgresql+asyncpg://postgres:rootfly@localhost:5432/QualityYouTubeBot')

async_session = AsyncSession(bind=engine)

async def insert_channel(channel_id, channel_name, channel_id_link, channel_description=None, channel_logo=None):
    async with async_session as session:
        created_at = datetime.datetime.now()  # get current date and time
        new_channel = Channels(channel_id=channel_id, channel_name=channel_name, channel_id_link=channel_id_link, channel_description=channel_description, channel_logo=channel_logo, created_at=created_at)
        try:
            session.add(new_channel)
            await session.commit()
        except IntegrityError:
            print(f"channel {channel_name} is already in the database.")
            await session.rollback()
        else:
            print(f"Successfully added {channel_name} to the database.")

async def check_channel_exists(channel_id):
    async with async_session as session:
        exists = await session.execute(select(Channels).where(Channels.channel_id == channel_id))
        return exists.scalars().first() is not None

async def delete_channel(channel_id):
    async with async_session as session:
        try:
            print(f"Attempting to delete channel with ID: {channel_id}")
            result = await session.execute(delete(Channels).where(Channels.channel_id == channel_id))
            if result.rowcount > 0:
                await session.commit()
                print(f"Successfully deleted channel with ID: {channel_id}")
                return True
            else:
                print(f"No channel found with ID: {channel_id}")
                return False
        except Exception as e:
            print(f"Failed to delete channel with ID: {channel_id}. Error: {e}")
            await session.rollback()
            return False

def channel_pull(channel_url, DEBUG_MODE):
    try:
        c = Channel(channel_url)
        channel_name = c.channel_name
        channel_id = c.channel_id
        channel_id_link = f"https://youtube.com/channel/{channel_id}"
    except Exception as e:
        if DEBUG_MODE:
            print(f"{Fore.RED}Error in channel_pull: {e}")
        # Try an alternative extraction method
        if '@' in channel_url:
            # Handle @username type URLs
            username = channel_url.split('@')[-1].split('/')[0].split('?')[0]
            channel_id = f"@{username}"
            channel_id_link = f"https://youtube.com/{channel_id}"
            channel_name = username  # Use username as fallback name
        else:
            # Extract channel ID using regex if possible
            channel_match = re.search(r"(?:\/channel\/|\/c\/|\/user\/)([^\/\?]+)", channel_url)
            if channel_match:
                channel_id = channel_match.group(1)
                channel_id_link = f"https://youtube.com/channel/{channel_id}"
                channel_name = channel_id  # Use ID as fallback name
            else:
                raise ValueError(f"Could not parse channel information from URL: {channel_url}")

    if DEBUG_MODE:
        if re.search("UCMDQxm7cUx3yXkfeHa5zJIQ", channel_id_link):
            print(f"{Fore.RED}######## Blocked Channel ########")
        print(f"{Fore.YELLOW}Channel Name: {channel_name}")
        print(f"{Fore.WHITE}Channel ID: {channel_id}")
        print(f"{Fore.WHITE}Channel Link: {channel_id_link}")
        if re.search("UCMDQxm7cUx3yXkfeHa5zJIQ", channel_id_link):
            print(f"{Fore.RED}#################################")
            
    return channel_name, channel_id_link, channel_id

def video_pull(channel_url, DEBUG_MODE):
    try:
        # First attempt: Use pytube
        YTV = YouTube(channel_url)
        channel_id = YTV.channel_id
        channel_id_link = YTV.channel_url
        
        c = Channel(channel_id_link)
        channel_name = c.channel_name
        channel_id = c.channel_id
    except Exception as e:
        if DEBUG_MODE:
            print(f"{Fore.RED}Error in video_pull using pytube: {e}")
            
        # Second attempt: Extract video ID and fetch channel info via direct HTML scraping
        try:
            video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", channel_url)
            if not video_id_match:
                raise ValueError(f"Could not extract video ID from URL: {channel_url}")
            
            video_id = video_id_match.group(1)
            watch_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Get the HTML of the watch page
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(watch_url, headers=headers)
            html_content = response.text
            
            # Try to extract channel ID from HTML
            channel_id_match = re.search(r'"channelId":"([^"]+)"', html_content)
            if not channel_id_match:
                raise ValueError(f"Could not extract channel ID from video page: {watch_url}")
                
            channel_id = channel_id_match.group(1)
            channel_id_link = f"https://youtube.com/channel/{channel_id}"
            
            # Try to extract channel name from HTML
            channel_name_match = re.search(r'"ownerChannelName":"([^"]+)"', html_content) or re.search(r'"author":"([^"]+)"', html_content)
            if channel_name_match:
                channel_name = html.unescape(channel_name_match.group(1))
            else:
                channel_name = f"Channel {channel_id}"  # Fallback name
                
        except Exception as nested_e:
            if DEBUG_MODE:
                print(f"{Fore.RED}Error in video_pull fallback method: {nested_e}")
            raise ValueError(f"Could not extract channel information from video URL: {channel_url}")

    if DEBUG_MODE:
        print(f"{Fore.YELLOW}Channel ID: {channel_id}")
        print(f"{Fore.WHITE}Channel Name: {channel_name}")
        print(f"{Fore.WHITE}Channel Link: {channel_id_link}")
        
    return channel_name, channel_id_link, channel_id

def env_pull(DEBUG_MODE):
    TOKEN = config('TOKEN') or ''
    PREFIX = config('PREFIX') or ''
    DISCORD_CHANNEL = config('DISCORD_CHANNEL', default='938207947878703187') or ''
    SQL_HOST = config('SQL_HOST', default='localhost')
    SQL_USER = config('SQL_USER') or ''
    SQL_PASS = config('SQL_PASS') or ''
    SQL_PORT = config('SQL_PORT', cast=int) or 5432
    SQL_DATABASE = config('SQL_DATABASE') or ''
    SQL_TABLE = config('SQL_TABLE') or ''
    OPEN_AI = config('OPEN_AI') or ''
    AI_ON = config('AI_ON', cast=bool) or 'False'
    DEBUG_MODE = config('DEBUG_MODE', cast=bool) or 'False'
    SQL_port_String = str(SQL_PORT)
    processing_message = config('processing_message', cast=bool) or 'False'
    if DEBUG_MODE:
        print()  
        print(f'{Fore.CYAN}discord_token: {TOKEN}')
        print(f'{Fore.CYAN}open_AI_token: {OPEN_AI}')
        print(f'{Fore.CYAN}prefix:  {PREFIX}')
        print(f'{Fore.CYAN}sql_host: {SQL_HOST}')
        print(f'{Fore.CYAN}sql_user: {SQL_USER}')
        print(f'{Fore.CYAN}sq_pass:  {SQL_PASS}')
        print(f'{Fore.CYAN}sql_port: {SQL_PORT}')
        print(f'{Fore.CYAN}sql_database: {SQL_DATABASE}')
        print(f'{Fore.CYAN}sql_table: {SQL_TABLE}')
        print()
        print(f'{Fore.CYAN}opem_AI_support: {AI_ON}')
        print(f'{Fore.CYAN}debug_mode: {DEBUG_MODE}')
        print()
        print(f'{Fore.CYAN}processing_message: {processing_message}')
    return TOKEN, PREFIX, DISCORD_CHANNEL, SQL_HOST, SQL_USER, SQL_PORT, SQL_DATABASE, SQL_PASS, SQL_TABLE, OPEN_AI, SQL_port_String, AI_ON, DEBUG_MODE, processing_message

# Function to extract About information - left commented out as in original
# def about_pull(c, DEBUG_MODE):
#     url = c.about_url
#
#     response = requests.get(
#         url, cookies={'CONSENT':'YES+42'})
#
#     text = response.text
#
#     pattern = r'itemprop="description"\s+content="([^"]+)"'
#
#     match = re.search(pattern, text)
#     if match:
#         content = match.group(1)
#         channel_about = html.unescape(content)
#         return channel_about
#     else:
#         if DEBUG_MODE:
#             print(f"No match found.")
#         return