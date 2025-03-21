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
import openai

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
    c = Channel(channel_url)
    channel_name = c.channel_name
    channel_id = c.channel_id
    channel_id_link = f"https://youtube.com/channel/{channel_id}"
    url = c.about_url
    # channel_about = about_pull(c, DEBUG_MODE)

    if DEBUG_MODE:
        if re.search("UCMDQxm7cUx3yXkfeHa5zJIQ", channel_id_link):
            print(f"######## Blocked Channel ########")
        print(f"Channel Name: {channel_name}")
        print(f"Channel ID: {channel_id}")
        print(f"Channel Link: {channel_id_link}")
        if re.search("UCMDQxm7cUx3yXkfeHa5zJIQ", channel_id_link):
            print(f"#################################")
    return channel_name, channel_id_link, channel_id

def video_pull(channel_url, DEBUG_MODE):
    YTV = YouTube(channel_url)
    channel_id = YTV.channel_id
    channel_id_link = YTV.channel_url

    c = Channel(channel_id_link)
    channel_name = c.channel_name
    channel_id = c.channel_id
    channel_html = c._about_html

    # channel_about = about_pull(c, DEBUG_MODE)

    if DEBUG_MODE:
        print(f"Channel ID: {channel_id}")
        print(f"Channel Name: {channel_name}")
        print(f"channel Link: {channel_id_link}")
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
        print(f'discord_token: {TOKEN}')
        print(f'open_AI_token: {OPEN_AI}')
        print(f'prefix:  {PREFIX}')
        print(f'sql_host: {SQL_HOST}')
        print(f'sql_user: {SQL_USER}')
        print(f'sq_pass:  {SQL_PASS}')
        print(f'sql_port: {SQL_PORT}')
        print(f'sql_database: {SQL_DATABASE}')
        print(f'sql_table: {SQL_TABLE}')
        print()
        print(f'opem_AI_support: {AI_ON}')
        print(f'debug_mode: {DEBUG_MODE}')
        print()
        print(f'processing_message: {processing_message}')
    return TOKEN, PREFIX, DISCORD_CHANNEL, SQL_HOST, SQL_USER, SQL_PORT, SQL_DATABASE, SQL_PASS, SQL_TABLE, OPEN_AI, SQL_port_String, AI_ON, DEBUG_MODE, processing_message

# def about_pull(c, DEBUG_MODE):
#     url = c.about_url

#     response = requests.get(
#         url, cookies={'CONSENT':'YES+42'})

#     text = response.text

#     pattern = r'itemprop="description"\s+content="([^"]+)"'

#     match = re.search(pattern, text)
#     if match:
#         content = match.group(1)
#         channel_about = html.unescape(content)
#         return channel_about
#     else:
#         if DEBUG_MODE:
#             print(f"No match found.")
#         return

# def read_prompt_from_file(file_path):
#     try:
#         with open(file_path, "r") as file:
#             return file.read().strip()
#     except FileNotFoundError:
#         print(f"Error: The file {file_path} was not found.")
#         return "You are a helpful assistant."  # Fallback prompt in case the file is not found

# async def open_ai_func(OPENAI_API_KEY, channel_about, AI_ON, channel_name, message):
#     if not AI_ON:
#         channel_description = "OPEN AI SUPPORT COMING SOON!"
#         await message.channel.send(channel_description, delete_after=10)
#         return channel_description

#     openai.api_key = OPENAI_API_KEY

#     try:
#         # Read the system prompt from the file
#         system_prompt = read_prompt_from_file("AI_PROMPT.txt")

#         response = openai.ChatCompletion.create(
#             model="gpt-4",
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": f"Summarize the following YouTube channel description in one sentence: {channel_about}"}
#             ],
#             temperature=0.7,
#             max_tokens=60,
#             top_p=1.0,
#             frequency_penalty=0.0,
#             presence_penalty=0.0,
#         )
#         channel_description = response.choices[0].message['content'].strip()
#         await message.channel.send(channel_description, delete_after=10)  # Send the generated description directly
#     except Exception as e:
#         print(f"Error with OpenAI call: {e}")
#         print("Failed to generate channel description.")
#         channel_description = None

#     return channel_description
