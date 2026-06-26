import os
import datetime
import discord
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# 1. Web server configuration for Render keep-alive
class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

def run_web_server():
    server = HTTPServer(("0.0.0.0", 10000), MyServer)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# 2. Core Bot initialization with all gateway intents
TOKEN = os.getenv('TOKEN')
intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot successfully logged in as: {client.user}')
    await client.change_presence(activity=discord.Game(name="👑 Ultimate Security | !help"))

async def send_to_log(guild, embed):
    log_channel = discord.utils.get(guild.text_channels, name='logs')
    if not log_channel: log_channel = discord.utils.get(guild.text_channels, name='اللوق')
    if log_channel: await log_channel.send(embed=embed)

# 3. Server administration logging (Permissions & Roles)
@client.event
async def on_guild_role_update(before, after):
    if before.permissions != after.permissions:
        embed = discord.Embed(title="⚠️ تعديل صلاحيات رتبة", color=discord.Color.dark_orange(), timestamp=datetime.datetime.utcnow())
        embed.add_field(name="الرتبة:", value=after.mention, inline=True)
        await send_to_log(after.guild, embed)

@client.event
async def on_guild_channel_update(before, after):
    if before.overwrites != after.overwrites:
        embed = discord.Embed(title="🔒 تعديل صلاحيات قناة", color=discord.Color.red(), timestamp=datetime.datetime.utcnow())
        embed.add_field(name="القناة:", value=after.mention, inline=True)
        await send_to_log(after.guild, embed)

# 4. Interactive button tickets panel
class TicketPanelView(discord.ui.View):
    def __init__(self) -> None: super().__init__(timeout=None)
    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str, color: discord.Color):
        guild = interaction.guild
        user = interaction.user
        category = discord.utils.get(guild.categories, name="📌 TICKETS")
        if not category: category = await guild.create_category("📌 TICKETS")
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }
        ticket_channel = await guild.create_text_channel(name=f"{ticket_type}-{user.name}", category=category, overwrites=overwrites)
        await interaction.response.send_message(f"✅ تم فتح تذكرتك: {ticket_channel.mention}", ephemeral=True)
        embed = discord.Embed(title=f"🎫 تذكرة جديدة | {ticket_type.upper()}", description=f"مرحباً بك {user.mention}، اكتب تفاصيل مشكلتك هنا.", color=color)
        await ticket_channel.send(embed=embed, view=TicketCloseView())

    @discord.ui.button(label="تذكرة باند", style=discord.ButtonStyle.danger, custom_id="btn_ban", emoji="🔨")
    async def ban_ticket(self, interaction: discord.Interaction, button: discord.ui.Button): await self.create_ticket(interaction, "appeal-ban", discord.Color.red())
    @discord.ui.button(label="تذكرة إدارة", style=discord.ButtonStyle.primary, custom_id="btn_admin", emoji="⚙️")
    async def admin_ticket(self, interaction: discord.Interaction, button: discord.ui.Button): await self.create_ticket(interaction, "admin", discord.Color.blue())
    @discord.ui.button(label="تذكرة مساعدة", style=discord.ButtonStyle.success, custom_id="btn_help", emoji="🤝")
    async def help_ticket(self, interaction: discord.Interaction, button: discord.ui.Button): await self.create_ticket(interaction, "help", discord.Color.green())
    @discord.ui.button(label="تذكرة متجر", style=discord.ButtonStyle.secondary, custom_id="btn_store", emoji="🛒")
    async def store_ticket(self, interaction: discord.Interaction, button: discord.ui.Button): await self.create_ticket(interaction, "store", discord.Color.gold())

class TicketCloseView(discord.ui.View):
    def __init__(self) -> None: super().__init__(timeout=None)
    @discord.ui.button(label="إغلاق التذكرة 🔒", style=discord.ButtonStyle.danger, custom_id="btn_close_ticket")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button): await interaction.channel.delete()

# 5. Core Discord events and logging handlers
@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='💜-‖-welcome')
    if not channel: channel = discord.utils.get(member.guild.text_channels, name='welcome')
    if channel:
        embed = discord.Embed(title="👋 عضو جديد انضم إلينا!", description=f"يا مرحباً بك {member.mention} في سيرفرنا! ✨", color=discord.Color.purple())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"أنت العضو رقم {len(member.guild.members)} في السيرفر")
        await channel.send(embed=embed)

