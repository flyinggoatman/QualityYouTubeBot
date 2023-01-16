import re
from pytube import YouTube
from pytube import Channel
import requests
import html
from decouple import config
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import Column, Text, VARCHAR, DateTime, select
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import datetime

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
        created_at = datetime.datetime.now() # get current date and time
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




def channel_pull(channel_url, DEBUG_MODE):
    c = Channel(channel_url)
    channel_name = c.channel_name
    channel_id = c.channel_id
    channel_id_link = f"https://youtube.com/channel/{channel_id}"
    url = c.about_url
    channel_about = about_pull(c, DEBUG_MODE)


    if DEBUG_MODE == True:
        if re.search("UCMDQxm7cUx3yXkfeHa5zJIQ", channel_id_link):
            print(f"######## Blocked Channel ########")
        print(f"Channel Name: {channel_name}")
        print(f"Channel ID: {channel_id}")
        print(f"Channel Link: {channel_id_link}")
        if re.search("UCMDQxm7cUx3yXkfeHa5zJIQ", channel_id_link):
            print(f"#################################")
    return channel_name, channel_id_link, channel_about, channel_id
        
    
    
    
    
    
        
def video_pull(channel_url, DEBUG_MODE):
    YTV = YouTube(channel_url)
    channel_id = YTV.channel_id
    channel_id_link = YTV.channel_url

    c = Channel(channel_id_link)
    channel_name = c.channel_name
    channel_id = c.channel_id
    channel_html = c._about_html
    
    
    channel_about = about_pull(c, DEBUG_MODE)
    

    
    # This prints out the channel information to the Console.
    if DEBUG_MODE == True:
        print(f"Channel ID: {channel_id}")
        print(f"Channel Name: {channel_name}")
        print(f"channel Link: {channel_id_link}")
    return channel_name, channel_id_link, channel_about, channel_id



def env_pull(DEBUG_MODE):
    TOKEN = config('TOKEN') or ''
    PREFIX = config('PREFIX') or ''
    DISCORD_CHANNEL = config('DISCORD_CHANNEL ', default='938207947878703187') or ''
    SQL_HOST = config('SQL_HOST', default='localhost')
    SQL_USER = config('SQL_USER') or ''
    SQL_PASS = config('SQL_PASS') or ''
    SQL_PORT = config('SQL_PORT', cast=int) or 5432
    SQL_DATABASE = config('SQL_DATABASE') or ''
    SQL_TABLE = config('SQL_TABLE') or ''
    OPEN_AI = config('OPEN_AI') or ''
    AI_ON = config('AI_ON', cast=bool) or 'False'
    DEBUG_MODE = config ('DEBUG_MODE', cast=bool) or 'False'
    SQL_port_String = str(SQL_PORT)
    if DEBUG_MODE == True:
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
    else:
        print()
    return TOKEN, PREFIX, DISCORD_CHANNEL, SQL_HOST, SQL_USER, SQL_PORT, SQL_DATABASE, SQL_PASS, SQL_TABLE, OPEN_AI, SQL_port_String, AI_ON, DEBUG_MODE




def about_pull(c, DEBUG_MODE):
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
        return channel_about
    else:
        if DEBUG_MODE == True:
            print(f"No match found.")
        else:
            return

async def open_ai_func(OPENAI_API_KEY, openai, channel_about, AI_ON, channel_name, message):
    # Open AI code, will be added back in future.
    
    if AI_ON == False:
        channel_description = "OPEN AI SUPPORT COMING SOON!"
    else:
        openai.api_key = OPENAI_API_KEY
        text_input = str(input(channel_about))
        text_input = text_input.strip()

        response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=f"\nDescription\n\ndescribe the following detailed in 20 to 30 words that MUST start with\n \n\n\' A channel that...' in one sentance\"\n\n\n{channel_about}\n\n\n\n",
                temperature=1.0,
                max_tokens=256,
                top_p=1,
                frequency_penalty=1.0,
                presence_penalty=0
                )

        delete_message = await message.channel.send(response["choices"][0]["text"])
        channel_description =  print(response["choices"][0]["text"])
        await delete_message.delete()
    return channel_description

