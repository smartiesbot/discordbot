from __future__ import annotations

import json
import logging
import random
import time
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable

import discord
from discord import app_commands
from discord.ext import commands

from .ui_helpers import add_info_fields, brand_embed, bullet_list, clone_embed, inline_stats

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

UNIT_HINTS: Dict[str, str] = {
    "HLF": "Erstangriff & technische Rettung",
    "DLK": "Rettung aus Höhen & Lüften",
    "RTW": "Patientenversorgung & Transport",
    "ELW": "Führung & Kommunikation",
    "RW": "Technische Rettung schwer",
    "NEF": "Notarzt für kritische Patienten",
    "GW-SAN": "Behandlungsplatz & Material",
    "KTW": "Transport Unterstützung",
    "POLIZEI": "Absperrung & Lageerkundung",
    "BOOT": "Wasserrettung & Evakuierung",
    "DLRG": "Spezialisierte Wasserrettung",
    "WASSERRETTUNG": "Unterstützung auf dem Wasser",
    "TIERARZT": "Tiermedizinische Betreuung",
    "RÜSTWAGEN": "Schwere Bergung & Hebekissen",
}

LOADOUTS = {
    "hlf": {
        "title": "HLF – Feuerwehr",
        "role": "Brandbekämpfung & technische Rettung",
        "crew": ["Maschinist", "Gruppenführer", "Angriffs- & Wassertrupp"],
        "equipment": [
            "Atemschutzgeräte (2x) & Wärmebildkamera",
            "Schnellangriff + Hydrantenset",
            "Halligan Tool, Kettensäge, Rettungsschere",
        ],
        "tactics": [
            "Trupp 1 erkundet und setzt erste Lagemeldung ab.",
            "Maschinist stellt Wasserversorgung & Strom.",
            "Gruppenführer koordiniert mit `/leitstelle statusboard`.",
        ],
    },
    "rd": {
        "title": "Rettungsdienst – RTW",
        "role": "Akutversorgung & Transport",
        "crew": ["NotSan", "RettSan"],
        "equipment": [
            "Monitor/Defi & Beatmungsgerät",
            "Notfallrucksack Erwachsene & Kinder",
            "Schaufeltrage + Vakuummatratze",
        ],
        "tactics": [
            "ABCDE-Check durchführen, Übergabe per Funk.",
            "Schlaganfall-/Trauma-Screen dokumentieren.",
            "Transportziel vor Abfahrt mit Leitstelle abstimmen.",
        ],
    },
    "pol": {
        "title": "Polizei – Funkstreife",
        "role": "Absicherung & Lagekontrolle",
        "crew": ["1. Streifenbeamter", "2. Streifenbeamter"],
        "equipment": [
            "Absperrmaterial & Blaulichtbaken",
            "Tablet für Einsatzprotokoll",
            "Handfesseln & Dienstmittel",
        ],
        "tactics": [
            "Absperrkreis und Verkehrsführung einrichten.",
            "Zeugenaufnahme & Dokumentation im Einsatzlog.",
            "Bei Großlagen Stab informieren (/leitstelle briefing).",
        ],
    },
    "thw": {
        "title": "THW – Rüstzug",
        "role": "Logistik & Spezialtechnik",
        "crew": ["Zugführer", "Truppführer", "Spezialisten"],
        "equipment": [
            "Hebekissen & Rettungszylinder",
            "Stromerzeuger & Lichtmast",
            "Abstützsysteme & Pumpen",
        ],
        "tactics": [
            "Erkundung gemeinsam mit Einsatzleitung.",
            "Aufgaben priorisieren und Kräfte anfordern.",
            "Arbeitsstellen absichern & dokumentieren.",
        ],
    },
}

