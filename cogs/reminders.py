
import time, re
import discord
from discord.ext import commands, tasks
from discord import app_commands

from .ui_helpers import add_info_fields, brand_embed

DURATION_RE = re.compile(r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?', re.I)

def parse_duration(s: str):
    m = DURATION_RE.fullmatch(s.strip())
    if not m:
        return None
    d, h, mnt, sec = (int(x) if x else 0 for x in m.groups())
    total = d*86400 + h*3600 + mnt*60 + sec
    return total if total > 0 else None

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.checker.start()

    def cog_unload(self):
        self.checker.cancel()

    @app_commands.command(name="remind", description="Setze eine Erinnerung, z. B. `10m Pause machen`.")
    @app_commands.describe(when="Dauer wie 10m, 2h, 1d2h", text="Text der Erinnerung")
    async def remind(self, interaction: discord.Interaction, when: str, text: str):
        seconds = parse_duration(when)
        if not seconds:
            return await interaction.response.send_message("Format: `XdYhZmWs`, z.B. `10m` oder `1h30m`.", ephemeral=True)
        now = int(time.time())
        due = now + seconds
        await self.bot.db.execute(
            "INSERT INTO reminders(guild_id,user_id,channel_id,text,due_ts,created_ts,done) VALUES(?,?,?,?,?,?,0)",
            (interaction.guild_id, interaction.user.id, interaction.channel_id, text, due, now)
        )
        await self.bot.db.commit()
        embed = brand_embed(
            "Reminder gesetzt",
            description=f"„{text}“",
            icon="⏰",
            colour=discord.Colour.from_str("#f97316"),
        )
        add_info_fields(
            embed,
            [
                ("Auslösung", f"<t:{due}:R> – <t:{due}:F>"),
                ("Kanal", interaction.channel.mention if interaction.channel else "DM"),
            ],
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @tasks.loop(seconds=10)
    async def checker(self):
        now = int(time.time())
        async with self.bot.db.execute("SELECT id, guild_id, user_id, channel_id, text FROM reminders WHERE done=0 AND due_ts<=?", (now,)) as cur:
            rows = await cur.fetchall()
        for rid, gid, uid, cid, text in rows:
            channel = self.bot.get_channel(cid)
            try:
                if channel:
                    embed = brand_embed(
                        "Reminder fällig",
                        description=f"**{text}**",
                        icon="⏰",
                        colour=discord.Colour.from_str("#facc15"),
                    )
                    embed.add_field(name="Empfänger", value=f"<@{uid}>", inline=True)
                    embed.timestamp = discord.utils.utcnow()
                    await channel.send(embed=embed)
            except Exception:
                pass
            await self.bot.db.execute("UPDATE reminders SET done=1 WHERE id=?", (rid,))
        if rows:
            await self.bot.db.commit()

    @checker.before_loop
    async def before(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Reminders(bot))
