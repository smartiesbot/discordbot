# Discord Manager Bot

Ein funktionsreicher Discord-Manager für Rollenspiel- und Community-Server, geschrieben mit [`discord.py`](https://discordpy.readthedocs.io/en/stable/) und dem Cog-System. Der Bot kombiniert Moderationstools, Automatisierung, Einsatz- und Leitstellen-Features für "Notruf Hamburg" sowie nützliche Hilfsbefehle in einer zentralen Anwendung.

## Inhaltsverzeichnis
- [Höhepunkte](#höhepunkte)
- [UX-Prinzipien & Design-Leitfaden](#ux-prinzipien--design-leitfaden)
- [Voraussetzungen](#voraussetzungen)
  - [Systemprüfung vor dem Start](#systemprüfung-vor-dem-start)
- [Schnellstart](#schnellstart)
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
- [Architektur & Code-Überblick](#architektur--code-überblick)
- [Datenbank-Struktur](#datenbank-struktur)
- [Qualitätssicherung & Tests](#qualitätssicherung--tests)
- [Deployment & Betrieb](#deployment--betrieb)
- [Troubleshooting](#troubleshooting)

## Höhepunkte
- 🔐 **Moderation** – Slash-Befehle für Kick, Ban, Timeout, Purge und Slowmode, ergänzt durch situative Warnhinweise in den Embeds.
- 🤖 **AutoMod** – Badword-Filter, Link-Blocker, Live-Neuladen und proaktive Feedback-Meldungen für einen ruhigen Funk.
- 👋 **Willkommensflow** – Marken-Embeds mit Schnellstart-Checklisten, Server-Map und wichtigen Einstiegsschritten für neue Einsatzkräfte.
- 🎛️ **Rollen-Selfservice** – Button-Panel für Rollenverwaltung mit klaren Tooltips und Logging für Admins.
- 🎟️ **Ticket-System** – Support-Zentrale inkl. Eskalationsstufen, Bearbeitungsstatus und smarten Close-Checks.
- ⏰ **Reminder** – Persistente Erinnerungen, Verlaufstimeline und auto-aktualisierte Fälligkeiten.
- 📝 **Moderations-Logs** – Visuell strukturierte Audit-Nachrichten zu Nachrichtenänderungen, Join/Leave und Eskalationen.
- 🗳️ **Polls** – Button-basierte Abstimmungen mit Live-Zähler und automatischem Abschluss bei Zeitablauf.
- 🚨 **Leitstelle & Einsätze** – Interaktive Einsatz-Boards, SOP-Bibliothek, Loadouts, Schichtbriefings und Lageberichte.
- 🎨 **Premium UI/UX** – Einheitliches Embed-Branding, Statusbadges, dedizierte Icons und kontextsensitive Buttons.
- 🛠️ **Hilfsbefehle** – Diagnose-, Server- und User-Dashboards für schnelle Entscheidungen.

## UX-Prinzipien & Design-Leitfaden
Der Bot setzt auf konsistente, hochwertige UI/UX, inspiriert von Dispatch-Tools professioneller Leitstellen:

- **Branding aus einer Hand** – `cogs/ui_helpers.py` definiert Farben, Footer und Icon-Sprache aller Embeds, damit Nachrichten sofort als offizieller Leitstellen-Content erkannt werden.
- **Informationshierarchie** – Jede Nachricht startet mit einer klaren Überschrift, gefolgt von maximal drei Kernaussagen pro Abschnitt, um auch auf Mobilgeräten lesbar zu bleiben.
- **Kontextsensitive Aktionen** – Buttons und Dropdowns erscheinen nur, wenn Eingaben fehlen oder Folgeaktionen nötig sind. Fertige Tickets oder Einsätze blenden Aktionen automatisch aus.
- **Barrierearme Gestaltung** – Hohe Kontraste, ergänzende Emojis und Textbeschreibungen sorgen dafür, dass Informationen schnell erfassbar sind.
- **Feedback-Loops** – Jeder Slash-Command bestätigt Aktionen mit einem Status-Embed und Zeitstempel, damit Dispatch-Teams Entscheidungen nachvollziehen können.

> 💡 **Tipp:** Für eigene Brand-Farben kannst du in [`cogs/ui_helpers.py`](cogs/ui_helpers.py) `PRIMARY_COLOUR`, `SECONDARY_COLOUR` und `FOOTER_TEXT` anpassen. Nutze Tools wie [Coolors](https://coolors.co/) oder den Discord-eigenen Farbpicker, um ein harmonisches Farbschema zu definieren.

## Voraussetzungen
- Python 3.11 oder höher (sichert Kompatibilität mit `discord.py` Slash-Commands und `asyncio`-Features)
- Ein Discord-Application Bot mit aktivierten Privileged Gateway Intents (**Server Members** und **Message Content**)
- SQLite (wird von Python mitgeliefert)
- Optional: `python-dotenv` zum lokalen Laden der `.env`
- Empfehlung: Linux- oder Windows-Server mit dauerhafter Internetverbindung für Reminder & Buttons

Die benötigten Python-Pakete sind in `requirements.txt` gelistet (u. a. `discord.py`, `aiosqlite`, `python-dotenv`).

### Systemprüfung vor dem Start
| Prüfschritt | Erwartetes Ergebnis |
|-------------|---------------------|
| `python --version` | Ausgabe `Python 3.11.x` |
| Intents im Developer Portal | **Presence Intent** optional, **Server Members** & **Message Content** aktiviert |
| Bot-Rolle auf dem Server | Mindestens so hoch wie die Rollen, die verwaltet werden sollen |
| Ports / Firewall | Ausgehende Verbindungen zu Discord-Gateway offen |

## Schnellstart
1. **Repository forken oder klonen** – sichert dir eigene Anpassungen.
2. **`.env` ausfüllen** – trage Bot-Token und optionale IDs direkt ein.
3. **`python -m compileall .`** – schneller Syntax-Check, bevor der Bot live geht.
4. **`python bot.py`** – startet die Anwendung; Slash-Commands werden automatisch synchronisiert.
5. **Slash-Commands testen** – `/ping`, `/ticket-setup` und `/einsatz` dienen als Smoke-Test.

> 📌 **Deployment-Tipp:** Für produktive Instanzen empfiehlt sich `systemd`, Docker oder PM2 (über `python3`) mit automatischem Restart, damit Reminder-Loops nie pausieren.

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

Beispiel einer minimalen `.env`:

```dotenv
DISCORD_TOKEN=dein_token
GUILD_ID=optional_guild_id_für_test_sync
STATUS_CHANNEL_ID=optional_statusboard_channel
```

### Persistente Daten
Der Bot legt/erwartet folgende Dateien im Projekt an:

| Pfad                 | Zweck                                                                 |
|----------------------|-----------------------------------------------------------------------|
| `data/bot.db`        | SQLite-Datenbank für Einstellungen, Reminder und Leitstellenstatus.   |
| `data/badwords.txt`  | Wortliste (eine Zeile pro Eintrag) für den AutoMod-Filter.            |
| `data/scenarios.json`| Optional: Individuelle Einsatzszenarien. Fehlt die Datei, greifen Defaults. |

Die Datenbank wird beim ersten Start automatisch erstellt und migriert (`setup_hook` in `bot.py`). Änderungen an `data/badwords.txt` können über `/automod reload` ohne Neustart geladen werden.

> 🗂️ **Szenarien pflegen:** Nutze die Struktur `{ "name": "Wohnungsbrand", "district": "Altstadt", "priority": "Alpha" }`. Mehrere Szenarien erhöhen die Vielfalt der Einsatz-Prompts.

## Funktionsübersicht & Slash-Commands
Nach dem ersten Start synchronisiert der Bot automatisch alle Slash-Commands mit dem Discord-Server (`bot.tree.sync()` in `bot.py`). Die Befehle sind in Cogs organisiert.

### Moderation
_Datei: [`cogs/moderation.py`](cogs/moderation.py)_

| Befehl        | Beschreibung                            | Berechtigung           |
|---------------|------------------------------------------|------------------------|
| `/kick`       | Nutzer aus dem Server entfernen.         | Kick/Ban/Nachrichten verwalten |
| `/ban`        | Nutzer bannen.                           | Kick/Ban/Nachrichten verwalten |
| `/timeout`    | Timeout in Minuten setzen.               | Kick/Ban/Nachrichten verwalten |
| `/purge`      | X Nachrichten im aktuellen Kanal löschen.| Kick/Ban/Nachrichten verwalten |
| `/slowmode`   | Slowmode-Sekunden für den Kanal setzen.  | Kick/Ban/Nachrichten verwalten |

### AutoMod
_Datei: [`cogs/automod.py`](cogs/automod.py)_

- `/automod Aktivieren` schaltet den Filter global ein.
- `/automod Deaktivieren` pausiert alle Wortfilter.
- `/automod Link-Blocker umschalten` toggelt den Link-Blocker.
- `/automod Wortliste neu laden` lädt `data/badwords.txt` neu.

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

Zusatzfunktionen:

- **Interaktive Buttons** – Statuswechsel, Einsatz-Updates und Eskalationen lassen sich ohne zusätzliche Slash-Commands abwickeln.
- **Adaptive Texte** – Eingehende Notizen werden in Echtzeit ins Statusboard eingetragen und automatisch priorisiert.
- **Persistent Views** – Einsatz-Buttons bleiben nach einem Neustart erhalten; der Bot registriert sie in `setup_hook`.

> 💡 **Tipp:** Kombiniere `/einsatz … interaktiv:true` mit dem Statusboard für einen kompletten Live-Leitstellen-Workflow.

### Hilfsbefehle
_Datei: [`cogs/utils.py`](cogs/utils.py)_

| Befehl        | Beschreibung                              |
|---------------|--------------------------------------------|
| `/ping`       | Systemdiagnose mit Latenz, Uptime und Server-Anzahl.
| `/server`     | Dashboard mit Mitgliederaufteilung, Boost-Level, Struktur und Sicherheitsstufe.
| `/userinfo`   | Profilkarte inkl. Badges, Rollen, Zeitlinie und Boost-Status.

## Architektur & Code-Überblick
- **`bot.py`** – Einstiegspunkt, lädt Cogs, setzt Logging und kümmert sich um die Synchronisierung der Slash-Commands.
- **`cogs/ui_helpers.py`** – Enthält Brand-Helfer für Embeds, Listen und Statistikfelder. Änderungen hier wirken sich global auf die UI aus.
- **`cogs/operations.py`** – Leitstellenlogik inkl. Statusverwaltung, interaktiver Views und Einsatzgenerator.
- **`cogs/utils.py`** – Diagnose- und Profilbefehle, nutzt Zeit- und Rollenformatter für elegante Ausgabe.
- **`cogs/tickets.py`** – Erstellt Support-Panels, verwaltet Ticket-Threads und schließt Kanäle mit Nachfassformular.
- **`cogs/reminders.py`** – Hintergrund-Task für Erinnerungen mit wiederverwendbaren Embed-Komponenten.
- **`data/`** – Persistente Assets (SQLite, Wortliste, optionale Szenarien).

> 🧭 **Navigationshilfe:** Jeder Cog folgt dem gleichen Aufbau: `setup`-Funktion für `bot.add_cog`, Slash-Commands mit `@app_commands.command` und persistenten Views, falls Buttons benötigt werden.

## Datenbank-Struktur
Die SQLite-Datenbank (`data/bot.db`) enthält folgende Tabellen:

- `settings`: Guild-spezifische Einstellungen (Welcome-/Farewell-Kanal, Log-Kanal, Ticket-Kategorie, Role-Panel-Message-ID, individuelle Texte).
- `reminders`: Persistente Reminder mit `due_ts` (Unix-Timestamp) und `done`-Flag.
- `unit_status`: Aktuelle Statusmeldungen der Leitstelle inklusive optionaler Notiz und Zeitstempel.

Die Tabellen werden bei jedem Start überprüft; fehlende Spalten (`farewell_channel_id`, `welcome_message`, `farewell_message`) werden automatisch ergänzt.

## Qualitätssicherung & Tests
- **Style & Typen** – Konsistente Typannotationen und Black-kompatibles Formatting erleichtern Reviews.
- **Syntax-Prüfung** – `python -m compileall .` deckt Tippfehler auf, bevor ein Bot-Start fehlschlägt.
- **Interaktive Tests** – Verwende einen privaten Test-Server mit denselben Rollen & Kategorien wie die Live-Umgebung, um Slash-Commands gefahrlos auszuprobieren.
- **Monitoring** – Aktiviere `discord.VoiceClient.warn_nacl = False`, falls Voice-Funktionen nicht genutzt werden, um Logspam zu vermeiden.
- **Logging** – Standard-Logging auf INFO-Level (siehe `logging.basicConfig` in `bot.py`). Bei Bedarf `DEBUG` aktivieren und mit Tools wie Sentry kombinieren.

## Deployment & Betrieb
- Der Bot benötigt Schreibrechte in den Kanälen für Willkommensnachrichten, Logs, Tickets etc.
- Für Reminder und Ticket-Buttons muss der Bot dauerhaft laufen; Tasks und Views sind persistent und verwenden `discord.ui.View(timeout=None)`.
- Slash-Command-Sync findet beim Start statt. Bei vielen Guilds empfiehlt sich das Speichern/Synchronisieren pro Guild (`bot.tree.sync(guild=...)`).
- Regelmäßige Backups von `data/bot.db` sind ratsam, insbesondere für Reminder- und Statusdaten.
- Bei Docker-Setups: Mount `./data` als Volume, damit Daten auch nach Container-Restarts verfügbar bleiben.
- Nutze Health-Checks (`docker HEALTHCHECK`, `systemd` `Restart=on-failure`), um abgestürzte Instanzen automatisch zu recovern.

## Troubleshooting
| Problem | Ursache | Lösung |
|---------|---------|--------|
| Slash-Commands fehlen | Bot hatte zum Zeitpunkt des Starts nicht die nötigen Rechte oder der Sync schlug fehl | `/sync`-Befehl in `bot.py` erneut ausführen lassen (`await bot.tree.sync()`), sicherstellen, dass `applications.commands` im OAuth2-Link aktiv ist |
| Buttons reagieren nicht mehr | Bot wurde neu gestartet und alte Views waren nicht registriert | Stelle sicher, dass `setup_hook` die Views lädt (siehe `cogs/operations.py`) und der Bot dauerhaft läuft |
| Reminder werden nicht zugestellt | Hintergrund-Task stoppt bei Exceptions | Logs auf Fehler prüfen, `data/bot.db` sichern und ggf. fehlerhafte Einträge entfernen (`done = 1` setzen) |
| AutoMod reagiert zu aggressiv | Wortliste enthält zu viele generische Begriffe | `data/badwords.txt` überarbeiten, `/automod reload` ausführen |
| Uptime im `/ping`-Embed springt zurück | Prozess wurde neu gestartet | Überwache mit Supervisor/`systemd`, um unerwartete Restarts zu erkennen |

Viel Erfolg beim Betrieb eures Discord-Manager-Bots! 🚑
