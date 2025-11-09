
import time
import discord
from discord import app_commands
from discord.ext import commands

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start = time.time()

    @app_commands.command(name="ping", description="Show bot latency.")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Pong! {round(self.bot.latency * 1000)}ms", ephemeral=True)

    @app_commands.command(name="server", description="Show server info.")
    async def server(self, interaction: discord.Interaction):
        g = interaction.guild
        if not g:
            return await interaction.response.send_message("Run in a server.", ephemeral=True)
        embed = discord.Embed(title=f"{g.name}", description="Server information")
        embed.add_field(name="Members", value=str(g.member_count))
        embed.add_field(name="Created", value=discord.utils.format_dt(g.created_at, style='R'))
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Show info about a user.")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member | None = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"{member.display_name}")
        embed.add_field(name="ID", value=str(member.id))
        joined = discord.utils.format_dt(member.joined_at, 'R') if getattr(member, 'joined_at', None) else "n/a"
        embed.add_field(name="Joined", value=joined)
        embed.set_thumbnail(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Utils(bot))
