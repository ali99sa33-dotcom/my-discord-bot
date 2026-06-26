import os
import discord
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# 1. خادم الويب لإبقاء البوت حياً 24 ساعة في منصة رندر
class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is alive and running 24/7!")

def run_web_server():
    server = HTTPServer(("0.0.0.0", 10000), MyServer)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# 2. إعدادات البوت والصلاحيات الكاملة الشاملة
TOKEN = os.getenv('TOKEN')
intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'تم تشغيل البوت الشامل بنجاح: {client.user}')
    # وضع حالة البوت (Playing...)
    await client.change_presence(activity=discord.Game(name="!help | لحماية السيرفر"))

# 3. نظام الترحيب التلقائي بالأعضاء الجدد (💜 ‖ Welcome)
@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='💜-‖-welcome')
    if not channel:
        channel = discord.utils.get(member.guild.text_channels, name='welcome')
    if channel:
        embed = discord.Embed(
            title="👋 عضو جديد انضم إلينا!",
            description=f"يا مرحباً بك {member.mention} في سيرفرنا!\n\nيسعدنا جداً انضمامك، نتمنى لك وقتاً ممتعاً ✨",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"أنت العضو رقم {len(member.guild.members)} في السيرفر")
        await channel.send(embed=embed)

# 4. نظام اللوق وتتبع الرسائل المحذوفة والمعدلة (logs)
@client.event
async def on_message_delete(message):
    if message.author.bot: return
    log_channel = discord.utils.get(message.guild.text_channels, name='logs')
    if log_channel:
        embed = discord.Embed(title="🗑️ رسالة محذوفة", color=discord.Color.red())
        embed.add_field(name="المرسل:", value=message.author.mention, inline=True)
        embed.add_field(name="القناة:", value=message.channel.mention, inline=True)
        embed.add_field(name="محتوى الرسالة:", value=message.content if message.content else "لا يوجد نص (صورة أو ملف)", inline=False)
        await log_channel.send(embed=embed)

@client.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content: return
    log_channel = discord.utils.get(before.guild.text_channels, name='logs')
    if log_channel:
        embed = discord.Embed(title="📝 رسالة معدّلة", color=discord.Color.orange())
        embed.add_field(name="المرسل:", value=before.author.mention, inline=True)
        embed.add_field(name="القناة:", value=before.channel.mention, inline=True)
        embed.add_field(name="قبل التعديل:", value=before.content, inline=False)
        embed.add_field(name="بعد التعديل:", value=after.content, inline=False)
        await log_channel.send(embed=embed)

# 5. نظام معالجة الأوامر، الحماية، والإدارة
@client.event
async def on_message(message):
    if message.author.bot: return

    # 🛑 نظام الحماية: منع إرسال روابط الإنترنت العشوائية لغير الإداريين
    if "http" in message.content or "discord.gg" in message.content:
        if not message.author.guild_permissions.administrator:
            await message.delete()
            await message.channel.send(f"❌ {message.author.mention}، يمنع نشر الروابط في هذا السيرفر لحمايته!", delete_after=5)
            return

    # قائمة الأوامر التفاعلية
    content = message.content.strip()

    # أمر قائمة المساعدة
    if content == '!help':
        embed = discord.Embed(title="📜 قائمة أوامر البوت الشامل", color=discord.Color.blue())
        embed.add_field(name="⚙️ الأوامر العامة:", value="`!ping` - لفحص سرعة الاتصال\n`!server` - لعرض معلومات السيرفر", inline=False)
        embed.add_field(name="🛡️ أوامر الإدارة:", value="`!clear [العدد]` - لتنظيف الشات\n`!kick @user` - لطرد عضو\n`!ban @user` - لحظر عضو كلياً", inline=False)
        embed.set_footer(text="البوت يعمل بنظام حماية تلقائي ضد الروابط واللوق")
        await message.channel.send(embed=embed)

    # أمر الفحص (Ping)
    if content == '!ping':
        await message.channel.send(f'🏓 Pong! السرعة الحالية: {round(client.latency * 1000)}ms')

    # أمر معلومات السيرفر (Server Info)
    if content == '!server':
        embed = discord.Embed(title=f"📊 معلومات سيرفر {message.guild.name}", color=discord.Color.gold())
        embed.add_field(name="👑 صاحب السيرفر:", value=message.guild.owner.mention if message.guild.owner else "غير معروف", inline=True)
        embed.add_field(name="👥 عدد الأعضاء:", value=str(message.guild.member_count), inline=True)
        embed.add_field(name="🆔 آيدي السيرفر:", value=str(message.guild.id), inline=False)
        await message.channel.send(embed=embed)

    # أمر مسح الشات وتنظيف الرسائل (!clear 50)
    if content.startswith('!clear'):
        if message.author.guild_permissions.manage_messages:
            args = content.split()
            amount = 100 # العدد الافتراضي إذا لم يحدد المبرمج
            if len(args) > 1 and args[1].isdigit():
                amount = int(args[1]) + 1
            await message.channel.purge(limit=amount)
            await message.channel.send(f"🧹 تم تنظيف الشات وحذف {amount-1} رسالة بنجاح.", delete_after=5)
        else:
            await message.channel.send("❌ ليس لديك صلاحية `إدارة الرسائل` لاستخدام هذا الأمر.")

    # أمر الطرد الاداري (!kick @user)
    if content.startswith('!kick'):
        if message.author.guild_permissions.kick_members:
            if message.mentions:
                user = message.mentions[0]
                await user.kick(reason="أمر إداري")
                await message.channel.send(f"✅ تم طرد {user.mention} بنجاح.")
            else:
                await message.channel.send("❌ منشن العضو المُراد طرده. مثال: `!kick @user`")
        else:
            await message.channel.send("❌ لا تملك صلاحية طرد الأعضاء.")

    # أمر الحظر الإداري (!ban @user)
    if content.startswith('!ban'):
        if message.author.guild_permissions.ban_members:
            if message.mentions:
                user = message.mentions[0]
                await user.ban(reason="أمر إداري")
                await message.channel.send(f"🚨 تم حظر {user.mention} من السيرفر كلياً.")
            else:
                await message.channel.send("❌ منشن العضو المُراد حظره. مثال: `!ban @user`")
        else:
            await message.channel.send("❌ لا تملك صلاحية حظر الأعضاء.")

client.run(TOKEN)