SOP_GUIDES = {
    "code1": {
        "title": "Code 1 – Routinefahrt",
        "description": "Keine Sonderrechte, regulärer Einsatz mit geringer Priorität.",
        "steps": [
            "Status 1 bis Abfahrt, danach Status 2 ohne Sonderrechte.",
            "Nach 5 Minuten Lage-Update an die Leitstelle senden.",
            "Dokumentation im Einsatzlog zeitnah ergänzen.",
        ],
        "comms": [
            "Standard-Funkverfahren, keine Eile.",
            "Rückfahrt nach Abschluss mit Status 4 melden.",
        ],
    },
    "code2": {
        "title": "Code 2 – Dringlich",
        "description": "Sonderrechte auf Anfahrt, erhöhte Aufmerksamkeit.",
        "steps": [
            "Zügige Ausrückzeit, Blaulicht & Horn nach Lagebild.",
            "Vor Eintreffen Absprache, wer erste Lage übernimmt.",
            "Patienten- oder Lageprioritäten eng verfolgen.",
        ],
        "comms": [
            "Status 2 melden, Lagebild innerhalb 2 Minuten.",
            "Parallele Teams via `/leitstelle statusboard` koordinieren.",
        ],
    },
    "code3": {
        "title": "Code 3 – Lebensgefahr",
        "description": "Sofortiges Handeln, höchste Priorität.",
        "steps": [
            "Sondersignal auf gesamter Anfahrt.",
            "Vor Ort sofortige Rückmeldung & Nachalarmierung prüfen.",
            "Ressourcenkoordination mit Einsatzleitung absichern.",
        ],
        "comms": [
            "Rückmeldungen alle 90 Sekunden.",
            "Parallelkanal für kritische Infos offen halten.",
        ],
    },
    "mci": {
        "title": "Massenanfall von Verletzten",
        "description": "Großlage mit vielen Betroffenen – strukturierte Triage.",
        "steps": [
            "Sichtung nach PRIOR-Stufen und Führung etablieren.",
            "Behandlungsplatz & Bereitstellungsraum definieren.",
            "Logistik, Nachschub und Rücktransport koordinieren.",
        ],
        "comms": [
            "ELW setzt Lagemeldungen via `/leitstelle lagebericht` ab.",
            "Ressourcenbedarf frühzeitig an die Stabsstelle geben.",
        ],
    },
}


