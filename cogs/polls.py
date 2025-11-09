
import discord
from discord.ext import commands
from discord import app_commands

class PollView(discord.ui.View):
    def __init__(self, options):
        super().__init__(timeout=None)
        self.counts = [0]*len(options)
        for idx, opt in enumerate(options):
            self.add_item(PollButton(opt, idx, self))

class PollButton(discord.ui.Button):
    def __init__(self, label, index, view):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, custom_id=f"poll_{index}")
        self.index = index
        self.pview = view
        self.voters = set()

    async def callback(self, interaction: discord.Interaction):
        uid = interaction.user.id
        if uid in self.voters:
            return await interaction.response.send_message("Du hast bereits abgestimmt.", ephemeral=True)
        self.voters.add(uid)
        self.pview.counts[self.index] += 1
        total = sum(self.pview.counts)
        results = " | ".join(f"{c}" for c in self.pview.counts)
        await interaction.response.edit_message(content=f"Aktuelle Stimmen: {results} (gesamt {total})", view=self.pview)

class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="poll", description="Create a button poll")
    @app_commands.describe(question="The poll question", options="Comma-separated options (2-5)")
    async def poll(self, interaction: discord.Interaction, question: str, options: str):
        opts = [o.strip() for o in options.split(",") if o.strip()]
        if not (2 <= len(opts) <= 5):
            return await interaction.response.send_message("Bitte 2–5 Optionen angeben, getrennt durch Komma.", ephemeral=True)
        view = PollView(opts)
        await interaction.response.send_message(f"**Umfrage:** {question}\nOptionen: {', '.join(opts)}", view=view)

async def setup(bot):
    await bot.add_cog(Polls(bot))
