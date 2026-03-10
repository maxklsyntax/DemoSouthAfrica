# .github/

GitHub configuration and CI/CD.

## workflows/deploy.yml

Auto-deploy to Raspberry Pi on push to `main`:
1. SSH into Pi using secrets (PI_HOST, PI_USER, PI_SSH_KEY, PI_PROJECT_PATH)
2. `git pull` → `pip install -r requirements.txt` → `systemctl restart bottle-inspection`
3. Health check: verify service is running

Required GitHub Secrets: `PI_HOST`, `PI_USER`, `PI_SSH_KEY`, `PI_PROJECT_PATH`
