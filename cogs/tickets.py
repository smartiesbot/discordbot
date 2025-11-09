
import discord
from discord.ext import commands
from discord import app_commands

class TicketOpenView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="🎫 Ticket eröffnen", style=discord.ButtonStyle.primary, custom_id="ticket_open_btn")
    async def open(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        async with self.bot.db.execute("SELECT tickets_category_id FROM settings WHERE guild_id=?", (guild.id,)) as cur:
            row = await cur.fetchone()
        category = guild.get_channel(row[0]) if row and row[0] else None
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        ch = await guild.create_text_channel(f"ticket-{interaction.user.name}", category=category, overwrites=overwrites)
        await ch.send(f"{interaction.user.mention} Willkommen im Ticket! Beschreibe dein Anliegen.", view=TicketCloseView())
        await interaction.response.send_message(f"Ticket eröffnet: {ch.mention}", ephemeral=True)

class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ Ticket schließen", style=discord.ButtonStyle.danger, custom_id="ticket_close_btn")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ticket wird geschlossen...", ephemeral=True)
        await interaction.channel.delete(reason=f"Closed by {interaction.user}")

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticket-setup", description="Post a ticket creation panel.")
    @app_commands.default_permissions(manage_channels=True)
    async def ticket_setup(self, interaction: discord.Interaction, channel: discord.TextChannel | None = None, category: discord.CategoryChannel | None = None):
        if channel is None:
            channel = interaction.channel
        if category:
            await self._save_setting(interaction.guild_id, "tickets_category_id", category.id)
        view = TicketOpenView(self.bot)
        msg = await channel.send("Brauchst du Hilfe? Öffne ein Ticket:", view=view)
        await interaction.response.send_message(f"🎟️ Ticket-Panel gepostet: {msg.jump_url}", ephemeral=True)

    async def _save_setting(self, guild_id: int, key: str, value: int | None):
        await self.bot.db.execute(f"INSERT INTO settings(guild_id,{key}) VALUES(?,?) ON CONFLICT(guild_id) DO UPDATE SET {key}=excluded.{key}", (guild_id, value))
        await self.bot.db.commit()

async def setup(bot):
    await bot.add_cog(Tickets(bot))
