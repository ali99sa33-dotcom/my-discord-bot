import os
import discord
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# 1. كود فتح منفذ الويب الوهمي لخدع منصة رندر ومنع إغلاق البوت
class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_web_server():
    server = HTTPServer(("0.0.0.0", 10000), MyServer)
    server.serve_forever()

# تشغيل خادم الويب في خلفية الكود
threading.Thread(target=run_web_server, daemon=True).start()

# 2. كود البوت الأساسي والأوامر
TOKEN = os.getenv('TOKEN')
intents = discord.Intents.all()
 

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot is ready: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # التأكد من قراءة الأمر بشكل صحيح وتحويل الأحرف الصغيرة
    if message.content.strip() == '!ping':
        await message.channel.send('Pong!')

client.run(TOKEN)
