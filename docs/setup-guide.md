# Bottle Inspection System — Setup-Anleitung

**Version:** 0.1.0
**Stand:** 2026-03-10

---

## Inhaltsverzeichnis

1. [Benötigte Hardware](#1-benötigte-hardware)
2. [Raspberry Pi vorbereiten](#2-raspberry-pi-vorbereiten)
3. [Waage anschließen (KERN PCB 2000-1)](#3-waage-anschließen-kern-pcb-2000-1)
4. [Kamera anschließen](#4-kamera-anschließen)
5. [Software installieren](#5-software-installieren)
6. [SAP-Zugangsdaten konfigurieren (.env)](#6-sap-zugangsdaten-konfigurieren-env)
7. [System starten und testen](#7-system-starten-und-testen)
8. [WLAN-Konfiguration im Feld](#8-wlan-konfiguration-im-feld)
9. [Dashboard bedienen](#9-dashboard-bedienen)
10. [Laptop als Plan B (ohne Pi)](#10-laptop-als-plan-b-ohne-pi)
11. [Fehlerbehebung](#11-fehlerbehebung)

---

## 1. Benötigte Hardware

| Komponente | Modell / Beschreibung | Anschluss |
|---|---|---|
| Raspberry Pi | Raspberry Pi 4 (mind. 2 GB RAM) | — |
| Netzteil | USB-C, 5V / 3A (offizielles Pi-Netzteil empfohlen) | USB-C am Pi |
| microSD-Karte | Mind. 16 GB, Class 10 | SD-Slot am Pi |
| Waage | KERN PCB 2000-1 | USB (seriell) am Pi |
| Kamera | Raspberry Pi Camera Module 3 | CSI-Flachbandkabel am Pi |
| USB-Kabel | Typ A auf Typ B (Drucker-Kabel) für die Waage | — |
| Ringlicht (optional) | USB-Ringlicht für gleichmäßige Ausleuchtung | USB am Pi |

---

## 2. Raspberry Pi vorbereiten

### 2.1 Betriebssystem installieren

1. **Raspberry Pi Imager** herunterladen: https://www.raspberrypi.com/software/
2. Imager starten, Einstellungen:
   - **OS:** Raspberry Pi OS (64-bit, Bookworm)
   - **SD-Karte** auswählen
   - **Zahnrad-Icon** (Einstellungen):
     - Hostname: `bottleinspection`
     - SSH aktivieren (Passwort-Authentifizierung)
     - Benutzername: `pi`, Passwort festlegen
     - WLAN konfigurieren (optional, kann auch später über AP-Modus)
     - Locale: `Europe/Berlin`, Tastatur `de`
3. **Schreiben** klicken und warten

### 2.2 Erster Start

1. microSD in den Pi einsetzen
2. Netzteil anschließen — Pi bootet automatisch
3. Warten bis die grüne LED nicht mehr flackert (~2 Minuten)
4. Per SSH verbinden:
   ```
   ssh pi@bottleinspection.local
   ```
   Falls `.local` nicht funktioniert: IP-Adresse im Router nachschauen

### 2.3 System aktualisieren

```bash
sudo apt update && sudo apt upgrade -y
```

---

## 3. Waage anschließen (KERN PCB 2000-1)

### 3.1 Physischer Anschluss

1. Waage auf eine **ebene, stabile Fläche** stellen
2. Waage mit dem **USB-Kabel** (Typ A auf Typ B) an einen USB-Port des Pi anschließen
3. Waage **einschalten** (Taster an der Rückseite)
4. Warten bis die Anzeige `0.0 g` zeigt

### 3.2 Waage am Pi prüfen

```bash
# Prüfen ob die Waage erkannt wird
ls /dev/ttyUSB*
```

Erwartete Ausgabe: `/dev/ttyUSB0`

Falls `/dev/ttyUSB0` nicht erscheint:
- USB-Kabel prüfen (anderes Kabel testen)
- Anderen USB-Port am Pi testen
- Waage aus- und wieder einschalten

### 3.3 Kommunikation testen (optional)

```bash
# Manueller Test der seriellen Verbindung
sudo apt install -y screen
screen /dev/ttyUSB0 9600
```

In der Screen-Session `w` eingeben und Enter drücken.
Erwartete Antwort: `     0.0 g` (oder aktuelles Gewicht).
Beenden mit `Ctrl+A`, dann `K`, dann `Y`.

### 3.4 Serielle Rechte für User

```bash
sudo usermod -a -G dialout pi
```

**Wichtig:** Danach neu einloggen (oder `newgrp dialout`), damit die Berechtigung greift.

### 3.5 Einstellungen der Waage

Die Software erwartet folgende Waage-Einstellungen:

| Parameter | Wert | Konfiguriert in |
|---|---|---|
| Baudrate | 9600 | Standard bei KERN |
| Serieller Port | `/dev/ttyUSB0` | `src/config/settings.py` |
| Timeout | 2 Sekunden | `src/config/settings.py` |
| Gewichtsbereich | 150–260 g (gefüllte Flasche) | `src/config/settings.py` |
| Trigger-Gewicht | 50 g (Flasche erkannt) | `src/config/settings.py` |

---

## 4. Kamera anschließen

### 4.1 Pi Camera Module 3 (empfohlen)

1. Pi **ausschalten** (`sudo shutdown -h now`)
2. **CSI-Kabel** vorsichtig in den Kamera-Port des Pi einsetzen:
   - Blauen Clip am Pi-Board nach oben ziehen
   - Flachbandkabel einsetzen (Kontakte zeigen zur Platine)
   - Clip wieder herunterdrücken
3. Kamera am Modul genauso anschließen
4. Pi wieder einschalten

### 4.2 Kamera testen

```bash
# Testbild aufnehmen
rpicam-still -o test.jpg
```

Falls Fehlermeldung: Prüfe ob das Kabel korrekt sitzt und die Kamera im richtigen Port steckt (nicht im Display-Port).

### 4.3 Kamera-Positionierung

- Kamera **frontal auf die Flasche** ausrichten
- Abstand ca. **15–25 cm** (gesamte Flasche im Bild)
- **Ringlicht** aktivieren für gleichmäßige Beleuchtung (verbessert Label- und Kontaminationserkennung)
- Die Kamera-Vorschau im Dashboard nutzen, um die Position zu prüfen

### 4.4 USB-Webcam (Alternative)

Wenn keine Pi Camera verfügbar ist, kann eine USB-Webcam verwendet werden:

1. USB-Webcam an einen USB-Port anschließen
2. Prüfen ob erkannt:
   ```bash
   ls /dev/video*
   ```
3. Die Software erkennt USB-Webcams automatisch (OpenCV-basiert)
4. Im Dashboard kann die Kamera über das **Dropdown-Menü** ausgewählt werden

---

## 5. Software installieren

### 5.1 Repository klonen

```bash
cd /home/pi
git clone https://github.com/maxklsyntax/DemoSouthAfrica.git
cd DemoSouthAfrica
```

### 5.2 Setup-Script ausführen

Das Setup-Script richtet alles automatisch ein (venv, Dependencies, systemd Service, Auto-Update):

```bash
chmod +x scripts/pi_setup.sh
sudo ./scripts/pi_setup.sh
```

Das Script:
- Installiert System-Abhängigkeiten (python3-venv, git, etc.)
- Erstellt eine Python Virtual Environment (`.venv`)
- Installiert alle Python-Pakete aus `requirements.txt`
- Richtet den **systemd Service** ein (App startet automatisch bei Boot)
- Richtet den **Auto-Update Timer** ein (prüft jede Minute auf GitHub-Updates)

### 5.3 Prüfen ob alles läuft

```bash
# Service-Status prüfen
sudo systemctl status bottle-inspection

# Live-Logs anschauen
sudo journalctl -u bottle-inspection -f

# Auto-Update Timer prüfen
sudo systemctl status bottle-inspection-update.timer
```

---

## 6. SAP-Zugangsdaten konfigurieren (.env)

### 6.1 .env-Datei erstellen

```bash
cd /home/pi/DemoSouthAfrica
cp .env.example .env
nano .env
```

### 6.2 Werte eintragen

```env
# SAP Digital Manufacturing
SAP_DM_CLIENT_ID=<Client-ID aus SAP DM Service Key>
SAP_DM_CLIENT_SECRET=<Client-Secret aus SAP DM Service Key>
SAP_DM_TOKEN_URL=https://<subdomain>.authentication.eu10.hana.ondemand.com/oauth/token
SAP_DM_BASE_URL=https://api.<subdomain>.cfapps.eu10.hana.ondemand.com
SAP_DM_PLANT=<Plant-ID>

# SAP Asset Performance Management
SAP_APM_AUTH_MODE=apikey
SAP_APM_API_KEY=<API Key aus SAP APM>
SAP_APM_BASE_URL=https://api.<subdomain>.cfapps.eu10.hana.ondemand.com
SAP_APM_EQUIPMENT_ID=<Equipment-ID>

# Allgemein
LOG_LEVEL=INFO
WEB_PORT=8080
```

Speichern mit `Ctrl+O`, Enter, `Ctrl+X`.

### 6.3 Service neu starten

```bash
sudo systemctl restart bottle-inspection
```

### 6.4 SAP-Verbindung testen

```bash
cd /home/pi/DemoSouthAfrica
source .venv/bin/activate
python scripts/test_sap_connection.py
```

---

## 7. System starten und testen

### 7.1 Automatischer Start

Nach dem Setup startet das System automatisch:
- **Bei jedem Boot** des Pi
- **Neustart bei Absturz** (nach 5 Sekunden)
- **Code-Updates** von GitHub werden jede Minute geprüft

### 7.2 Manuell starten / stoppen

```bash
# Starten
sudo systemctl start bottle-inspection

# Stoppen
sudo systemctl stop bottle-inspection

# Neustarten
sudo systemctl restart bottle-inspection

# Logs live anschauen
sudo journalctl -u bottle-inspection -f
```

### 7.3 Dashboard öffnen

1. Browser öffnen
2. Navigieren zu: `http://<Pi-IP-Adresse>:8080`
   - oder `http://bottleinspection.local:8080`
3. Dashboard zeigt:
   - Kamera-Vorschau (Live)
   - Waage-Status und Gewicht
   - Letzte Inspektion (Ergebnis, Label, Gewicht, Kontamination)
   - SAP-Übertragungsstatus (DM + APM)
   - Netzwerk-Status

### 7.4 Funktionstest durchführen

1. **Kamera-Test:** Kamera-Vorschau im Dashboard prüfen — Bild muss live aktualisieren
2. **Waage-Test:** Flasche auf die Waage stellen — Gewicht muss im Dashboard erscheinen
3. **Inspektion manuell:** "Run Inspection" Button im Dashboard klicken
4. **Inspektion automatisch:** Flasche auf Waage stellen → System erkennt automatisch (>50g) → Inspektion wird ausgeführt
5. **SAP-Test:** Nach erfolgreicher Inspektion prüfen ob SAP DM/APM Status auf "Success" steht

---

## 8. WLAN-Konfiguration im Feld

### 8.1 Automatischer AP-Modus

Wenn der Pi beim Boot **kein bekanntes WLAN** findet, startet er automatisch einen eigenen Hotspot:

| Einstellung | Wert |
|---|---|
| SSID | `BottleInspection-Setup` |
| Passwort | `inspect123` |
| IP-Adresse | `10.42.0.1` |

### 8.2 WLAN einrichten

1. Mit Handy oder Laptop zum WLAN `BottleInspection-Setup` verbinden
2. Passwort: `inspect123`
3. Browser öffnen: `http://10.42.0.1:8080/wifi`
4. **"Scan for Networks"** klicken
5. Gewünschtes WLAN aus der Liste auswählen
6. Passwort eingeben und **"Connect"** klicken
7. Pi verbindet sich → Hotspot wird automatisch deaktiviert
8. Dashboard ist jetzt unter der neuen IP erreichbar

### 8.3 Mobiler Router / Hotspot

Bei Verwendung eines mobilen Routers (z.B. für die Demo):
1. Mobilen Router einschalten
2. WLAN-Name und Passwort des Routers notieren
3. Pi per AP-Modus (siehe oben) mit dem Router-WLAN verbinden
4. Pi merkt sich das WLAN und verbindet sich beim nächsten Boot automatisch

---

## 9. Dashboard bedienen

### 9.1 Kamera-Vorschau

- Live-Bild aktualisiert sich jede Sekunde
- **Kamera-Dropdown** (oben rechts im Kamera-Bereich): zwischen mehreren Kameras wechseln
- Dient zur Positionierung und Kontrolle

### 9.2 Inspektion auslösen

Es gibt zwei Wege:

1. **Automatisch:** Flasche auf die Waage stellen (Gewicht > 50g → Inspektion startet)
2. **Manuell:** Button **"Run Inspection"** im Dashboard klicken

### 9.3 Ergebnisse lesen

| Feld | Bedeutung |
|---|---|
| **Overall** | PASS (alles OK) oder FAIL (mind. ein Check fehlgeschlagen) |
| **Label** | Etikett erkannt (true/false) → wird an SAP DM gesendet |
| **Weight** | Gewicht in Gramm → wird an SAP DM gesendet |
| **Contamination** | Kontamination erkannt (true/false) → wird an SAP APM gesendet |

### 9.4 Standalone-Betrieb

Das System funktioniert auch wenn nur **eine** Komponente angeschlossen ist:
- **Nur Kamera:** Label- und Kontaminationsprüfung (kein Gewicht)
- **Nur Waage:** Gewichtsprüfung (kein Label/Kontamination)
- **Beides:** Vollständige Inspektion

---

## 10. Laptop als Plan B (ohne Pi)

Falls der Pi nicht verfügbar ist, kann das System auf einem Laptop laufen:

### 10.1 Voraussetzungen

- Python 3.9+
- Webcam (eingebaut oder USB)
- Git

### 10.2 Installation

```bash
git clone https://github.com/maxklsyntax/DemoSouthAfrica.git
cd DemoSouthAfrica
python3 -m venv .venv
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

### 10.3 Starten

```bash
python -m src.main
```

Dashboard öffnen: `http://localhost:8080`

### 10.4 Hinweise Laptop-Betrieb

- Die **Webcam** wird automatisch erkannt (keine Pi Camera nötig)
- Die **Waage** wird simuliert (Mock-Daten, kein USB-Serial)
- Falls die Webcam beim ersten Start nicht geht: **Kamerazugriff** in den Systemeinstellungen erlauben
  - **macOS:** Systemeinstellungen → Datenschutz & Sicherheit → Kamera → Terminal/IDE erlauben
  - **Windows:** Einstellungen → Datenschutz → Kamera
- **Kamera wechseln:** Im Dashboard über das Dropdown-Menü die gewünschte Kamera auswählen

---

## 11. Fehlerbehebung

### Waage wird nicht erkannt

| Problem | Lösung |
|---|---|
| `/dev/ttyUSB0` nicht vorhanden | USB-Kabel prüfen, anderen Port testen, Waage neu starten |
| Permission denied | `sudo usermod -a -G dialout pi` und neu einloggen |
| Gewicht immer `None` | Baudrate prüfen (muss 9600 sein), Waage auf Werkeinstellung |

### Kamera zeigt kein Bild

| Problem | Lösung |
|---|---|
| Pi Camera nicht erkannt | CSI-Kabel prüfen (richtige Richtung, richtiger Port) |
| `rpicam-still` Fehler | `sudo apt install -y rpicam-apps` |
| Webcam: "not authorized" | Kamerazugriff in Systemeinstellungen erlauben |
| Bild zu dunkel | Ringlicht einschalten, Position anpassen |

### Dashboard nicht erreichbar

| Problem | Lösung |
|---|---|
| Seite lädt nicht | `sudo systemctl status bottle-inspection` prüfen |
| Port 8080 blockiert | Firewall prüfen: `sudo ufw allow 8080/tcp` |
| IP unbekannt | `hostname -I` auf dem Pi eingeben |

### SAP-Verbindung schlägt fehl

| Problem | Lösung |
|---|---|
| 401 Unauthorized | Client-ID/Secret in `.env` prüfen |
| 403 Forbidden | API-Berechtigungen im SAP BTP Cockpit prüfen |
| Timeout | Internet-Verbindung prüfen, SAP-URL prüfen |
| Token-Fehler | Token-URL in `.env` prüfen (muss auf `/oauth/token` enden) |

### Auto-Update funktioniert nicht

```bash
# Timer-Status prüfen
sudo systemctl status bottle-inspection-update.timer

# Manuell Update auslösen
cd /home/pi/DemoSouthAfrica && git pull origin main

# Timer neu starten
sudo systemctl restart bottle-inspection-update.timer
```

---

## Schnellreferenz

```bash
# Service starten/stoppen
sudo systemctl start|stop|restart bottle-inspection

# Logs anschauen
sudo journalctl -u bottle-inspection -f

# WLAN-Status
nmcli dev wifi list

# IP-Adresse anzeigen
hostname -I

# Manuelles Update von GitHub
cd /home/pi/DemoSouthAfrica && git pull origin main

# SAP-Verbindung testen
cd /home/pi/DemoSouthAfrica && source .venv/bin/activate && python scripts/test_sap_connection.py
```
