
import os
import logging
import aiosqlite
from dotenv import load_dotenv
import discord
from discord import app_commands

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s: %(message)s")

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN in .env")

intents = discord.Intents.default()
intents.members = True
intents.message_content = False

class ManagerBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
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
            '''
        )
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

        # Sync slash commands
        await self.tree.sync()
        logging.info("Slash commands synced.")

client = ManagerBot()

@client.event
async def on_ready():
    logging.info(f"Logged in as {client.user} (ID: {client.user.id})")
    await client.change_presence(activity=discord.Game(name="/help | Manager Bot"))

if __name__ == "__main__":
    client.run(TOKEN)
