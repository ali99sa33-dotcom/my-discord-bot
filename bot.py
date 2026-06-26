import discord

TOKEN = "MTUxOTY1NTczNjQ5MjQyNTQ0Ng.GSOz9E.Ub5o_wyWVFkEA08K98ZYIH5FQCDIiEt9VFwqcw"
intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'تم تشغيل البوت: {client.user}')

client.run(TOKEN)