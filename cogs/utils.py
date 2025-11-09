from __future__ import annotations

import time
from typing import Iterable

import discord
from discord import app_commands
from discord.ext import commands

from .ui_helpers import add_info_fields, brand_embed, bullet_list, inline_stats


VERIFICATION_LABELS = {
    discord.VerificationLevel.none: "Keine",
    discord.VerificationLevel.low: "Niedrig",
    discord.VerificationLevel.medium: "Mittel",
    discord.VerificationLevel.high: "Hoch",
    discord.VerificationLevel.highest: "Sehr hoch",
}


class Utils(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start = time.time()

    # region Helpers
    @staticmethod
    def _format_duration(seconds: float) -> str:
        seconds = int(seconds)
        periods = (
            ("T", 86400),
            ("Std", 3600),
            ("Min", 60),
            ("Sek", 1),
        )
        parts: list[str] = []
        for suffix, length in periods:
            value, seconds = divmod(seconds, length)
            if value:
                parts.append(f"{value} {suffix}")
        return " ".join(parts) if parts else "0 Sek"

    @staticmethod
    def _format_roles(member: discord.Member, *, limit: int = 8) -> str:
        roles: Iterable[discord.Role] = [role for role in member.roles if role.name != "@everyone"]
        if not roles:
            return "Keine Zusatzrollen"
        sorted_roles = sorted(roles, key=lambda r: r.position, reverse=True)
        display = [role.mention for role in sorted_roles[:limit]]
        if len(sorted_roles) > limit:
            display.append(f"… {len(sorted_roles) - limit} weitere")
        return " • ".join(display)

    # endregion

    @app_commands.command(name="ping", description="Zeige die Systemdiagnose des Bots.")
    async def ping(self, interaction: discord.Interaction) -> None:
        latency_ms = round(self.bot.latency * 1000)
        uptime = self._format_duration(time.time() - self.start)
        guilds = len(self.bot.guilds)
        embed = brand_embed(
            "Systemdiagnose",
            description="Leistungsübersicht des Manager Bots.",
            icon="📡",
            colour=discord.Colour.from_str("#22c55e"),
        )
        embed.add_field(name="Antwortzeit", value=f"`{latency_ms} ms`", inline=True)
        embed.add_field(name="Laufzeit", value=f"`{uptime}`", inline=True)
        embed.add_field(name="Server", value=f"`{guilds}`", inline=True)
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="server", description="Zeige Informationen zum aktuellen Server.")
    async def server(self, interaction: discord.Interaction) -> None:
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("Dieser Befehl funktioniert nur in einem Server.", ephemeral=True)
            return

        bots = humans = None
        if guild.chunked:
            bots = sum(1 for member in guild.members if member.bot)
            humans = guild.member_count - bots

        embed = brand_embed(
            guild.name,
            description="Premium-Dashboard für deinen Roblox RP-Hub.",
            icon="🏛️",
            colour=discord.Colour.from_str("#0f172a"),
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(
            name="Mitglieder",
            value=inline_stats(
                [
                    ("Gesamt", str(guild.member_count)),
                    ("Spieler", str(humans) if humans is not None else None),
                    ("Bots", str(bots) if bots is not None else None),
                ]
            ),
            inline=False,
        )
        owner = guild.owner or discord.utils.get(guild.members, id=guild.owner_id)
        owner_value = owner.mention if owner else f"<@{guild.owner_id}>"
        add_info_fields(
            embed,
            [
                ("Leitung", f"👑 {owner_value}"),
                (
                    "Struktur",
                    bullet_list(
                        [
                            f"{len(guild.text_channels)} Textkanäle",
                            f"{len(guild.voice_channels)} Sprachkanäle",
                            f"{len(guild.categories)} Kategorien",
                        ]
                    ),
                ),
                (
                    "Boost & Sicherheit",
                    inline_stats(
                        [
                            ("Boosts", str(guild.premium_subscription_count) if guild.premium_subscription_count else "0"),
                            ("Level", f"Stufe {guild.premium_tier}" if guild.premium_tier else "Basis"),
                            (
                                "Verifikation",
                                VERIFICATION_LABELS.get(guild.verification_level, "Unbekannt"),
                            ),
                        ]
                    ),
                ),
                ("Erstellt", discord.utils.format_dt(guild.created_at, style="F")),
            ],
        )
        features = guild.features
        if features:
            nice = bullet_list(feature.replace("_", " ").title() for feature in features)
            embed.add_field(name="Aktivierte Features", value=nice, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Zeige ein übersichtliches Profil eines Mitglieds.")
    async def userinfo(
        self,
        interaction: discord.Interaction,
        member: discord.Member | None = None,
    ) -> None:
        member = member or interaction.user
        embed = brand_embed(
            member.display_name,
            description=f"Individueller Dienststatus für {member.mention}.",
            icon="🪪",
            colour=member.colour if member.colour.value else discord.Colour.from_str("#1d4ed8"),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=f"`{member.id}`", inline=True)
        embed.add_field(name="Top-Rolle", value=member.top_role.mention if member.top_role else "Keine", inline=True)
        badges = member.public_flags.all() if member.public_flags is not None else []
        badge_text = " ".join(flag.name.replace("_", " ").title() for flag in badges) if badges else "Keine"
        embed.add_field(name="Badges", value=badge_text, inline=False)
        add_info_fields(
            embed,
            [
                (
                    "Zeitleiste",
                    bullet_list(
                        [
                            f"Beigetreten: {discord.utils.format_dt(member.joined_at, style='R') if member.joined_at else '–'}",
                            f"Account erstellt: {discord.utils.format_dt(member.created_at, style='R')}",
                        ]
                    ),
                ),
                ("Rollen", self._format_roles(member)),
                (
                    "Sichtbarkeit",
                    inline_stats(
                        [
                            ("Nickname", member.nick or "–"),
                            ("Status", str(member.status).title()),
                            ("Boostet", "Ja" if member.premium_since else "Nein"),
                        ]
                    ),
                ),
            ],
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utils(bot))
