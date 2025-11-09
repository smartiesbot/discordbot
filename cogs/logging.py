
import discord
from discord.ext import commands
from discord import app_commands

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="log-set", description="Lege den Kanal für Moderationsprotokolle fest.")
    @app_commands.default_permissions(manage_guild=True)
    async def log_set(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await self._save_setting(interaction.guild_id, "log_channel_id", channel.id)
        await interaction.response.send_message(f"📜 Log-Channel gesetzt: {channel.mention}", ephemeral=True)

    async def _save_setting(self, guild_id: int, key: str, value: int | None):
        await self.bot.db.execute(f"INSERT INTO settings(guild_id,{key}) VALUES(?,?) ON CONFLICT(guild_id) DO UPDATE SET {key}=excluded.{key}", (guild_id, value))
        await self.bot.db.commit()

    async def _get_log_channel(self, guild: discord.Guild):
        async with self.bot.db.execute("SELECT log_channel_id FROM settings WHERE guild_id=?", (guild.id,)) as cur:
            row = await cur.fetchone()
        if not row or not row[0]:
            return None
        return guild.get_channel(row[0])

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        ch = await self._get_log_channel(message.guild)
        if ch:
            await ch.send(f"🗑️ Nachricht von **{message.author}** gelöscht in {message.channel.mention}: {message.content[:400]}")

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or not before.guild:
            return
        if before.content == after.content:
            return
        ch = await self._get_log_channel(before.guild)
        if ch:
            await ch.send(f"✏️ Nachricht bearbeitet von **{before.author}** in {before.channel.mention}\nVorher: {before.content[:300]}\nNachher: {after.content[:300]}")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        ch = await self._get_log_channel(member.guild)
        if ch:
            await ch.send(f"➕ Mitglied beigetreten: **{member}**")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        ch = await self._get_log_channel(member.guild)
        if ch:
            await ch.send(f"➖ Mitglied verlassen: **{member}**")

async def setup(bot):
    await bot.add_cog(LoggingCog(bot))
