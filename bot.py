import os
import discord

TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True 

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'تم تفعيل البوت بنجاح: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == '!ping':
        await message.channel.send('Pong!')

client.run(TOKEN)
