# Bottle Inspection Demo – Raspberry Pi

## Projektübersicht
Demo-System zur automatischen Qualitätskontrolle von kleinen 0,1L Glasflaschen.
Das System prüft ob ein Label auf der Flasche vorhanden ist, misst das Gewicht und erfasst Umgebungsdaten.

---

## Hardware

| Komponente | Modell | Anschluss |
|---|---|---|
| Computer | Raspberry Pi 4 Model B 4GB | - |
| Waage | KERN PCB 2000-1 (2kg / 0,1g) | USB-B → USB-A |
| Kamera | Raspberry Pi Camera Module 3 (12MP, HDR, Autofokus) | CSI-Port |
| Umgebungssensor | BME280 (Temperatur, Luftfeuchtigkeit, Luftdruck) | I2C (GPIO) |
| Beleuchtung | Ringlicht | Extern |
| OS | Raspberry Pi OS (64-bit, Bookworm) | - |

## GPIO Belegung BME280 (I2C)

| BME280 Pin | Raspberry Pi Pin |
|---|---|
| VCC | Pin 1 (3.3V) |
| GND | Pin 6 (GND) |
| SDA | Pin 3 (GPIO2) |
| SCL | Pin 5 (GPIO3) |

---

## Software Dependencies

```bash
pip install pyserial
pip install opencv-python
pip install adafruit-circuitpython-bme280
pip install adafruit-blinka
pip install RPi.GPIO
```

I2C aktivieren:
```bash
sudo raspi-config → Interface Options → I2C → Enable
```

---

## Schnittstellen

### Waage (KERN PCB 2000-1)
- Verbindung: USB → `/dev/ttyUSB0`
- Baudrate: 9600
- Protokoll: KERN Communication Protocol (KCP)

```python
import serial
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=2)
raw = ser.readline().decode('utf-8').strip()
# Beispieloutput: "     150.3 g"
```

### Kamera (Camera Module 3)
- Verbindung: CSI
- Library: OpenCV + picamera2

```python
from picamera2 import Picamera2
import cv2

picam2 = Picamera2()
picam2.start()
frame = picam2.capture_array()
```

### BME280 (I2C)
- Adresse: 0x76 (oder 0x77 je nach Modul)

```python
import board
import adafruit_bme280.basic as adafruit_bme280

i2c = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

print(f"Temperatur: {bme280.temperature:.1f} °C")
print(f"Luftfeuchtigkeit: {bme280.humidity:.1f} %")
print(f"Luftdruck: {bme280.pressure:.1f} hPa")
```

---

## Ziel-Logik

```
Flasche auf Waage stellen
    │
    ├─ Waage: Gewicht im Toleranzbereich? (z.B. 150g–260g)
    │         → außerhalb: SCHLECHT ✗
    │
    ├─ Kamera: Label erkannt?
    │         → kein Label: SCHLECHT ✗
    │
    └─ Beide OK → GUT ✓
```

## Toleranzwerte (Richtwerte, nach Tests anpassen)
- Flasche leer: ca. 80–120g
- Flasche gefüllt (0,1L): ca. 150–260g
- Label vorhanden: Kantenkontrast oder Helligkeitsdifferenz > Schwellwert

---

## Projektstruktur

```
/bottle-inspection/
├── .github/
│   └── workflows/
│       └── deploy.yml       # GitHub Actions Auto-Deploy auf Pi
├── main.py                  # Hauptprogramm, Steuerlogik
├── scale.py                 # Waagen-Modul (KERN PCB)
├── camera.py                # Kamera-Modul (Label-Erkennung)
├── sensor.py                # BME280-Modul
├── config.py                # Toleranzwerte, Schwellwerte, Ports
├── requirements.txt         # Python Dependencies
└── CLAUDE.md                # Diese Datei
```

---

## GitHub Actions – Auto-Deploy auf Raspberry Pi

### Konzept
Bei jedem `git push` auf `main` wird der Code automatisch per SSH auf den Pi deployed und der Service neu gestartet. Der Pi muss dafür erreichbar sein (lokales Netz oder per Tailscale für Fernzugriff).

### 1. SSH-Key einrichten (einmalig)

Auf deinem Entwicklungsrechner:
```bash
ssh-keygen -t ed25519 -C "github-actions-deploy"
# Speichern z.B. als ~/.ssh/id_deploy
```

Public Key auf den Pi kopieren:
```bash
ssh-copy-id -i ~/.ssh/id_deploy.pub pi@<PI_IP>
```

