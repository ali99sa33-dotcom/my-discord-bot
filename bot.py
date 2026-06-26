import os
import datetime
import discord
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# 1. خادم الويب لإبقاء البوت حياً 24 ساعة في منصة رندر
class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is fully active 24/7 with all premium features!")

def run_web_server():
    server = HTTPServer(("0.0.0.0", 10000), MyServer)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# 2. إعدادات البوت والصلاحيات الشاملة الخارقة
TOKEN = os.getenv('TOKEN')
intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'تم تفعيل البوت الشامل والكامل بنجاح: {client.user}')
    await client.change_presence(activity=discord.Game(name="🛡️ نظام الحماية الشامل | !help"))

# Helper function لـ إرسال اللوق بشكل منظم ونظيف
async def send_to_log(guild, embed):
    log_channel = discord.utils.get(guild.text_channels, name='logs')
    if not log_channel:
        log_channel = discord.utils.get(guild.text_channels, name='اللوق')
    if log_channel:
        await log_channel.send(embed=embed)

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

# 4. لوق تتبع الرسائل المحذوفة والمعدلة
@client.event
async def on_message_delete(message):
    if message.author.bot: return
    embed = discord.Embed(title="🗑️ رسالة محذوفة", color=discord.Color.red())
    embed.add_field(name="المرسل:", value=message.author.mention, inline=True)
    embed.add_field(name="القناة:", value=message.channel.mention, inline=True)
    embed.add_field(name="المحتوى المحذوف:", value=message.content if message.content else "لا يوجد نص (صورة أو ملف)", inline=False)
    await send_to_log(message.guild, embed)

@client.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content: return
    embed = discord.Embed(title="📝 رسالة معدّلة", color=discord.Color.orange())
    embed.add_field(name="المرسل:", value=before.author.mention, inline=True)
    embed.add_field(name="القناة:", value=before.channel.mention, inline=True)
    embed.add_field(name="قبل التعديل:", value=before.content, inline=False)
    embed.add_field(name="بعد التعديل:", value=after.content, inline=False)
    await send_to_log(before.guild, embed)

# 5. 🔥 نظام لوق الرومات الصوتية الخارق (تحركات، سحب، طرد، كتم، دفن)
@client.event
async def on_voice_state_update(member, before, after):
    embed = discord.Embed(color=discord.Color.blue(), timestamp=datetime.datetime.utcnow())
    embed.set_author(name=f"{member.name}", icon_url=member.display_avatar.url)
    
    # دخول روم صوتي
    if before.channel is None and after.channel is not None:
        embed.title = "📥 دخول روم صوتي"
        embed.description = f"قام العضو {member.mention} بدخول الروم الصوتي: **{after.channel.name}**"
        await send_to_log(member.guild, embed)
        
    # خروج من روم صوتي
    elif before.channel is not None and after.channel is None:
        embed.title = "📤 خروج من روم صوتي"
        embed.description = f"قام العضو {member.mention} بمغادرة الروم الصوتي: **{before.channel.name}**"
        embed.color = discord.Color.dark_red()
        await send_to_log(member.guild, embed)
        
    # الانتقال أو السحب بين الرومات
    elif before.channel is not None and after.channel is not None and before.channel != after.channel:
        embed.title = "🔄 انتقال / سحب عضو"
        embed.description = f"تم نقل العضو {member.mention}\nمن روم: **{before.channel.name}**\nإلى روم: **{after.channel.name}**"
        embed.color = discord.Color.gold()
        await send_to_log(member.guild, embed)

    # تتبع الكتم والدفن (Mute / Deafen) من الإدارة أو الشخص نفسه
    if before.self_mute != after.self_mute or before.mute != after.mute:
        embed.title = "🎙️ تغيير حالة المايك (كتم)"
        state = "قفل المايك 🤐" if after.self_mute or after.mute else "فتح المايك 🗣️"
        by_admin = "(بواسطة الإدارة/سيرفر)" if after.mute or (before.mute and not after.mute) else "(تلقائي من الشخص)"
        embed.description = f"العضو {member.mention} قام بـ **{state}** {by_admin}"
        embed.color = discord.Color.purple()
        await send_to_log(member.guild, embed)

    if before.self_deaf != after.self_deaf or before.deaf != after.deaf:
        embed.title = "🎧 تغيير حالة السماعة (دفن/صموت)"
        state = "شغّل الدفن (صموت) 🔇" if after.self_deaf or after.deaf else "قفل الدفن (سماع) 🔊"
        by_admin = "(بواسطة الإدارة/سيرفر)" if after.deaf or (before.deaf and not after.deaf) else "(تلقائي من الشخص)"
        embed.description = f"العضو {member.mention} قام بـ **{state}** {by_admin}"
        embed.color = discord.Color.dark_purple()
        await send_to_log(member.guild, embed)

