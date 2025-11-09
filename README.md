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
- 👋 **Willkommensflow**: Einbettungen für Join/Leave mit individuellen Textvorlagen.
- 🎛️ **Rollen-Selfservice**: Button-Panel zum Holen/Entfernen einer Rolle.
- 🎟️ **Ticket-System**: Channel-Erstellung per Button, inkl. Kategorie- und Rechteverwaltung.
- ⏰ **Reminder**: Persistente Erinnerungen mit automatischem Hintergrund-Task.
- 📝 **Moderations-Logs**: Nachrichten-Löschungen/-Bearbeitungen sowie Join/Leave Tracking.
- 🗳️ **Polls**: Button-basierte Abstimmungen mit Live-Zähler.
- 🚨 **Leitstelle & Einsätze**: Szenario-Generator, Statusboard, Lageberichte für RP.
- 🛠️ **Hilfsbefehle**: Ping, Serverinfo, Userinfo.

## Voraussetzungen
- Python 3.11 oder höher
- Ein Discord-Application Bot mit aktivierten Privileged Gateway Intents (Mitglieds-Intents erforderlich)
- SQLite (wird von Python mitgeliefert)
- Optional: `python-dotenv` zum lokalen Laden der `.env`

Die benötigten Python-Pakete sind in `requirements.txt` gelistet (u. a. `discord.py`, `aiosqlite`, `python-dotenv`).

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

Beim Join/Leave sendet der Bot ein Embed mit Avatar und Text in den hinterlegten Kanal.

### Rollenpanel
_Datei: [`cogs/roles.py`](cogs/roles.py)_

- `/role-panel <Rolle> [channel] [title]` erstellt einen Button. Nutzer können die Rolle selbst hinzufügen oder entfernen. Der Button funktioniert serverweit (persistent View).

### Ticketsystem
_Datei: [`cogs/tickets.py`](cogs/tickets.py)_

- `/ticket-setup [channel] [category]` postet ein Panel mit Button zum Ticket eröffnen.
- Tickets werden als Textkanal (optional in der hinterlegten Kategorie) mit passenden Overwrites erstellt.
- Innerhalb des Tickets ermöglicht ein zweiter Button das Schließen und Löschen.

### Reminder
_Datei: [`cogs/reminders.py`](cogs/reminders.py)_

- `/remind <Dauer> <Text>` akzeptiert Format `XdYhZmWs` (z. B. `1h30m`).
- Ein Hintergrund-Task (`tasks.loop`) prüft alle 10 Sekunden fällige Einträge und erinnert den Nutzer im ursprünglichen Kanal.

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

| Befehl                        | Beschreibung |
|-------------------------------|--------------|
| `/einsatz [stadtteil]`        | Zufälliges Einsatzszenario (Konfiguration via `data/scenarios.json`). |
| `/leitstelle status-set`      | Eigenen Status inkl. optionaler Notiz setzen (Auswahl aus Status 1–6). |
| `/leitstelle status-clear`    | Eigenen Status löschen. |
| `/leitstelle statusboard`     | Übersicht aller Statusmeldungen im Server, sortiert nach Aktualität. |
| `/leitstelle lagebericht`     | Aggregierter Lagebericht basierend auf den Statusen. |

### Hilfsbefehle
_Datei: [`cogs/utils.py`](cogs/utils.py)_

| Befehl        | Beschreibung                              |
|---------------|--------------------------------------------|
| `/ping`       | Aktuelle Latenz in Millisekunden.          |
| `/server`     | Allgemeine Serverinfos (Mitglieder, Alter).|
| `/userinfo`   | Embed mit ID, Join-Datum und Avatar.       |

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
