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
import json

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
    """Extract channel information from a channel URL."""
    try:
        # Check if it's a video URL (watch?v=) - redirect to video_pull
        if re.search(r"youtube\.com/watch\?v=|youtu\.be/", channel_url):
            if DEBUG_MODE:
                print(f"{Fore.YELLOW}Detected watch URL, redirecting to video_pull: {channel_url}")
            return video_pull(channel_url, DEBUG_MODE)
        
        # Try the standard pytube Channel method
        c = Channel(channel_url)
        channel_name = c.channel_name
        channel_id = c.channel_id
        channel_id_link = f"https://youtube.com/channel/{channel_id}"
    except Exception as e:
        if DEBUG_MODE:
            print(f"{Fore.RED}Error in channel_pull: {e}")
        
        # Enhanced alternative extraction methods
        try:
            # Handle @username type URLs
            if '@' in channel_url:
                username = channel_url.split('@')[-1].split('/')[0].split('?')[0]
                channel_id = f"@{username}"
                channel_id_link = f"https://youtube.com/{channel_id}"
                
                # Try to get a better channel name by fetching the page
                try:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    response = requests.get(channel_id_link, headers=headers)
                    html_content = response.text
                    
                    # Try to extract channel name from HTML
                    channel_name_match = re.search(r'<meta name="title" content="([^"]+)"', html_content) or \
                                         re.search(r'<meta property="og:title" content="([^"]+)"', html_content)
                    if channel_name_match:
                        channel_name = html.unescape(channel_name_match.group(1))
                    else:
                        channel_name = username  # Use username as fallback name
                except Exception:
                    channel_name = username  # Use username as fallback name
                
                return channel_name, channel_id_link, channel_id
            
            # Extract channel ID using improved regex
            channel_match = re.search(r"(?:\/channel\/|\/c\/|\/user\/)([^\/\?]+)", channel_url)
            if channel_match:
                channel_id = channel_match.group(1)
                channel_id_link = f"https://youtube.com/channel/{channel_id}"
                
                # Try to get a better channel name by fetching the page
                try:
                    headers = {"User-Agent": "Mozilla/5.0"}
                    response = requests.get(channel_id_link, headers=headers)
                    html_content = response.text
                    
                    # Try to extract channel name from HTML
                    channel_name_match = re.search(r'<meta name="title" content="([^"]+)"', html_content) or \
                                         re.search(r'<meta property="og:title" content="([^"]+)"', html_content)
                    if channel_name_match:
                        channel_name = html.unescape(channel_name_match.group(1))
                    else:
                        channel_name = f"Channel {channel_id}"  # Use ID as fallback name
                except Exception:
                    channel_name = f"Channel {channel_id}"  # Use ID as fallback name
                
                return channel_name, channel_id_link, channel_id
            
            # Check once more for video URLs and redirect to video_pull
            if "youtube.com/watch" in channel_url or "youtu.be/" in channel_url:
                if DEBUG_MODE:
                    print(f"{Fore.YELLOW}Detected watch URL in fallback, redirecting to video_pull: {channel_url}")
                return video_pull(channel_url, DEBUG_MODE)
            
            # If we get here, we couldn't extract channel info with any method
            raise ValueError(f"Could not parse channel information from URL: {channel_url}")
            
        except Exception as nested_e:
            if DEBUG_MODE:
                print(f"{Fore.RED}Error in channel_pull alternative method: {nested_e}")
            
            # One final attempt - if it's a video URL, try video_pull
            if "youtube.com/watch" in channel_url or "youtu.be/" in channel_url:
                if DEBUG_MODE:
                    print(f"{Fore.YELLOW}Last resort attempt with video_pull: {channel_url}")
                try:
                    return video_pull(channel_url, DEBUG_MODE)
                except Exception as video_e:
                    if DEBUG_MODE:
                        print(f"{Fore.RED}Last resort video_pull also failed: {video_e}")
            
            raise ValueError(f"Could not extract channel information from URL: {channel_url}")

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
    """Extract channel information from a video URL."""
    if DEBUG_MODE:
        print(f"{Fore.CYAN}Video pull called with URL: {channel_url}")
        
    try:
        # Extract video ID first - this should work for both youtube.com/watch?v= and youtu.be/ URLs
        video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", channel_url)
        if not video_id_match:
            raise ValueError(f"Could not extract video ID from URL: {channel_url}")
        
        video_id = video_id_match.group(1)
        watch_url = f"https://www.youtube.com/watch?v={video_id}"
        
        if DEBUG_MODE:
            print(f"{Fore.CYAN}Extracted video ID: {video_id}, watch URL: {watch_url}")
        
        # First attempt: Use pytube
        try:
            YTV = YouTube(watch_url)
            channel_id = YTV.channel_id
            if channel_id:
                channel_id_link = YTV.channel_url
                channel_name = YTV.author or "Unknown Channel"
                
                if DEBUG_MODE:
                    print(f"{Fore.GREEN}Successfully extracted channel info using pytube: ID={channel_id}, Name={channel_name}")
                
                return channel_name, channel_id_link, channel_id
        except Exception as pytube_error:
            if DEBUG_MODE:
                print(f"{Fore.RED}Pytube extraction failed: {pytube_error}")
        
        # Second attempt: Direct HTML scraping
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9"
        }
        response = requests.get(watch_url, headers=headers)
        html_content = response.text
        
        if DEBUG_MODE:
            print(f"{Fore.CYAN}HTML request status code: {response.status_code}")
        
        # Try multiple patterns to extract channel ID
        channel_id_patterns = [
            r'"channelId":"([^"]+)"',
            r'<meta itemprop="channelId" content="([^"]+)"',
            r'"externalChannelId":"([^"]+)"',
            r'<link itemprop="url" href="https://www.youtube.com/channel/([^"]+)"'
        ]
        
        channel_id = None
        for pattern in channel_id_patterns:
            match = re.search(pattern, html_content)
            if match:
                channel_id = match.group(1)
                if DEBUG_MODE:
                    print(f"{Fore.GREEN}Found channel ID with pattern: {pattern}")
                break
                
        if not channel_id:
            # Try to extract from initial data JSON
            try:
                initial_data_match = re.search(r'ytInitialData\s*=\s*({.+?});', html_content, re.DOTALL)
                if initial_data_match:
                    json_str = initial_data_match.group(1)
                    data = json.loads(json_str)
                    channel_id = data.get('contents', {}).get('twoColumnWatchNextResults', {}).get('results', {}).get('results', {}).get('contents', [{}])[0].get('videoPrimaryInfoRenderer', {}).get('owner', {}).get('videoOwnerRenderer', {}).get('navigationEndpoint', {}).get('browseEndpoint', {}).get('browseId')
                    if DEBUG_MODE and channel_id:
                        print(f"{Fore.GREEN}Found channel ID in ytInitialData: {channel_id}")
            except Exception as json_error:
                if DEBUG_MODE:
                    print(f"{Fore.RED}JSON extraction error: {json_error}")
        
        if not channel_id:
            raise ValueError(f"Could not extract channel ID from video page: {watch_url}")
                
        channel_id_link = f"https://youtube.com/channel/{channel_id}"
        
        # Try multiple patterns to extract channel name
        channel_name_patterns = [
            r'"ownerChannelName":"([^"]+)"',
            r'"author":"([^"]+)"',
            r'<span itemprop="author".*?<link itemprop="name" content="([^"]+)"',
            r'<link rel="canonical" href="https://www.youtube.com/channel/[^"]+"><link rel="alternate" href="android-app://com.google.android.youtube/http/www.youtube.com/channel/[^"]+"><link rel="alternate" href="ios-app://544007664/http/www.youtube.com/channel/[^"]+"><title>([^<]+)',
            r'<meta name="title" content="([^"]+)"'
        ]
        
        channel_name = None
        for pattern in channel_name_patterns:
            match = re.search(pattern, html_content)
            if match:
                channel_name = html.unescape(match.group(1))
                if DEBUG_MODE:
                    print(f"{Fore.GREEN}Found channel name with pattern: {pattern}")
                break
            
        # If no name found, use a fallback
        if not channel_name:
            channel_name = f"Channel {channel_id}"
            if DEBUG_MODE:
                print(f"{Fore.YELLOW}Using fallback channel name: {channel_name}")
                
    except Exception as e:
        if DEBUG_MODE:
            print(f"{Fore.RED}Error in video_pull fallback method: {e}")
        raise ValueError(f"Could not extract channel information from video URL: {channel_url}. Error: {e}")

    if DEBUG_MODE:
        print(f"{Fore.YELLOW}Channel ID: {channel_id}")
        print(f"{Fore.WHITE}Channel Name: {channel_name}")
        print(f"{Fore.WHITE}Channel Link: {channel_id_link}")
        
    return channel_name, channel_id_link, channel_id

def env_pull(DEBUG_MODE):
    """Extract environment variables for configuration."""
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
#         channel_about = html.unescape(content)a
#         return channel_about
#     else:
#         if DEBUG_MODE:
#             print(f"No match found.")
#         return