# 6. نظام معالجة الأوامر، الحماية، والإدارة
@client.event
async def on_message(message):
    if message.author.bot: return

    # نظام الحماية من الروابط
    if "http" in message.content or "discord.gg" in message.content:
        if not message.author.guild_permissions.administrator:
            await message.delete()
            await message.channel.send(f"❌ {message.author.mention}، يمنع نشر الروابط لحماية السيرفر!", delete_after=5)
            return

    content = message.content.strip()

    # أمر قائمة المساعدة المحدثة
    if content == '!help':
        embed = discord.Embed(title="📜 لوحة تحكم البوت الكاملة والشاملة", color=discord.Color.green())
        embed.add_field(name="⚙️ الأوامر العامة:", value="`!ping` - فحص سرعة الاتصال\n`!server` - معلومات السيرفر", inline=False)
        embed.add_field(name="🛡️ أوامر الإدارة الحازمة:", value="`!clear [العدد]` - تنظيف الشات\n`!kick @user` - طرد عضو\n`!ban @user` - حظر عضو\n`!timeout @user [الدقائق]` - تايم أوت\n`!untimeout @user` - فك التايم أوت", inline=False)
        embed.set_footer(text="البوت يراقب ويحمي السيرفر والرومات الصوتية تلقائياً على مدار الساعة")
        await message.channel.send(embed=embed)

    if content == '!ping':
        await message.channel.send(f'🏓 Pong! {round(client.latency * 1000)}ms')

    if content == '!server':
        embed = discord.Embed(title=f"📊 تفاصيل سيرفر {message.guild.name}", color=discord.Color.gold())
        embed.add_field(name="👑 المالك:", value=message.guild.owner.mention if message.guild.owner else "غير معروف", inline=True)
        embed.add_field(name="👥 الأعضاء:", value=str(message.guild.member_count), inline=True)
        await message.channel.send(embed=embed)

    # أمر تنظيف الشات
    if content.startswith('!clear'):
        if message.author.guild_permissions.manage_messages:
            args = content.split()
            amount = 100
            if len(args) > 1 and args[1].isdigit():
                amount = int(args[1]) + 1
            await message.channel.purge(limit=amount)
            await message.channel.send(f"🧹 تم تنظيف الشات وحذف {amount-1} رسالة.", delete_after=5)

    # أوامر الكيك والـبان
    if content.startswith('!kick'):
        if message.author.guild_permissions.kick_members and message.mentions:
            user = message.mentions[0]
            await user.kick(reason="أمر إداري")
            await message.channel.send(f"✅ تم طرد {user.mention} بنجاح.")

    if content.startswith('!ban'):
        if message.author.guild_permissions.ban_members and message.mentions:
            user = message.mentions[0]
            await user.ban(reason="أمر إداري")
            await message.channel.send(f"🚨 تم حظر {user.mention} كلياً.")

    # أوامر التايم أوت وفكه
    if content.startswith('!timeout'):
        if message.author.guild_permissions.moderate_members and message.mentions:
            user = message.mentions[0]
            args = content.split()
            minutes = 10
            if len(args) > 2 and args[2].isdigit():
                minutes = int(args[2])
            await user.timeout(datetime.timedelta(minutes=minutes), reason="إجراء إداري")
            await message.channel.send(f"🤫 تم إسكات {user.mention} لمدة {minutes} دقيقة.")

    if content.startswith('!untimeout'):
        if message.author.guild_permissions.moderate_members and message.mentions:
            user = message.mentions[0]
            await user.timeout(None)
            await message.channel.send(f"🔊 تم فك التايم أوت عن {user.mention}، يمكنه التحدث الآن.")

client.run(TOKEN)
