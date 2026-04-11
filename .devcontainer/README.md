# MemeTrader Codespace Configuration

This directory contains the VS Code Devcontainer configuration for the **memetrader-unification** branch, which combines Hermes Agent and NOFX into a unified MemeTrader platform.

## What's Configured

### Base Environment
- **Python 3.12** with full Bullseye Linux runtime
- **Go** (latest) for NOFX backend
- **Node.js 20** for NOFX React UI
- **Docker** for containerized workflows

### Installed Features
- GitHub CLI for repository management
- SSH mount for git credentials
- Docker-in-Docker for building containers

### Port Forwarding
- **8643**: Hermes Agent API
- **8642**: Hermes Agent Gateway (messaging)
- **8080**: NOFX Trading Backend
- **3000**: NOFX React Trading UI
- **8686**: Hermes UI (deprecated, silenced)

### Python Dependencies
All extras are installed:
- `dev` - pytest, debugpy, mcp
- `voice` - faster-whisper, sounddevice
- `messaging` - Telegram, Discord, Slack, Signal
- `cli` - Terminal UI enhancements
- `tts-premium` - ElevenLabs TTS
- `pty` - PTY process support
- `honcho` - Honcho integration
- `mcp` - Model Context Protocol
- `homeassistant` - Home Assistant integration
- `sms` - SMS support
- `acp` - Agent Client Protocol
- `cron` - Scheduler
- `crypto` - Cryptographic utilities

## Post-Create Setup

The `post-create.sh` script automatically:
1. Verifies you're on `memetrader-unification` branch
2. Creates/activates Python virtual environment
3. Installs all Python dependencies
4. Discovers and verifies Hermes tools (web_search, browser, etc.)
5. Installs NOFX requirements (Go backend modules)
6. Installs NOFX UI npm packages
7. Displays setup summary and next steps

## Starting the Development Environment

### Terminal 1: Hermes Agent
```bash
source .venv/bin/activate
python -m hermes_cli.main
```

### Terminal 2: NOFX Backend (Go)
```bash
cd nofx
go run .
```

### Terminal 3: NOFX React UI
```bash
cd nofx-ui
npm run dev
```

## Repository Configuration

### Git Remotes
```
origin     → https://github.com/RaptorLaunchPage/hermes-agent (fork)
upstream   → https://github.com/NousResearch/hermes-agent.git (official)
```

### Current Branch
```
memetrader-unification → MemeTrader Unification: Hermes Agent + NOFX Integration
```

## Troubleshooting

### Tools Not Discovered
If `web_search` or browser tools aren't discovered:
```bash
source .venv/bin/activate
python -c "import model_tools; print(model_tools.get_all_tool_names())"
```

### Missing Dependencies
Reinstall full extras:
```bash
pip install -e ".[all,dev,voice,crypto]"
```

### Git Remote Issues
To sync with Official Nous Research repo:
```bash
git fetch upstream
git merge upstream/main
```

## Branch-Specific Notes

The **memetrader-unification branch** contains:
- Complete Hermes Agent codebase with all tools
- NOFX trading system integration
- Full browser automation (Browserbase)
- Vision/image analysis capabilities
- Multi-platform messaging (Telegram, Discord, Slack, etc.)
- Cryptographic trading utilities

This is a **development branch** for MemeTrader's unified architecture.