class DeploymentView(discord.ui.View):
    STAGE_ORDER = [
        ("ready", ("🟢", "Einsatzbereit")),
        ("enroute", ("🟡", "Auf Anfahrt")),
        ("onscene", ("🔴", "Am Einsatzort")),
        ("clear", ("✅", "Wieder frei")),
    ]

    def __init__(self, base_embed: discord.Embed) -> None:
        super().__init__(timeout=None)
        self.base_embed = clone_embed(base_embed)
        self.assignments: dict[int, tuple[str, int]] = {}

    def _build_embed(self) -> discord.Embed:
        embed = clone_embed(self.base_embed)
        if self.assignments:
            summary_lines = []
            for key, (emoji, label) in self.STAGE_ORDER:
                count = sum(1 for stage, _ in self.assignments.values() if stage == key)
                if count:
                    summary_lines.append(f"{emoji} {label}: **{count}**")
            if summary_lines:
                embed.add_field(name="Live-Status", value="\n".join(summary_lines), inline=False)
        else:
            embed.add_field(name="Live-Status", value="Noch keine Rückmeldungen – melde dich über die Buttons!", inline=False)

        for key, (emoji, label) in self.STAGE_ORDER:
            lines = [
                f"{emoji} <@{uid}> · <t:{ts}:R>"
                for uid, (stage, ts) in self.assignments.items()
                if stage == key
            ]
            if lines:
                embed.add_field(name=label, value="\n".join(lines), inline=False)

        embed.timestamp = discord.utils.utcnow()
        return embed

    def initial_embed(self) -> discord.Embed:
        return self._build_embed()

    async def _mark(self, interaction: discord.Interaction, stage: str, ack: str) -> None:
        self.assignments[interaction.user.id] = (stage, int(time.time()))
        embed = self._build_embed()
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send(ack, ephemeral=True)

    @discord.ui.button(label="Einsatzbereit", style=discord.ButtonStyle.success, emoji="🟢")
    async def ready(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self._mark(interaction, "ready", "Du bist als einsatzbereit eingetragen.")

    @discord.ui.button(label="Auf Anfahrt", style=discord.ButtonStyle.primary, emoji="🟡")
    async def enroute(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self._mark(interaction, "enroute", "Anfahrt vermerkt – sichere deine Anfahrt!")

    @discord.ui.button(label="Am Einsatzort", style=discord.ButtonStyle.danger, emoji="🔴")
    async def onscene(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self._mark(interaction, "onscene", "Lagemeldung bitte direkt an die Leitstelle.")

    @discord.ui.button(label="Wieder frei", style=discord.ButtonStyle.secondary, emoji="✅")
    async def clear(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self._mark(interaction, "clear", "Status 4 dokumentiert – gute Arbeit!")

    @discord.ui.button(label="Austragen", style=discord.ButtonStyle.secondary, emoji="✖️")
    async def remove(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        self.assignments.pop(interaction.user.id, None)
        embed = self._build_embed()
        await interaction.response.edit_message(embed=embed, view=self)
        await interaction.followup.send("Du wurdest aus dem Einsatzboard entfernt.", ephemeral=True)


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

    def _unit_listing(self, units: Iterable[str]) -> str:
        lines = []
        for unit in units:
            upper = unit.upper()
            info = UNIT_HINTS.get(upper, "Bereit für Spezialauftrag")
            lines.append(f"**{unit}** – {info}")
        return bullet_list(lines)

    def _scenario_embed(
        self,
        title: str,
        district: str,
        situation: str,
        units: Iterable[str],
        extra: str | None,
        *,
        priority: str | None,
        call_id: str,
    ) -> discord.Embed:
        embed = brand_embed(
            f"{title} – {district}",
            description=situation,
            icon="🚨",
            colour=discord.Colour.from_str("#ef4444"),
        )
        embed.add_field(
            name="Leitstellenpaket",
            value=inline_stats(
                [
                    ("Einsatz-ID", call_id),
                    ("Priorität", priority or "Standard"),
                    ("Stadtteil", district),
                ]
            ),
            inline=False,
        )
        embed.add_field(name="Alarmierung", value=self._unit_listing(units), inline=False)
        embed.add_field(
            name="Checkliste",
            value=bullet_list(
                [
                    "Absicherung und Gefahrenbereich markieren.",
                    "Lage erkunden & Nachforderung abstimmen.",
                    "Statusmeldungen via `/leitstelle status-set` aktualisieren.",
                ]
            ),
            inline=False,
        )
        if extra:
            embed.add_field(name="Lagehinweis", value=extra, inline=False)
        embed.add_field(
            name="Werkzeuge",
            value=bullet_list(
                [
                    "`/leitstelle statusboard` für Live-Übersicht",
                    "`/leitstelle lagebericht` für Einsatzberichte",
                    "Buttons unter dieser Nachricht für Live-Updates",
                ]
            ),
            inline=False,
        )
        embed.timestamp = discord.utils.utcnow()
        return embed

    @app_commands.command(name="einsatz", description="Erstelle ein einsatzbereites Leitstellen-Szenario.")
    @app_commands.describe(
        stadtteil="Optionaler Stadtteil für das Szenario",
        prioritaet="Einsatzpriorität",
        interaktiv="Füge ein Live-Board mit Buttons hinzu",
    )
    @app_commands.choices(
        prioritaet=[
            app_commands.Choice(name="Code 1 – Routine", value="Code 1"),
            app_commands.Choice(name="Code 2 – Dringlich", value="Code 2"),
            app_commands.Choice(name="Code 3 – Lebensgefahr", value="Code 3"),
            app_commands.Choice(name="MCI – Großschadenslage", value="MCI"),
        ]
    )
    async def einsatz(
        self,
        interaction: discord.Interaction,
        stadtteil: str | None = None,
        prioritaet: app_commands.Choice[str] | None = None,
        interaktiv: bool = False,
    ) -> None:
        scenario = random.choice(self._scenarios)
        district = stadtteil or str(scenario.get("district", "Hamburg"))
        call_id = f"NH-{random.randint(100, 999)}-{random.randint(100, 999)}"
        priority_value = prioritaet.value if prioritaet else None
        embed = self._scenario_embed(
            title=str(scenario.get("title", "Einsatz")),
            district=district,
            situation=str(scenario.get("situation", "Ein neuer Einsatz wartet auf euch.")),
            units=[str(u) for u in scenario.get("units", [])],
            extra=scenario.get("extra") if isinstance(scenario.get("extra"), str) else None,
            priority=priority_value,
            call_id=call_id,
        )
        if interaktiv:
            view = DeploymentView(embed)
            await interaction.response.send_message(embed=view.initial_embed(), view=view)
        else:
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
        embed = brand_embed(
            "Status aktualisiert",
            description=f"{interaction.user.mention} meldet {status_value}.",
            icon="📟",
            colour=discord.Colour.from_str("#22c55e"),
        )
        embed.add_field(name="Status", value=f"**{status_value}**", inline=True)
        embed.add_field(name="Notiz", value=note or "Keine zusätzlichen Infos", inline=True)
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed)

    @leitstelle.command(name="status-clear", description="Setze deinen Status zurück.")
    async def status_clear(self, interaction: discord.Interaction) -> None:
        assert interaction.guild is not None
        await self.bot.db.execute(
            "DELETE FROM unit_status WHERE guild_id=? AND user_id=?",
            (interaction.guild.id, interaction.user.id),
        )
        await self.bot.db.commit()
        embed = brand_embed(
            "Status gelöscht",
            description="Du bist wieder ohne aktiven Einsatzstatus.",
            icon="🧼",
            colour=discord.Colour.from_str("#94a3b8"),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

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
        summary = Counter()
        entries: list[tuple[str, str]] = []
        for user_id, status_value, note, updated_ts in rows[:20]:
            member = interaction.guild.get_member(user_id)
            name = member.display_name if member else f"ID {user_id}"
            summary[status_value] += 1
            base = f"**{status_value}** \n<t:{int(updated_ts)}:R>"
            if note:
                safe_note = discord.utils.escape_markdown(note)
                base += f"\n`{safe_note[:170]}`"
            entries.append((name, base))
        embed = brand_embed(
            "Statusboard Notruf Hamburg",
            description="Live-Überblick deiner Einsatzkräfte.",
            icon="📋",
            colour=discord.Colour.from_str("#38bdf8"),
        )
        summary_lines = [f"{count}× {status}" for status, count in summary.most_common()]
        embed.add_field(name="Übersicht", value=bullet_list(summary_lines), inline=False)
        for name, value in entries:
            embed.add_field(name=name, value=value, inline=False)
        embed.timestamp = discord.utils.utcnow()
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
        totals: Counter[str] = Counter(status for (status,) in rows)
        embed = brand_embed(
            "Lagebericht Notruf Hamburg",
            description="Zusammenfassung deiner aktuellen Kräfte.",
            icon="🗞️",
            colour=discord.Colour.from_str("#facc15"),
        )
        embed.add_field(
            name="Verteilung",
            value=bullet_list(f"{count}× {status}" for status, count in totals.most_common()),
            inline=False,
        )
        embed.add_field(
            name="Empfehlung",
            value=bullet_list(
                [
                    "Statusmeldungen aktuell halten, besonders bei Code 3 & MCI.",
                    "Überlege, ob zusätzliche Kräfte via `/leitstelle briefing` angefordert werden sollen.",
                    "Dokumentation im Ticketsystem sichern.",
                ]
            ),
            inline=False,
        )
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed)

    @leitstelle.command(name="briefing", description="Erstelle ein Schichtbriefing für die Einsatzkräfte.")
    @app_commands.describe(
        schicht="Name oder Schwerpunkt der Schicht",
        fokus="Lagefokus, z. B. Innenstadt, Großevent",
        wetter="Optionale Wetterlage",
        besonderheiten="Besondere Hinweise oder Einschränkungen",
    )
    async def briefing(
        self,
        interaction: discord.Interaction,
        schicht: str,
        fokus: str,
        wetter: str | None = None,
        besonderheiten: str | None = None,
    ) -> None:
        dispatcher = interaction.user.display_name
        embed = brand_embed(
            f"Lagebriefing – {schicht}",
            description="Verteile dieses Briefing vor Schichtbeginn.",
            icon="🧭",
            colour=discord.Colour.from_str("#10b981"),
        )
        add_info_fields(
            embed,
            [
                (
                    "Lagebild",
                    bullet_list(
                        [
                            f"Fokus: {fokus}",
                            f"Wetter: {wetter}" if wetter else None,
                            f"Hinweis: {besonderheiten}" if besonderheiten else None,
                        ]
                    ),
                ),
                (
                    "Prioritäten",
                    bullet_list(
                        [
                            "30-Minuten-Check-ins via `/leitstelle statusboard`.",
                            "Dokumentation wichtiger Calls im Ticketkanal.",
                            "Ersatzkräfte rechtzeitig bei Abmeldungen informieren.",
                        ]
                    ),
                ),
                (
                    "Tools",
                    bullet_list(
                        [
                            "`/leitstelle einsatz` für spontane Szenarien",
                            "`/leitstelle lagebericht` zur Stabslage",
                            "`/leitstelle loadout` für Crew-Briefings",
                        ]
                    ),
                ),
            ],
        )
        embed.set_footer(text=f"Disponent: {dispatcher} • {embed.footer.text}")
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed)

    @leitstelle.command(name="loadout", description="Zeige ein einsatzbereites Loadout für verschiedene Einheiten.")
    @app_commands.describe(einheit="Wähle das gewünschte Einsatzprofil")
    @app_commands.choices(
        einheit=[
            app_commands.Choice(name="HLF / Feuerwehr", value="hlf"),
            app_commands.Choice(name="Rettungsdienst / RTW", value="rd"),
            app_commands.Choice(name="Polizei / Funkstreife", value="pol"),
            app_commands.Choice(name="THW / Rüstzug", value="thw"),
        ]
    )
    async def loadout(
        self,
        interaction: discord.Interaction,
        einheit: app_commands.Choice[str],
    ) -> None:
        data = LOADOUTS[einheit.value]
        embed = brand_embed(
            f"Loadout – {data['title']}",
            description=data["role"],
            icon="🧰",
            colour=discord.Colour.from_str("#6366f1"),
        )
        add_info_fields(
            embed,
            [
                ("Crew", bullet_list(data["crew"])),
                ("Equipment", bullet_list(data["equipment"])),
                ("Taktik", bullet_list(data["tactics"])),
            ],
        )
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed)

    @leitstelle.command(name="sop", description="Abruf der Standardabläufe (SOP) für wichtige Lagen.")
    @app_commands.describe(lage="Wähle die Lage oder Priorität")
    @app_commands.choices(
        lage=[
            app_commands.Choice(name="Code 1 – Routine", value="code1"),
            app_commands.Choice(name="Code 2 – Dringlich", value="code2"),
            app_commands.Choice(name="Code 3 – Lebensgefahr", value="code3"),
            app_commands.Choice(name="MCI – Großschadenslage", value="mci"),
        ]
    )
    async def sop(
        self,
        interaction: discord.Interaction,
        lage: app_commands.Choice[str],
    ) -> None:
        guide = SOP_GUIDES[lage.value]
        embed = brand_embed(
            guide["title"],
            description=guide["description"],
            icon="📘",
            colour=discord.Colour.from_str("#3b82f6"),
        )
        embed.add_field(name="Ablauf", value=bullet_list(guide["steps"]), inline=False)
        embed.add_field(name="Kommunikation", value=bullet_list(guide["comms"]), inline=False)
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Operations(bot))