### 2. GitHub Secrets hinterlegen

In GitHub → Repository → Settings → Secrets and variables → Actions:

| Secret Name | Inhalt |
|---|---|
| `PI_HOST` | IP-Adresse des Pi (z.B. `192.168.1.100` oder Tailscale-IP) |
| `PI_USER` | `pi` |
| `PI_SSH_KEY` | Inhalt der privaten Key-Datei (`id_deploy`) |
| `PI_PROJECT_PATH` | Pfad auf dem Pi (z.B. `/home/pi/bottle-inspection`) |

### 3. GitHub Actions Workflow

Datei: `.github/workflows/deploy.yml`

```yaml
name: Deploy to Raspberry Pi

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.PI_SSH_KEY }}" > ~/.ssh/id_deploy
          chmod 600 ~/.ssh/id_deploy
          ssh-keyscan -H ${{ secrets.PI_HOST }} >> ~/.ssh/known_hosts

      - name: Deploy to Pi
        run: |
          ssh -i ~/.ssh/id_deploy ${{ secrets.PI_USER }}@${{ secrets.PI_HOST }} "
            cd ${{ secrets.PI_PROJECT_PATH }} &&
            git pull origin main &&
            pip install -r requirements.txt --break-system-packages &&
            sudo systemctl restart bottle-inspection
          "

      - name: Health Check
        run: |
          ssh -i ~/.ssh/id_deploy ${{ secrets.PI_USER }}@${{ secrets.PI_HOST }} "
            sudo systemctl status bottle-inspection --no-pager
          "
```

### 4. Systemd Service auf dem Pi einrichten

Damit das Skript automatisch startet und nach einem Deploy neu gestartet werden kann:

```bash
sudo nano /etc/systemd/system/bottle-inspection.service
```

```ini
[Unit]
Description=Bottle Inspection Demo
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/bottle-inspection/main.py
WorkingDirectory=/home/pi/bottle-inspection
StandardOutput=journal
StandardError=journal
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable bottle-inspection
sudo systemctl start bottle-inspection
```

Logs live anschauen:
```bash
sudo journalctl -u bottle-inspection -f
```

### 5. Git Repository auf dem Pi initialisieren (einmalig)

```bash
cd /home/pi
git clone https://github.com/<dein-user>/bottle-inspection.git
```

---

## Fernwartung – Tailscale (empfohlen)

Wenn der Pi nicht immer im gleichen Netzwerk ist oder du von unterwegs drauf zugreifen willst, empfiehlt sich **Tailscale** – ein Zero-Config VPN, kostenlos für private Nutzung.

### Installation auf Pi:
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

### Installation auf deinem Rechner:
tailscale.com/download → App installieren → einloggen mit gleichem Account

Danach ist der Pi per `ssh pi@<tailscale-ip>` von überall erreichbar – auch unterwegs, auch hinter NAT. Die Tailscale-IP einmalig in das GitHub Secret `PI_HOST` eintragen, dann funktioniert der Auto-Deploy von überall.

---

## Deploy-Workflow Zusammenfassung

```
Du pushst Code auf GitHub (main branch)
        │
        ▼
GitHub Actions startet automatisch
        │
        ▼
Actions verbindet sich per SSH mit Pi (via Tailscale)
        │
        ▼
git pull → pip install → systemctl restart
        │
        ▼
Health Check: Service läuft? ✓
```

---

## Nützliche Befehle

```bash
# Service Status prüfen
sudo systemctl status bottle-inspection

# Logs live anschauen
sudo journalctl -u bottle-inspection -f

# Manuell neu starten
sudo systemctl restart bottle-inspection

# Waagen-Port prüfen
ls /dev/ttyUSB*

# BME280 I2C-Adresse prüfen
i2cdetect -y 1

# Kamera testen
libcamera-hello

# Tailscale IP anzeigen
tailscale ip
```

---

## Hinweise
- Ringlicht immer einschalten bevor Kamera-Auswertung startet
- Waage vor jedem Messdurchlauf tarieren (Tara-Funktion per KCP-Befehl)
- Nach jedem `git push` auf `main` deployed GitHub Actions automatisch auf den Pi
- Tailscale-IP bleibt immer gleich, auch wenn sich die lokale Netzwerk-IP ändert
- Branch Protection Rule in GitHub empfohlen: kein direkter Push auf `main`, nur über Pull Request (Vier-Augen-Prinzip)