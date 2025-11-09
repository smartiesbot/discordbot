# Discord Manager Bot

Ein funktionsreicher Discord-Manager für Rollenspiel- und Community-Server, geschrieben mit [`discord.py`](https://discordpy.readthedocs.io/en/stable/) und dem Cog-System. Der Bot kombiniert Moderationstools, Automatisierung, Einsatz- und Leitstellen-Features für "Notruf Hamburg" sowie nützliche Hilfsbefehle in einer zentralen Anwendung.

## Inhaltsverzeichnis
- [Highlights](#highlights)
- [Voraussetzungen](#voraussetzungen)
- [Installation & Start](#installation--start)
- [Konfiguration](#konfiguration)
  - [Umgebungsvariablen](#umgebungsvariablen)
  - [Persistente Daten](#persistente-daten)
- [Funktionsübersicht & Slash-Commands](#funktionsübersicht--slash-commands)
  - [Moderation](#moderation)
  - [AutoMod](#automod)
  - [Willkommen & Abschied](#willkommen--abschied)
  - [Rollenpanel](#rollenpanel)
  - [Ticketsystem](#ticketsystem)
  - [Reminder](#reminder)
  - [Logging](#logging)
  - [Umfragen](#umfragen)
  - [Leitstelle & RP-Tools](#leitstelle--rp-tools)
  - [Hilfsbefehle](#hilfsbefehle)
- [Datenbank-Struktur](#datenbank-struktur)
- [Entwicklung & Tests](#entwicklung--tests)
- [Deployment-Hinweise](#deployment-hinweise)

## Highlights
- 🔐 **Moderation**: Slash-Befehle für Kick, Ban, Timeout, Purge und Slowmode.
- 🤖 **AutoMod**: Badword-Filter und optionaler Link-Blocker mit Live-Neuladen der Wortliste.
- 👋 **Willkommensflow**: Marken-Embeds mit Schnellstart-Checklisten für neue Einsatzkräfte.
- 🎛️ **Rollen-Selfservice**: Button-Panel zum Holen/Entfernen einer Rolle.
- 🎟️ **Ticket-System**: Support-Zentrale mit stylischem Panel und Checklisten im Ticket.
- ⏰ **Reminder**: Persistente Erinnerungen mit visueller Terminübersicht.
- 📝 **Moderations-Logs**: Nachrichten-Löschungen/-Bearbeitungen sowie Join/Leave Tracking.
- 🗳️ **Polls**: Button-basierte Abstimmungen mit Live-Zähler.
- 🚨 **Leitstelle & Einsätze**: Interaktive Einsatz-Boards, SOP-Bibliothek, Loadouts & Schichtbriefings.
- 🎨 **Premium UI/UX**: Einheitliches Embed-Branding, Diagnosedashboards & Live-Buttons.
- 🛠️ **Hilfsbefehle**: Diagnose-, Server- und User-Dashboards für schnelle Entscheidungen.

## Voraussetzungen
- Python 3.11 oder höher
- Ein Discord-Application Bot mit aktivierten Privileged Gateway Intents (**Server Members** und **Message Content**)
- SQLite (wird von Python mitgeliefert)
- Optional: `python-dotenv` zum lokalen Laden der `.env`

Die benötigten Python-Pakete sind in `requirements.txt` gelistet (u. a. `discord.py`, `aiosqlite`, `python-dotenv`).

### OAuth2-URL & Berechtigungen
1. Öffne im [Discord Developer Portal](https://discord.com/developers/applications) deine Anwendung und navigiere zu **OAuth2 ▸ URL Generator**.
2. Wähle unter **Scopes** mindestens:
   - `bot`
   - `applications.commands`
3. Aktiviere unter **Bot Permissions** die folgenden Häkchen (entsprechen dem internen Permissions-Integer `285466671968`):

| Kategorie              | Berechtigung                            | Warum benötigt? |
|------------------------|-----------------------------------------|-----------------|
| Allgemein              | View Channels                            | Basisrecht, automatisch gesetzt |
|                        | Send Messages                            | Bot-Antworten in Kanälen |
|                        | Embed Links                              | Embeds für Willkommens-, Log- und Info-Nachrichten |
|                        | Read Message History                     | Benötigt für `/purge` und Ticket-Antworten |
| Moderation             | Manage Messages                          | `/purge`, AutoMod-Löschungen, Reminder-Updates |
|                        | Moderate Members                         | `/timeout` benötigt dieses Recht |
|                        | Kick Members                             | Für `/kick` |
|                        | Ban Members                              | Für `/ban` |
| Kanalverwaltung        | Manage Channels                          | Ticket-System erstellt/löscht Kanäle |
| Rollenverwaltung       | Manage Roles                             | Rollenpanel vergibt/entfernt Rollen |

Optional, je nach Server-Setup:

- **Attach Files** – falls der Bot Dateien versenden soll.
- **Use External Emojis** – falls Buttons/Embeds Emojis aus anderen Servern nutzen sollen.

Den generierten Invite-Link findest du unterhalb der Permissionsliste. Teile ihn mit deinem Team, um den Bot auf den Zielserver einzuladen.

## Installation & Start
```powershell
# 1. Repository klonen
# git clone <dein-fork>
cd discordbot

# 2. Virtuelle Umgebung erstellen & aktivieren
python -m venv .venv
.\.venv\Scripts\Activate.ps1    # PowerShell (Windows)
# source .venv/bin/activate       # Bash (macOS/Linux)

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. Umgebungsdatei anlegen
cp .env.example .env
notepad .env                      # TOKEN eintragen (siehe unten)

# 5. Bot starten
python bot.py
```

Unter Linux/macOS können die Aktivierung und Editor-Schritte entsprechend angepasst werden.

## Konfiguration
### Umgebungsvariablen
| Variable        | Beschreibung                                       |
|-----------------|----------------------------------------------------|
| `DISCORD_TOKEN` | Bot-Token aus dem Discord Developer Portal. Pflicht. |

Die `.env` wird beim Start via [`python-dotenv`](https://github.com/theskumar/python-dotenv) geladen. Alternativ kann das Token direkt als Environment-Variable gesetzt werden.

### Persistente Daten
Der Bot legt/erwartet folgende Dateien im Projekt an:

| Pfad                 | Zweck                                                                 |
|----------------------|-----------------------------------------------------------------------|
| `data/bot.db`        | SQLite-Datenbank für Einstellungen, Reminder und Leitstellenstatus.   |
| `data/badwords.txt`  | Wortliste (eine Zeile pro Eintrag) für den AutoMod-Filter.            |
| `data/scenarios.json`| Optional: Individuelle Einsatzszenarien. Fehlt die Datei, greifen Defaults. |

Die Datenbank wird beim ersten Start automatisch erstellt und migriert (`setup_hook` in `bot.py`). Änderungen an `data/badwords.txt` können über `/automod reload` ohne Neustart geladen werden.

## Funktionsübersicht & Slash-Commands
Nach dem ersten Start synchronisiert der Bot automatisch alle Slash-Commands mit dem Discord-Server (`bot.tree.sync()` in `bot.py`). Die Befehle sind in Cogs organisiert.

### Moderation
_Datei: [`cogs/moderation.py`](cogs/moderation.py)_

| Befehl        | Beschreibung                            | Berechtigung           |
|---------------|------------------------------------------|------------------------|
| `/kick`       | Nutzer aus dem Server entfernen.         | Kick/Ban/Manage Messages |
| `/ban`        | Nutzer bannen.                           | Kick/Ban/Manage Messages |
| `/timeout`    | Timeout in Minuten setzen.               | Kick/Ban/Manage Messages |
| `/purge`      | X Nachrichten im aktuellen Kanal löschen.| Kick/Ban/Manage Messages |
| `/slowmode`   | Slowmode-Sekunden für den Kanal setzen.  | Kick/Ban/Manage Messages |

### AutoMod
_Datei: [`cogs/automod.py`](cogs/automod.py)_

- `/automod enable|disable` schaltet den Filter global um.
- `/automod links` toggelt den Link-Blocker.
- `/automod reload` lädt `data/badwords.txt` neu.

Der Listener `on_message` löscht Nachrichten mit gesperrten Wörtern oder Links (falls aktiviert) und weist den Autor auf die Richtlinien hin.

### Willkommen & Abschied
_Datei: [`cogs/welcome.py`](cogs/welcome.py)_

| Befehl                | Beschreibung                                                |
|-----------------------|------------------------------------------------------------|
| `/welcome-set`        | Kanal für Willkommensnachrichten speichern.                |
| `/farewell-set`       | Kanal für Abschieds-Nachrichten speichern.                  |
| `/welcome-message`    | Individuelle Vorlage mit Platzhaltern (`{member}`, `{name}`, `{guild}`). |
| `/farewell-message`   | Individuelle Abschiedsvorlage mit Platzhaltern.            |

Beim Join/Leave sendet der Bot ein gebrandetes Embed mit Avatar, Crew-Zähler und Schnellstart-Checkliste in den hinterlegten Kanal.

### Rollenpanel
_Datei: [`cogs/roles.py`](cogs/roles.py)_

- `/role-panel <Rolle> [channel] [title]` erstellt einen Button. Nutzer können die Rolle selbst hinzufügen oder entfernen. Der Button funktioniert serverweit (persistent View).

### Ticketsystem
_Datei: [`cogs/tickets.py`](cogs/tickets.py)_

- `/ticket-setup [channel] [category]` postet ein gebrandetes Support-Panel mit Live-Button.
- Ticket-Channels erhalten automatisch Checklisten-Embeds, Kategorie-Overwrites und Close-Button.
- Nutzer sehen im Panel Hinweise zu Reaktionszeit, benötigten Informationen und Anhängen.

### Reminder
_Datei: [`cogs/reminders.py`](cogs/reminders.py)_

- `/remind <Dauer> <Text>` akzeptiert Format `XdYhZmWs` (z. B. `1h30m`) und liefert ein visuelles Termin-Embed.
- Ein Hintergrund-Task (`tasks.loop`) prüft alle 10 Sekunden fällige Einträge und verschickt stilvolle Reminder-Embeds an den Kanal.

### Logging
_Datei: [`cogs/logging.py`](cogs/logging.py)_

| Befehl      | Beschreibung                                      |
|-------------|----------------------------------------------------|
| `/log-set`  | Kanal für Moderationslogs speichern.               |

Automatische Events schreiben Meldungen zu gelöschten/bearbeiteten Nachrichten und Join/Leave in den Log-Kanal.

### Umfragen
_Datei: [`cogs/polls.py`](cogs/polls.py)_

- `/poll <Frage> <Optionen>` erzeugt bis zu fünf Buttons. Jeder Nutzer kann einmal abstimmen; die Anzeige aktualisiert sich live mit den aktuellen Stimmen.

### Leitstelle & RP-Tools
_Datei: [`cogs/operations.py`](cogs/operations.py)_

| Befehl                                   | Beschreibung |
|------------------------------------------|--------------|
| `/einsatz [stadtteil] [prioritaet] [interaktiv]` | Erstellt ein gebrandetes Einsatzszenario inkl. Checkliste; `interaktiv=true` aktiviert ein Live-Board mit Buttons. |
| `/leitstelle status-set`                 | Eigenen Status inkl. optionaler Notiz setzen (Auswahl aus Status 1–6) mit stylischem Bestätigungs-Embed. |
| `/leitstelle status-clear`               | Eigenen Status löschen und per Embed bestätigen lassen. |
| `/leitstelle statusboard`                | Übersicht aller Statusmeldungen mit Zusammenfassung, Notizen und Zeitstempel. |
| `/leitstelle lagebericht`                | Aggregierter Lagebericht basierend auf Statusmeldungen inkl. Handlungsempfehlung. |
| `/leitstelle briefing`                   | Erzeugt ein Schichtbriefing mit Fokus, Prioritäten und Tool-Empfehlungen. |
| `/leitstelle loadout`                    | Zeigt Crew-, Equipment- und Taktik-Checklisten für HLF, RTW, Polizei oder THW. |
| `/leitstelle sop`                        | Liefert Standardabläufe (Code 1–3, MCI) für Funk & Einsatzkoordination. |

> 💡 **Tipp:** Kombiniere `/einsatz … interaktiv:true` mit dem Statusboard für einen kompletten Live-Leitstellen-Workflow.

### Hilfsbefehle
_Datei: [`cogs/utils.py`](cogs/utils.py)_

| Befehl        | Beschreibung                              |
|---------------|--------------------------------------------|
| `/ping`       | Systemdiagnose mit Latenz, Uptime und Server-Anzahl. |
| `/server`     | Dashboard mit Mitgliederaufteilung, Boost-Level und Struktur. |
| `/userinfo`   | Profilkarte inkl. Badges, Rollen und Zeitlinie. |

## Datenbank-Struktur
Die SQLite-Datenbank (`data/bot.db`) enthält folgende Tabellen:

- `settings`: Guild-spezifische Einstellungen (Welcome-/Farewell-Kanal, Log-Kanal, Ticket-Kategorie, Role-Panel-Message-ID, individuelle Texte).
- `reminders`: Persistente Reminder mit `due_ts` (Unix-Timestamp) und `done`-Flag.
- `unit_status`: Aktuelle Statusmeldungen der Leitstelle inklusive optionaler Notiz und Zeitstempel.

Die Tabellen werden bei jedem Start überprüft; fehlende Spalten (`farewell_channel_id`, `welcome_message`, `farewell_message`) werden automatisch ergänzt.

## Entwicklung & Tests
- **Style**: Projekt nutzt Typannotationen (Python 3.11) und `discord.py` Slash-Command-APIs.
- **Lokale Tests**: Einfache Smoke-Tests über `python bot.py` (stellt Verbindung zum Discord-Gateway her). Für automatisierte Tests können Mock-Events mit `discord.py`-Testtools eingesetzt werden.
- **Logging**: Standard-Logging auf INFO-Level (siehe `logging.basicConfig` in `bot.py`).

## Deployment-Hinweise
- Der Bot benötigt Schreibrechte in den Kanälen für Willkommensnachrichten, Logs, Tickets etc.
- Für Reminder und Ticket-Buttons muss der Bot dauerhaft laufen; Tasks und Views sind persistent und verwenden `discord.ui.View(timeout=None)`.
- Slash-Command-Sync findet beim Start statt. Bei vielen Guilds empfiehlt sich das Speichern/Synchronisieren pro Guild (`bot.tree.sync(guild=...)`).
- Regelmäßige Backups von `data/bot.db` sind ratsam, insbesondere für Reminder- und Statusdaten.

Viel Erfolg beim Betrieb eures Discord-Manager-Bots! 🚑
