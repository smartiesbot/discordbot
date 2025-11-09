from __future__ import annotations

import json
import logging
import random
import time
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

STATUS_CHOICES = [
    ("Status 1 – Einsatzbereit", "Status 1 – Einsatzbereit"),
    ("Status 2 – Auf Anfahrt", "Status 2 – Auf Anfahrt"),
    ("Status 3 – Am Einsatzort", "Status 3 – Am Einsatzort"),
    ("Status 4 – Einsatz abgearbeitet", "Status 4 – Einsatz abgearbeitet"),
    ("Status 5 – Sprechwunsch", "Status 5 – Sprechwunsch"),
    ("Status 6 – Außer Dienst", "Status 6 – Außer Dienst"),
]

DEFAULT_SCENARIOS = [
    {
        "title": "Wohnungsbrand in Altona",
        "district": "Altona",
        "situation": "Dichter Rauch aus einem Mehrfamilienhaus, mehrere Anrufer melden eingeschlossene Personen.",
        "units": ["HLF", "DLK", "RTW", "ELW"],
        "extra": "Nachbarn berichten von knallenden Geräuschen aus dem Hinterhof.",
    },
    {
        "title": "VU mit eingeklemmter Person",
        "district": "Wilhelmsburg",
        "situation": "PKW kollidiert mit LKW an einer Kreuzung, Fahrer eingeklemmt.",
        "units": ["HLF", "RW", "NEF", "RTW"],
        "extra": "Kraftstoff läuft aus, Polizei sperrt die Zufahrt.",
    },
    {
        "title": "Großtierrettung im Hafen",
        "district": "HafenCity",
        "situation": "Ein Pferd ist in eine Laderampe gestürzt und steckt bis zum Bauch fest.",
        "units": ["Rüstwagen", "Tierarzt", "RTW"],
        "extra": "Besitzer meldet starke Unruhe bei dem Tier, Umfeld ist rutschig.",
    },
    {
        "title": "Massenanfall von Verletzten",
        "district": "St. Pauli",
        "situation": "Gedränge in einem Club löst Panik aus, dutzende Personen klagen über Atemnot.",
        "units": ["ELW", "GW-San", "RTW", "KTW", "Polizei"],
        "extra": "Die Leitstelle bittet um Aufbau eines Behandlungsplatzes.",
    },
    {
        "title": "Sturmflut an den Landungsbrücken",
        "district": "Landungsbrücken",
        "situation": "Steigende Pegel überspülen die Promenade, Passanten werden eingeschlossen.",
        "units": ["Boot", "DLRG", "Wasserrettung", "RTW"],
        "extra": "Starker Wind erschwert die Kommunikation, Medien sind vor Ort.",
    },
]


