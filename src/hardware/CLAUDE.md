# src/hardware/

Hardware abstraction layer for scale, camera, and environment sensor.

## Modules

- **scale.py** — `Scale` class: KERN PCB 2000-1 via USB serial (/dev/ttyUSB0, 9600 baud, KCP protocol). Commands: 'w' (weight), 't' (tare).
- **camera.py** — `Camera` class (picamera2 wrapper) + `detect_label()` and `detect_contamination()` pure functions that take a numpy frame.
- **sensor.py** — `EnvironmentSensor` class: BME280 via I2C (adafruit library).
- **mock.py** — `MockScale`, `MockCamera`, `MockSensor`: return random/demo data for local development.

## Mock Strategy

Pi-only libraries (picamera2, adafruit_bme280, board) are imported in try/except blocks. On non-Pi platforms, `main.py` uses mock classes from `mock.py` instead of the real hardware classes. Both real and mock classes share the same interface (connect, read, close, etc.).
