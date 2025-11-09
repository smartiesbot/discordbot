
# Discord Manager Bot (Python, discord.py cogs)

Features:
- Moderation: /ban /kick /timeout /purge /slowmode
- AutoMod: bad-word filter (editable), link spam toggle
- Welcome/Goodbye: configurable welcome channel + DM
- Roles: create a button role panel
- Tickets: /ticket-setup and open/close via buttons
- Reminders: /remind me in 10m ... (SQLite + background task)
- Logging: message edits/deletes, member join/leave
- Polls: /poll create with buttons
- Utils: /ping, /server, /userinfo

## Setup (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
notepad .env   # paste your DISCORD_TOKEN
python bot.py
```

## Invite
- Scopes: bot, applications.commands
- Permissions: Send Messages, Manage Roles, Manage Channels, Manage Messages, Use Slash Commands

## Notes
- Database file: data/bot.db
- Bad words list: data/badwords.txt (one per line). Edit and reload with /automod reload.
