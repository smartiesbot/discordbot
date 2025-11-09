
import discord
from discord.ext import commands
from discord import app_commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="welcome-set", description="Set the welcome channel.")
    @app_commands.describe(channel="Select the channel for welcomes")
    @app_commands.default_permissions(manage_guild=True)
    async def welcome_set(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await self._save_setting(interaction.guild_id, "welcome_channel_id", channel.id)
        await interaction.response.send_message(f"👋 Welcome-Channel gesetzt: {channel.mention}", ephemeral=True)

    async def _save_setting(self, guild_id: int, key: str, value: int | None):
        await self.bot.db.execute(f"INSERT INTO settings(guild_id,{key}) VALUES(?,?) ON CONFLICT(guild_id) DO UPDATE SET {key}=excluded.{key}", (guild_id, value))
        await self.bot.db.commit()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        async with self.bot.db.execute("SELECT welcome_channel_id FROM settings WHERE guild_id=?", (member.guild.id,)) as cur:
            row = await cur.fetchone()
        if not row or not row[0]:
            return
        channel = member.guild.get_channel(row[0])
        if channel:
            await channel.send(f"👋 Willkommen {member.mention}! Schau dich um und hab Spaß!")

async def setup(bot):
    await bot.add_cog(Welcome(bot))