class Operations(commands.Cog):
    """Roleplay Werkzeuge für Notruf Hamburg."""

    leitstelle = app_commands.Group(name="leitstelle", description="Leitstellen-Tools für deine Schichten.")

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._scenarios = self._load_scenarios()

    def _load_scenarios(self) -> list[dict[str, object]]:
        path = Path("data/scenarios.json")
        if path.exists():
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                logging.warning("Failed to decode scenarios.json, falling back to defaults.")
            else:
                if isinstance(payload, list):
                    return [item for item in payload if isinstance(item, dict)] or DEFAULT_SCENARIOS
        return DEFAULT_SCENARIOS

    @app_commands.command(name="einsatz", description="Erstelle ein zufälliges Einsatzszenario für Notruf Hamburg.")
    @app_commands.describe(stadtteil="Optionaler Stadtteil für das Szenario")
    async def einsatz(self, interaction: discord.Interaction, stadtteil: str | None = None) -> None:
        scenario = random.choice(self._scenarios)
        district = stadtteil or str(scenario.get("district", "Hamburg"))
        embed = discord.Embed(
            title=f"{scenario.get('title', 'Einsatz')} ({district})",
            description=scenario.get("situation", "Ein neuer Einsatz wartet auf euch."),
            colour=discord.Colour.red(),
        )
        units = scenario.get("units")
        if isinstance(units, list) and units:
            embed.add_field(name="Alarmierung", value=", ".join(str(unit) for unit in units), inline=False)
        extra = scenario.get("extra")
        if isinstance(extra, str) and extra:
            embed.add_field(name="Lagehinweis", value=extra, inline=False)
        embed.set_footer(text="Bleibt professionell und viel Erfolg im Einsatz!")
        await interaction.response.send_message(embed=embed)

    @leitstelle.command(name="status-set", description="Aktualisiere deinen Status auf der Leitstelle.")
    @app_commands.describe(status="Wähle deinen Funkstatus", note="Optional: Rufname, Fahrzeug oder Zusatzinfo")
    @app_commands.choices(status=[app_commands.Choice(name=name, value=value) for name, value in STATUS_CHOICES])
    async def status_set(
        self,
        interaction: discord.Interaction,
        status: app_commands.Choice[str],
        note: str | None = None,
    ) -> None:
        assert interaction.guild is not None
        status_value = status.value
        timestamp = int(time.time())
        await self.bot.db.execute(
            """
            INSERT INTO unit_status(guild_id, user_id, status, note, updated_ts)
            VALUES(?,?,?,?,?)
            ON CONFLICT(guild_id, user_id) DO UPDATE SET
                status=excluded.status,
                note=excluded.note,
                updated_ts=excluded.updated_ts
            """,
            (interaction.guild.id, interaction.user.id, status_value, note, timestamp),
        )
        await self.bot.db.commit()
        response = f"📟 {interaction.user.mention} ist jetzt **{status_value}**."
        if note:
            response += f" (`{note}`)"
        await interaction.response.send_message(response)

    @leitstelle.command(name="status-clear", description="Setze deinen Status zurück.")
    async def status_clear(self, interaction: discord.Interaction) -> None:
        assert interaction.guild is not None
        await self.bot.db.execute(
            "DELETE FROM unit_status WHERE guild_id=? AND user_id=?",
            (interaction.guild.id, interaction.user.id),
        )
        await self.bot.db.commit()
        await interaction.response.send_message("✅ Dein Leitstellenstatus wurde gelöscht.", ephemeral=True)

    @leitstelle.command(name="statusboard", description="Zeige die aktuellen Statusmeldungen aller Einheiten an.")
    async def status_board(self, interaction: discord.Interaction) -> None:
        assert interaction.guild is not None
        async with self.bot.db.execute(
            "SELECT user_id, status, note, updated_ts FROM unit_status WHERE guild_id=? ORDER BY updated_ts DESC",
            (interaction.guild.id,),
        ) as cursor:
            rows = await cursor.fetchall()
        if not rows:
            await interaction.response.send_message("ℹ️ Noch keine Statusmeldungen vorhanden.", ephemeral=True)
            return
        embed = discord.Embed(
            title="Statusboard Notruf Hamburg",
            description="Live-Überblick deiner Einsatzkräfte",
            colour=discord.Colour.blue(),
        )
        for user_id, status_value, note, updated_ts in rows[:15]:
            member = interaction.guild.get_member(user_id)
            name = member.display_name if member else f"ID {user_id}"
            timestamp = f"<t:{int(updated_ts)}:R>" if updated_ts else "unbekannt"
            line = f"{status_value} · {timestamp}"
            if note:
                line += f"\n`{note}`"
            embed.add_field(name=name, value=line, inline=False)
        await interaction.response.send_message(embed=embed)

    @leitstelle.command(name="lagebericht", description="Erstelle einen Lagebericht aus allen Statusmeldungen.")
    async def lagebericht(self, interaction: discord.Interaction) -> None:
        assert interaction.guild is not None
        async with self.bot.db.execute(
            "SELECT status FROM unit_status WHERE guild_id=?",
            (interaction.guild.id,),
        ) as cursor:
            rows = await cursor.fetchall()
        if not rows:
            await interaction.response.send_message("ℹ️ Keine Statusmeldungen für einen Lagebericht vorhanden.", ephemeral=True)
            return
        totals: dict[str, int] = {}
        for (status_value,) in rows:
            totals[status_value] = totals.get(status_value, 0) + 1
        lines = [f"**{status}**: {count} Einheiten" for status, count in totals.items()]
        embed = discord.Embed(
            title="Lagebericht Notruf Hamburg",
            description="\n".join(lines),
            colour=discord.Colour.dark_gold(),
        )
        embed.set_footer(text="Halte deine Lage aktuell, damit die Leitstelle reagieren kann.")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Operations(bot))
