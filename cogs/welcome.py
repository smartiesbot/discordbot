
from __future__ import annotations

import discord
from discord.ext import commands
from discord import app_commands

from .ui_helpers import add_info_fields, brand_embed, bullet_list

DEFAULT_WELCOME = "👋 Willkommen {member}! Starte einsatzbereit in Notruf Hamburg."
DEFAULT_FAREWELL = "🚨 {name} verlässt den Funk. Wir sehen uns beim nächsten Einsatz!"

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="welcome-set", description="Set the welcome channel.")
    @app_commands.describe(channel="Select the channel for welcomes")
    @app_commands.default_permissions(manage_guild=True)
    async def welcome_set(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await self._save_setting(interaction.guild_id, "welcome_channel_id", channel.id)
        await interaction.response.send_message(f"👋 Welcome-Channel gesetzt: {channel.mention}", ephemeral=True)

    async def _save_setting(self, guild_id: int, key: str, value):
        await self.bot.db.execute(
            f"INSERT INTO settings(guild_id,{key}) VALUES(?,?) ON CONFLICT(guild_id) DO UPDATE SET {key}=excluded.{key}",
            (guild_id, value),
        )
        await self.bot.db.commit()

    @app_commands.command(name="farewell-set", description="Set the farewell channel.")
    @app_commands.describe(channel="Select the channel for farewells")
    @app_commands.default_permissions(manage_guild=True)
    async def farewell_set(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await self._save_setting(interaction.guild_id, "farewell_channel_id", channel.id)
        await interaction.response.send_message(f"👋 Farewell-Channel gesetzt: {channel.mention}", ephemeral=True)

    @app_commands.command(name="welcome-message", description="Set a custom welcome message.")
    @app_commands.describe(message="Use {member}, {name} oder {guild} als Platzhalter")
    @app_commands.default_permissions(manage_guild=True)
    async def welcome_message(self, interaction: discord.Interaction, message: str):
        await self._save_setting(interaction.guild_id, "welcome_message", message)
        await interaction.response.send_message("✅ Willkommensnachricht aktualisiert.", ephemeral=True)

    @app_commands.command(name="farewell-message", description="Set a custom farewell message.")
    @app_commands.describe(message="Use {member}, {name} oder {guild} als Platzhalter")
    @app_commands.default_permissions(manage_guild=True)
    async def farewell_message(self, interaction: discord.Interaction, message: str):
        await self._save_setting(interaction.guild_id, "farewell_message", message)
        await interaction.response.send_message("✅ Abschiedsnachricht aktualisiert.", ephemeral=True)

    def _render_template(self, template: str | None, member: discord.Member, *, fallback: str) -> str:
        base = template or fallback
        return (
            base.replace("{member}", member.mention)
            .replace("{name}", member.display_name)
            .replace("{guild}", member.guild.name)
        )

    async def _send_embed(
        self,
        channel_id: int | None,
        member: discord.Member,
        *,
        template: str | None,
        fallback: str,
        title: str,
        icon: str,
        colour: discord.Colour,
    ) -> None:
        if not channel_id:
            return
        channel = member.guild.get_channel(channel_id)
        if not isinstance(channel, discord.TextChannel):
            return
        description = self._render_template(template, member, fallback=fallback)
        embed = brand_embed(title, description=description, colour=colour, icon=icon)
        embed.set_thumbnail(url=member.display_avatar.url)
        member_count = member.guild.member_count
        add_info_fields(
            embed,
            [
                (
                    "Schnellstart",
                    bullet_list(
                        [
                            "Hol dir ein Einsatzfahrzeug im Spawn und melde dich bei der Leitstelle.",
                            "Checke dein Funkgerät mit `/leitstelle status-set`.",
                            "Lies die Einsatzordnung im Info-Kanal, bevor du loslegst.",
                        ]
                    ),
                ),
                (
                    "Crew", f"Wir zählen jetzt **{member_count}** Einsatzkräfte in {member.guild.name}!",
                ),
            ],
        )
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        async with self.bot.db.execute(
            "SELECT welcome_channel_id, welcome_message FROM settings WHERE guild_id=?",
            (member.guild.id,),
        ) as cur:
            row = await cur.fetchone()
        if not row:
            return
        channel_id, template = row
        await self._send_embed(
            channel_id,
            member,
            template=template,
            fallback=DEFAULT_WELCOME,
            title="Willkommen an Bord!",
            icon="🎉",
            colour=discord.Colour.green(),
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        async with self.bot.db.execute(
            "SELECT farewell_channel_id, farewell_message FROM settings WHERE guild_id=?",
            (member.guild.id,),
        ) as cur:
            row = await cur.fetchone()
        if not row:
            return
        channel_id, template = row
        await self._send_embed(
            channel_id,
            member,
            template=template,
            fallback=DEFAULT_FAREWELL,
            title="Bis zum nächsten Einsatz!",
            icon="👋",
            colour=discord.Colour.orange(),
        )

async def setup(bot):
    await bot.add_cog(Welcome(bot))
