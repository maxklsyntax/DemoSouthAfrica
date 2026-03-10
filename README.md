# Bottle Inspection Demo — Raspberry Pi

## Projektübersicht

Demo-System zur automatischen Qualitätskontrolle von kleinen 0,1L Glasflaschen.
Das System prüft ob ein Label auf der Flasche vorhanden ist (Kamera), misst das Gewicht (Waage) und erkennt Kontamination (Helligkeitsanalyse). Ergebnisse werden an SAP DM und SAP APM gesendet.

Läuft auf dem Raspberry Pi 4 **und** als Plan B auf einem Laptop mit Webcam.

---

## Hardware

| Komponente | Modell | Anschluss |
|---|---|---|
| Computer | Raspberry Pi 4 Model B (mind. 2GB) | — |
| Waage | KERN PCB 2000-1 (2kg / 0,1g) | USB-B → USB-A |
| Kamera | Raspberry Pi Camera Module 3 | CSI-Port |
| Beleuchtung | Ringlicht (optional) | USB |
| OS | Raspberry Pi OS (64-bit, Bookworm) | — |

**Laptop-Betrieb:** Waage wird simuliert (Mock), Webcam (eingebaut oder USB) wird automatisch erkannt.

---

## Schnellstart

### Auf dem Raspberry Pi

```bash
git clone https://github.com/maxklsyntax/DemoSouthAfrica.git
cd DemoSouthAfrica
chmod +x scripts/pi_setup.sh
sudo ./scripts/pi_setup.sh
```

Das Setup-Script installiert alles automatisch (venv, Dependencies, systemd Service, Auto-Update von GitHub jede Minute).

### Auf dem Laptop (Plan B)

```bash
git clone https://github.com/maxklsyntax/DemoSouthAfrica.git
cd DemoSouthAfrica
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

Dashboard öffnen: http://localhost:8080

---

## SAP-Zugangsdaten

```bash
cp .env.example .env
nano .env   # Zugangsdaten eintragen
```

Siehe `.env.example` für alle benötigten Variablen.

---

## Projektstruktur

```
src/
├── main.py              # Entry point: Plattform-Erkennung, Hardware-Init, Inspektions-Loop
├── platform_detect.py   # Erkennt Pi vs Laptop, setzt Feature-Flags
├── config/settings.py   # Alle Schwellwerte und Konfiguration, lädt .env
├── hardware/            # Hardware-Abstraktion (Waage, Kamera + Mocks + Webcam)
├── inspection/engine.py # Orchestriert den Inspektionszyklus
├── sap/                 # SAP DM + APM API Clients mit OAuth2
└── network/             # WiFi-Management + AP-Modus (nur Pi)

web/
├── app.py               # Flask App Factory
├── api/routes.py        # REST API für Dashboard
├── templates/           # Jinja2 Templates (Dashboard + WiFi-Config)
└── static/              # CSS + JS (Live-Vorschau, Auto-Refresh)

scripts/
├── pi_setup.sh          # Pi Ersteinrichtung (venv, systemd, Auto-Update)
├── start.sh             # Manueller Start
└── test_sap_connection.py  # SAP API Verbindungstest

docs/
└── setup-guide.md/pdf   # Detaillierte Setup-Anleitung
```

---

## Datenfluss

```
Waage (Gewicht)     → Inspection Engine → SAP DM (Data Collection)
Kamera (Label)      → Inspection Engine → SAP DM (Data Collection)
Kamera (Helligkeit) → Inspection Engine → SAP APM (Contamination Alert)
Alle Ergebnisse     → app_state         → Web Dashboard
```

---

## Inspektions-Modi

| Modus | Beschreibung |
|---|---|
| **Automatisch** | Flasche auf Waage (>50g) → Inspektion startet |
| **Manuell** | Button "Run Inspection" im Dashboard |
| **Nur Kamera** | Waage nicht angeschlossen → Label + Kontamination |
| **Nur Waage** | Kamera nicht angeschlossen → Gewichtsprüfung |

---

## WLAN-Konfiguration (Feld-Einsatz)

Wenn der Pi kein bekanntes WLAN findet, startet er automatisch einen Hotspot:

1. WLAN `BottleInspection-Setup` verbinden (Passwort: `inspect123`)
2. Browser: `http://10.42.0.1:8080/wifi`
3. WLAN auswählen + Passwort → Pi verbindet sich automatisch

---

## Auto-Update

Der Pi prüft **jede Minute** ob neue Commits auf GitHub sind.
Bei Änderungen: `git pull` → Dependencies installieren → Service neu starten.

Workflow: Code auf Laptop ändern → `git push` → Pi aktualisiert sich automatisch.

---

## Nützliche Befehle

```bash
# Service verwalten
sudo systemctl start|stop|restart|status bottle-inspection

# Logs live anschauen
sudo journalctl -u bottle-inspection -f

# Auto-Update Timer prüfen
sudo systemctl status bottle-inspection-update.timer

# Manuelles Update
cd ~/DemoSouthAfrica && git pull origin main

# SAP-Verbindung testen
source .venv/bin/activate && python scripts/test_sap_connection.py

# Waagen-Port prüfen
ls /dev/ttyUSB*

# Kamera testen (Pi)
rpicam-still -o test.jpg
```

---

## Dokumentation

- **[Setup-Anleitung (PDF)](docs/setup-guide.pdf)** — Detaillierte Schritt-für-Schritt Anleitung
- **CLAUDE.md** — Technische Referenz für Entwicklung
