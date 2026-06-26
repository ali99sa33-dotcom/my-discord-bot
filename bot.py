import os
import datetime
import discord
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# 1. Web server to keep the bot alive 24/7 on Render
class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Ultimate Premium Bot is Active 24/7!")

def run_web_server():
    server = HTTPServer(("0.0.0.0", 10000), MyServer)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# 2. Bot settings and Intents configuration
TOKEN = os.getenv('TOKEN')
intents = discord.Intents.all()

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)

    async def on_ready(self):
        self.add_view(TicketPanelView())
        self.add_view(TicketCloseView())
        print(f'Bot is ready: {self.user}')
        await self.change_presence(activity=discord.Game(name="👑 Premium Protection | !help"))

client = MyBot()

async def send_to_log(guild, embed):
    log_channel = discord.utils.get(guild.text_channels, name='logs')
    if not log_channel:
        log_channel = discord.utils.get(guild.text_channels, name='اللوق')
    if log_channel:
        await log_channel.send(embed=embed)

# 3. Audit logs for roles and channels
@client.event
async def on_guild_role_update(before, after):
    if before.permissions != after.permissions:
        embed = discord.Embed(title="⚠️ تعديل صلاحيات رتبة (Role Permissions)", color=discord.Color.dark_orange(), timestamp=datetime.datetime.utcnow())
        embed.add_field(name="الرتبة المعدلة:", value=after.mention, inline=True)
        await send_to_log(after.guild, embed)

@client.event
async def on_guild_channel_update(before, after):
    if before.overwrites != after.overwrites:
        embed = discord.Embed(title="🔒 تعديل صلاحيات قناة (Channel Overwrites)", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
        embed.add_field(name="القناة:", value=after.mention, inline=True)
        await send_to_log(after.guild, embed)

# 4. Interactive Ticket System
class TicketPanelView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str, color: discord.Color):
        guild = interaction.guild
        user = interaction.user
        category = discord.utils.get(guild.categories, name="📌 TICKETS")
        if not category:
            category = await guild.create_category("📌 TICKETS")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        channel_name = f"{ticket_type}-{user.name}"
        ticket_channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites)
        await interaction.response.send_message(f"✅ تم فتح تذكرتك بنجاح: {ticket_channel.mention}", ephemeral=True)

        embed = discord.Embed(title=f"🎫 تذكرة جديدة | {ticket_type.upper()}", description=f"مرحباً بك {user.mention}، يرجى كتابة تفاصيل مشكلتك هنا وسيرد عليك الدعم الفني.", color=color)
        await ticket_channel.send(embed=embed, view=TicketCloseView())

    @discord.ui.button(label="تذكرة باند", style=discord.ButtonStyle.danger, custom_id="btn_ban", emoji="🔨")
    async def ban_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "appeal-ban", discord.Color.red())

    @discord.ui.button(label="تذكرة إدارة", style=discord.ButtonStyle.primary, custom_id="btn_admin", emoji="⚙️")
    async def admin_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "admin", discord.Color.blue())

    @discord.ui.button(label="تذكرة مساعدة", style=discord.ButtonStyle.success, custom_id="btn_help", emoji="🤝")
    async def help_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "help", discord.Color.green())

    @discord.ui.button(label="تذكرة متجر", style=discord.ButtonStyle.secondary, custom_id="btn_store", emoji="🛒")
    async def store_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "store", discord.Color.gold())

class TicketCloseView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="إغلاق التذكرة 🔒", style=discord.ButtonStyle.danger, custom_id="btn_close_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.delete()

# 5. Welcome System (💜 ‖ Welcome)
@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='💜-‖-welcome')
    if not channel: channel = discord.utils.get(member.guild.text_channels, name='welcome')
    if channel:
        embed = discord.Embed(title="👋 عضو جديد انضم إلينا!", description=f"يا مرحباً بك {member.mention} في سيرفرنا! ✨", color=discord.Color.purple())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"أنت العضو رقم {len(member.guild.members)} في السيرفر")
        await channel.send(embed=embed)

