from __future__ import annotations

from typing import Iterable, Sequence

import discord

PRIMARY_COLOUR = discord.Colour.from_str("#2563eb")
SECONDARY_COLOUR = discord.Colour.from_str("#111827")

FOOTER_TEXT = "Manager Bot • Roblox Roleplay Leitstelle"


def brand_embed(
    title: str,
    description: str | None = None,
    *,
    colour: discord.Colour | None = None,
    icon: str | None = None,
) -> discord.Embed:
    """Create a consistently styled embed for bot messages."""

    heading = f"{icon} {title}" if icon else title
    embed = discord.Embed(title=heading, description=description, colour=colour or PRIMARY_COLOUR)
    embed.set_footer(text=FOOTER_TEXT)
    return embed


def add_info_fields(embed: discord.Embed, fields: Iterable[tuple[str, str | None]]) -> discord.Embed:
    """Append non-empty fields to an embed."""

    for name, value in fields:
        if value:
            embed.add_field(name=name, value=value, inline=False)
    return embed


def bullet_list(items: Iterable[str], *, bullet: str = "•") -> str:
    """Return a formatted bullet list for embed content."""

    lines = [f"{bullet} {item}" for item in items if item]
    return "\n".join(lines) if lines else "–"


def inline_stats(values: Sequence[tuple[str, str | None]]) -> str:
    """Format key/value stats for a compact embed field."""

    parts = [f"**{key}:** {value}" for key, value in values if value]
    return " · ".join(parts) if parts else "–"


def clone_embed(embed: discord.Embed) -> discord.Embed:
    """Return a detached clone that can be mutated safely."""

    return discord.Embed.from_dict(embed.to_dict())
