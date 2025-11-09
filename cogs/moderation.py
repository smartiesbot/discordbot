
import discord
from discord import app_commands
from discord.ext import commands

def mod_perms():
    return app_commands.default_permissions(kick_members=True, ban_members=True, manage_messages=True)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Kick a member.")
    @mod_perms()
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str | None = None):
        await member.kick(reason=reason or f"Kicked by {interaction.user}")
        await interaction.response.send_message(f"✅ {member} wurde gekickt. Grund: {reason or '—'}", ephemeral=True)

    @app_commands.command(name="ban", description="Ban a member.")
    @mod_perms()
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str | None = None):
        await member.ban(reason=reason or f"Banned by {interaction.user}")
        await interaction.response.send_message(f"✅ {member} wurde gebannt.", ephemeral=True)

    @app_commands.command(name="timeout", description="Timeout a member (minutes).")
    @mod_perms()
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str | None = None):
        duration = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
        await member.timeout(until=duration, reason=reason or f"Timeout by {interaction.user}")
        await interaction.response.send_message(f"⏳ {member} Timeout für {minutes} Min.", ephemeral=True)

    @app_commands.command(name="purge", description="Delete N messages from this channel.")
    @mod_perms()
    async def purge(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer(ephemeral=True, thinking=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"🧹 Gelöscht: {len(deleted)} Nachrichten.", ephemeral=True)

    @app_commands.command(name="slowmode", description="Set slowmode seconds for this channel (0 to disable).")
    @mod_perms()
    async def slowmode(self, interaction: discord.Interaction, seconds: int):
        await interaction.channel.edit(slowmode_delay=seconds)
        await interaction.response.send_message(f"🐢 Slowmode: {seconds}s", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