@client.event
async def on_message_delete(message):
    if message.author.bot: return
    embed = discord.Embed(title="🗑️ الرسائل المحذوفة", color=discord.Color.red())
    embed.add_field(name="المرسل:", value=message.author.mention, inline=True)
    embed.add_field(name="القناة:", value=message.channel.mention, inline=True)
    embed.add_field(name="المحتوى המחذوف:", value=message.content if message.content else "صورة أو ملف", inline=False)
    await send_to_log(message.guild, embed)

@client.event
async def on_message_edit(before, after):
    if before.author.bot or before.content == after.content: return
    embed = discord.Embed(title="📝 الرسائل المعدلة", color=discord.Color.orange())
    embed.add_field(name="المرسل:", value=before.author.mention, inline=True)
    embed.add_field(name="القناة:", value=before.channel.mention, inline=True)
    embed.add_field(name="قبل:", value=before.content, inline=False)
    embed.add_field(name="بعد:", value=after.content, inline=False)
    await send_to_log(before.guild, embed)

@client.event
async def on_voice_state_update(member, before, after):
    embed = discord.Embed(color=discord.Color.blue(), timestamp=datetime.datetime.utcnow())
    embed.set_author(name=f"{member.name}", icon_url=member.display_avatar.url)
    if before.channel is None and after.channel is not None:
        embed.title = "📥 دخول روم صوتي"
        embed.description = f"العضو {member.mention} دخل الروم: **{after.channel.name}**"
        await send_to_log(member.guild, embed)
    elif before.channel is not None and after.channel is None:
        embed.title = "📤 خروج من روم صوتي"
        embed.description = f"العضو {member.mention} غادر الروم: **{before.channel.name}**"
        embed.color = discord.Color.dark_red()
        await send_to_log(member.guild, embed)
    elif before.channel is not None and after.channel is not None and before.channel != after.channel:
        embed.title = "🔄 انتقال / سحب عضو"
        embed.description = f"نقل العضو {member.mention} من **{before.channel.name}** إلى **{after.channel.name}**"
        embed.color = discord.Color.gold()
        await send_to_log(member.guild, embed)

    if before.self_mute != after.self_mute or before.mute != after.mute:
        embed.title = "🎙️ كتم المايك"
        state = "قفل المايك 🤐" if after.self_mute or after.mute else "فتح المايك 🗣️"
        embed.description = f"العضو {member.mention} قام بـ **{state}**"
        await send_to_log(member.guild, embed)

    if before.self_deaf != after.self_deaf or before.deaf != after.deaf:
        embed.title = "🎧 تشغيل الدفن"
        state = "شغّل الدفن 🔇" if after.self_deaf or after.deaf else "قفل الدفن 🔊"
        embed.description = f"العضو {member.mention} قام بـ **{state}**"
        await send_to_log(member.guild, embed)

# 6. Core message event router (Commands and Anti-Links)
@client.event
async def on_message(message):
    if message.author.bot: return
    if "http" in message.content or "discord.gg" in message.content:
        if not message.author.guild_permissions.administrator:
            await message.delete()
            return
    content = message.content.strip()
    if content == '!ticket':
        if message.author.guild_permissions.administrator:
            await message.delete()
            embed = discord.Embed(title="🎫 نظام تذاكر الدعم الفني | Ticket System", description="اضغط على الزر بالأسفل لفتح تذكرة فوراً.\n\n🔨 **تذكرة باند**\n⚙️ **تذكرة إدارة**\n🤝 **تذكرة مساعدة**\n🛒 **تذكرة متجر**", color=discord.Color.purple())
            await message.channel.send(embed=embed, view=TicketPanelView())
            return
    if content.startswith('!role'):
        if message.author.guild_permissions.manage_roles:
            args = content.split()
            if len(args) >= 4 and message.mentions and message.role_mentions:
                action = args.lower()
                user = message.mentions
                role = message.role_mentions
                if action == 'add': await user.add_roles(role)
                elif action == 'remove': await user.remove_roles(role)
        return
    if content == '!help':
        embed = discord.Embed(title="📜 لوحة تحكم ومواصفات البوت الكاملة والنهائية", color=discord.Color.blue())
        embed.add_field(name="⚙️ الأوامر:", value="`!ping` | `!server` | `!clear` | `!kick` | `!ban` | `!timeout`", inline=False)
        await message.channel.send(embed=embed)
        return
    if content == '!ping':
        await message.channel.send(f'🏓 Pong! {round(client.latency * 1000)}ms')
        return
    if content == '!server':