# 6. Message Logs
@client.event
async def on_message_delete(message):
    if message.author.bot: return
    embed = discord.Embed(title="🗑️ رسالة محذوفة", color=discord.Color.red())
    embed.add_field(name="المرسل:", value=message.author.mention, inline=True)
    embed.add_field(name="القناة:", value=message.channel.mention, inline=True)
    embed.add_field(name="المحتوى المحذوف:", value=message.content if message.content else "صورة أو ملف", inline=False)
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

# 7. Voice Logs (Join, Leave, Move, Mute, Deafen)
@client.event
async def on_voice_state_update(member, before, after):
    embed = discord.Embed(color=discord.Color.blue(), timestamp=datetime.datetime.utcnow())
    embed.set_author(name=f"{member.name}", icon_url=member.display_avatar.url)
    
    if before.channel is None and after.channel is not None:
        embed.title = "📥 دخول روم صوتي"
        embed.description = f"قام العضو {member.mention} بدخول الروم الصوتي: **{after.channel.name}**"
        await send_to_log(member.guild, embed)
    elif before.channel is not None and after.channel is None:
        embed.title = "📤 خروج من روم صوتي"
        embed.description = f"قام العضو {member.mention} بمغادرة الروم الصوتي: **{before.channel.name}**"
        embed.color = discord.Color.dark_red()
        await send_to_log(member.guild, embed)
    elif before.channel is not None and after.channel is not None and before.channel != after.channel:
        embed.title = "🔄 انتقال / سحب عضو"
        embed.description = f"تم نقل العضو {member.mention}\nمن روم: **{before.channel.name}**\nإلى روم: **{after.channel.name}**"
        embed.color = discord.Color.gold()
        await send_to_log(member.guild, embed)

    if before.self_mute != after.self_mute or before.mute != after.mute:
        embed.title = "🎙️ تغيير حالة المايك (كتم)"
        state = "قفل المايك 🤐" if after.self_mute or after.mute else "فتح المايك 🗣️"
        by_admin = "(إداري)" if after.mute or (before.mute and not after.mute) else "(تلقائي)"
        embed.description = f"العضو {member.mention} قام بـ **{state}** {by_admin}"
        embed.color = discord.Color.purple()
        await send_to_log(member.guild, embed)

    if before.self_deaf != after.self_deaf or before.deaf != after.deaf:
        embed.title = "🎧 تغيير حالة السماعة (دفن/صموت)"
        state = "شغّل الدفن 🔇" if after.self_deaf or after.deaf else "قفل الدفن 🔊"
        by_admin = "(إداري)" if after.deaf or (before.deaf and not after.deaf) else "(تلقائي)"
        embed.description = f"العضو {member.mention} قام بـ **{state}** {by_admin}"
        embed.color = discord.Color.dark_purple()
        await send_to_log(member.guild, embed)

# 8. Core Commands and Anti-Links Management
@client.event
async def on_message(message):
    if message.author.bot: return

    if "http" in message.content or "discord.gg" in message.content:
        if not message.author.guild_permissions.administrator:
            await message.delete()
            await message.channel.send(f"❌ {message.author.mention}، الروابط ممنوعة هنا لحماية السيرفر!", delete_after=5)
            return

    content = message.content.strip()

    if content == '!ticket':
        if message.author.guild_permissions.administrator:
            await message.delete()
            embed = discord.Embed(title="🎫 نظام تذاكر الدعم الفني | Ticket System", description="مرحباً بك في مركز خدمة السيرفر. اضغط على الزر بالأسفل لفتح تذكرة فوراً.\n\n🔨 **تذكرة باند**\n⚙️ **تذكرة إدارة**\n🤝 **تذكرة مساعدة**\n🛒 **تذكرة متجر**", color=discord.Color.purple())
            await message.channel.send(embed=embed, view=TicketPanelView())
            return

    if content.startswith('!role'):
        if message.author.guild_permissions.manage_roles:
            args = content.split()
