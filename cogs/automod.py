
import re, pathlib
import discord
from discord.ext import commands
from discord import app_commands

BADWORDS_PATH = pathlib.Path("data/badwords.txt")

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.badwords = set()
        self.enabled = True
        self.link_block = False
        self._load()

    def _load(self):
        if BADWORDS_PATH.exists():
            self.badwords = {w.strip().lower() for w in BADWORDS_PATH.read_text(encoding="utf-8").splitlines() if w.strip()}

    @app_commands.command(name="automod", description="Steuere den AutoMod für deinen Server.")
    @app_commands.describe(aktion="Wähle die gewünschte Aktion")
    @app_commands.choices(
        aktion=[
            app_commands.Choice(name="Aktivieren", value="enable"),
            app_commands.Choice(name="Deaktivieren", value="disable"),
            app_commands.Choice(name="Link-Blocker umschalten", value="links"),
            app_commands.Choice(name="Wortliste neu laden", value="reload"),
        ]
    )
    @app_commands.default_permissions(manage_guild=True)
    async def automod(self, interaction: discord.Interaction, aktion: app_commands.Choice[str]):
        action = aktion.value
        if action == "enable":
            self.enabled = True
            await interaction.response.send_message("✅ AutoMod aktiviert.", ephemeral=True)
        elif action == "disable":
            self.enabled = False
            await interaction.response.send_message("⛔ AutoMod deaktiviert.", ephemeral=True)
        elif action == "links":
            self.link_block = not self.link_block
            await interaction.response.send_message(f"🔗 Link-Block: {'AN' if self.link_block else 'AUS'}", ephemeral=True)
        elif action == "reload":
            self._load()
            await interaction.response.send_message("🔁 Badwords neu geladen.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not self.enabled or message.author.bot or not message.guild:
            return
        content = message.content.lower()
        # bad word
        if any(bw in content for bw in self.badwords):
            try:
                await message.delete()
            except discord.Forbidden:
                return
            await message.channel.send(f"{message.author.mention} bitte auf die Wortwahl achten.", delete_after=5)
            return
        # links
        if self.link_block and re.search(r"https?://", content):
            try:
                await message.delete()
            except discord.Forbidden:
                return
            await message.channel.send(f"{message.author.mention} Links sind derzeit deaktiviert.", delete_after=5)

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
