# src/hardware/

Hardware abstraction layer for scale and camera.

## Modules

- **scale.py** — `Scale` class: KERN PCB 2000-1 via USB serial (/dev/ttyUSB0, 9600 baud, KCP protocol). Commands: 'w' (weight), 't' (tare).
- **camera.py** — `Camera` class (picamera2 wrapper) + `detect_label()` and `detect_contamination()` pure functions that take a numpy frame.
- **mock.py** — `MockScale`, `MockCamera`: return random/demo data. `WebcamCamera`: uses laptop webcam via OpenCV for real image capture with device selection support.

## Mock / Fallback Strategy

Pi-only libraries (picamera2) are imported in try/except blocks. On non-Pi platforms, `main.py` tries `WebcamCamera` first (real webcam via OpenCV), then falls back to `MockCamera`. Both real and mock classes share the same interface (start, capture, stop, is_available).

Hardware is optional: the inspection engine accepts `None` for scale or camera and skips the corresponding checks.
