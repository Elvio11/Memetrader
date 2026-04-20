# Quick Start - Hermes Agent

## First Time Setup
- Run `./setup-hermes.sh` — installs Python 3.11, creates venv, installs all dependencies
- Wait for completion (takes ~2-3 minutes)
- This creates `venv/` directory and installs 147+ packages

## Start Hermes Services
- Activate venv: `source venv/bin/activate`
- Run: `./start-memetrader.sh`
- Services start on ports: **8643** (FastAPI), **8642** (Gateway)

## Access Hermes
- **CLI**: `hermes` (in any terminal with venv active)
- **Web UI**: http://127.0.0.1:8643
- **Gateway**: http://127.0.0.1:8642

## Common Commands
- Check health: `hermes doctor`
- View config: `cat ~/.hermes/config.yaml`
- Set API key: Add to `~/.hermes/.env`
- Stop services: `pkill -f "python.*fastapi_server|hermes.*gateway"`
- View logs: `tail -f /tmp/hermes-fastapi.log` or `/tmp/hermes-gateway.log`

## Troubleshooting
- Permission denied on script? Run: `chmod +x script.sh`
- Venv not found? Run `./setup-hermes.sh` again
- Port in use? Kill processes or update config
- Module not found? Ensure venv is activated before running commands

## Next
- Configure API keys in `~/.hermes/.env`
- Run `hermes` to start interactive sessions
- Check `README.md` for advanced setup
