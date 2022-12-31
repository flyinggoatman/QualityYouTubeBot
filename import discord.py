import discord

# Set the client and channel that you want to retrieve the message history for


intents = discord.Intents.all()
client = discord.Client(intents=intents)

async def get_message_history():
    # Retrieve the message history for the channel
    channel = client.get_channel(938207947878703187)
    async for message in channel.history(limit=6):
        
        # Print each message to the console
        print(message.content)
        print("-")

    await get_message_history()

client.run('OTM4MjEyMDIxOTkwNzM1OTAy.G1vqqM.ELFhdKhs0cy4_dMd9Pfd0bX_dk7wIiy5ysmZLM')