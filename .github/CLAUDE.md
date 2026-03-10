# .github/

GitHub configuration.

No CI/CD workflows — deployment is handled by the Pi itself via a systemd timer that runs `git pull` every minute (see `scripts/pi_setup.sh`).
