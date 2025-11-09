
import os
import logging
import aiosqlite
from dotenv import load_dotenv
import discord
from discord.ext import commands

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s: %(message)s")

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN in .env")

intents = discord.Intents.default()
intents.members = True
intents.message_content = False

class ManagerBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("!"), intents=intents)
        self.db = None  # type: aiosqlite.Connection | None

    async def setup_hook(self):
        # Database init
        self.db = await aiosqlite.connect("data/bot.db")
        await self.db.executescript(
            '''
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS settings (
                guild_id INTEGER PRIMARY KEY,
                welcome_channel_id INTEGER,
                log_channel_id INTEGER,
                tickets_category_id INTEGER,
                role_panel_message_id INTEGER,
                role_panel_channel_id INTEGER
            );
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                channel_id INTEGER,
                text TEXT,
                due_ts INTEGER,
                created_ts INTEGER,
                done INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS unit_status (
                guild_id INTEGER,
                user_id INTEGER,
                status TEXT,
                note TEXT,
                updated_ts INTEGER,
                PRIMARY KEY (guild_id, user_id)
            );
            '''
        )
        await self._ensure_column("settings", "farewell_channel_id", "INTEGER")
        await self._ensure_column("settings", "welcome_message", "TEXT")
        await self._ensure_column("settings", "farewell_message", "TEXT")
        await self.db.commit()

        # Load cogs
        await self.load_extension("cogs.utils")
        await self.load_extension("cogs.moderation")
        await self.load_extension("cogs.automod")
        await self.load_extension("cogs.welcome")
        await self.load_extension("cogs.roles")
        await self.load_extension("cogs.tickets")
        await self.load_extension("cogs.reminders")
        await self.load_extension("cogs.logging")
        await self.load_extension("cogs.polls")
        await self.load_extension("cogs.operations")

        # Sync slash commands
        await self.tree.sync()
        logging.info("Slash commands synced.")

    async def _ensure_column(self, table: str, column: str, definition: str) -> None:
        assert self.db is not None
        async with self.db.execute(f"PRAGMA table_info({table})") as cursor:
            rows = await cursor.fetchall()
        existing = {row[1] for row in rows}
        if column not in existing:
            await self.db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            await self.db.commit()

    async def close(self):
        if self.db is not None:
            await self.db.close()
            self.db = None
        await super().close()

client = ManagerBot()

@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user} (ID: {client.user.id})")
    await client.change_presence(activity=discord.Game(name="/help | Manager Bot"))

if __name__ == "__main__":
    client.run(TOKEN)
