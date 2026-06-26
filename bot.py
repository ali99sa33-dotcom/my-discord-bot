import discord

TOKEN = "MTUxOTY1NTczNjQ5MjQyNTQ0Ng.Gw5hUZ.nO4uagT2EKeWKc9DCYRxrHiWQgJvMocZdFdUyU"
intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'تم تشغيل البوت: {client.user}')

client.run(TOKEN)
