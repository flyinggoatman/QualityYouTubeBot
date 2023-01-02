import re
from pytube import YouTube
from pytube import Channel
import requests
import html
from decouple import config








def channel_pull(channel_url):
    c = Channel(channel_url)
    channel_name = c.channel_name
    channel_id = c.channel_id
    channel_id_link = f"https://youtube.com/channel/{channel_id}"
    url = c.about_url
    channel_about = about_pull(c)



    if re.search("UCMDQxm7cUx3yXkfeHa5zJIQ", channel_id_link):
        print(f"######## Blocked Channel ########")
    print(f"Channel Name: {channel_name}")
    print(f"Channel ID: {channel_id}")
    print(f"Channel Link: {channel_id_link}")
    if re.search("UCMDQxm7cUx3yXkfeHa5zJIQ", channel_id_link):
        print(f"#################################")
    return channel_name, channel_id_link, channel_about
        
    
    
    
    
    
        
def video_pull(channel_url):
    YTV = YouTube(channel_url)
    channel_id = YTV.channel_id
    channel_id_link = YTV.channel_url

    c = Channel(channel_id_link)
    channel_name = c.channel_name
    channel_id = c.channel_id
    channel_html = c._about_html
    
    
    channel_about = about_pull(c)
    

    
    # This prints out the channel information to the Console.
    print(f"Channel ID: {channel_id}")
    print(f"Channel Name: {channel_name}")
    print(f"channel Link: {channel_id_link}")
    return channel_name, channel_id_link, channel_about



def env_pull():
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
    AI_ON = config('AI_ON', cast=bool)
    SQL_port_String = str(SQL_PORT)
    print(AI_ON)

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
    print(f'OPEN AI SUPPORT: {AI_ON}')
    print()
    return TOKEN, PREFIX, DISCORD_CHANNEL, SQL_HOST, SQL_USER, SQL_PORT, SQL_PASS, SQL_TABLE, OPEN_AI, SQL_port_String, AI_ON



def about_pull(c):
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
        print(f"No match found.")
    print()
    return channel_about

def open_ai_func(OPENAI_API_KEY, openai, channel_about, AI_ON):
    # Open AI code, will be added back in future.
    AI_O
    if AI_ON == False:
        channel_description = "OPEN AI SUPPORT COMING SOON!"
    else:
        # openai.api_key = OPENAI_API_KEY
        # text_input = str(input(channel_about))
        # text_input = text_input.strip()

        # response = openai.Completion.create(
        #         engine="text-davinci-002",
        #         prompt="\nDescription\n\ndescribe the following in 20 words that MUST start with\n \n\n\""+channel_name+" - A channel that...'\"\n\n\n"+channel_about+"\n\n\n\n",
        #         temperature=0.9,
        #         max_tokens=256,
        #         top_p=1,
        #         frequency_penalty=0,
        #         presence_penalty=0
        #         )


    # channel_diecription= print(response["choices"][0]["text"])
        return channel_description
    