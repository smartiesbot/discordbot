
import discord
from discord.ext import commands
from discord import app_commands

class RoleView(discord.ui.View):
    def __init__(self, role: discord.Role):
        super().__init__(timeout=None)
        self.role = role

    @discord.ui.button(label="Rolle holen/abgeben", style=discord.ButtonStyle.primary, custom_id="role_button")
    async def button(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        if self.role in member.roles:
            await member.remove_roles(self.role, reason="Rollen-Panel")
            await interaction.response.send_message(f"❌ Rolle entfernt: {self.role.name}", ephemeral=True)
        else:
            try:
                await member.add_roles(self.role, reason="Rollen-Panel")
                await interaction.response.send_message(f"✅ Rolle gegeben: {self.role.name}", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("Mir fehlen Rechte, um diese Rolle zu vergeben.", ephemeral=True)

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="role-panel", description="Erstelle einen Button zur Selbstvergabe einer Rolle.")
    @app_commands.default_permissions(manage_roles=True)
    async def role_panel(self, interaction: discord.Interaction, role: discord.Role, channel: discord.TextChannel | None = None, title: str = "Rolle holen / entfernen"):
        if channel is None:
            channel = interaction.channel
        msg = await channel.send(title, view=RoleView(role))
        await interaction.response.send_message(f"🎛️ Rollen-Panel erstellt: {msg.jump_url}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Roles(bot))
