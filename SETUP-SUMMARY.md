# Hermes Setup Complete - Summary & Next Steps

## What We've Completed

### 1. ✅ Created QUICK-START-HERMES.md
Quick reference guide with bullet points for:
- First-time setup (one command)
- Starting services
- Accessing Hermes CLI & Web UI
- Common commands & troubleshooting

### 2. ✅ Created SYSTEM-DEPENDENCIES-GUIDE.md  
Comprehensive guide explaining:
- **What "system dependency not met" means** — OS-level packages, not Python packages
- **Which tools have system dependencies** — image_gen, messaging, homeassistant, social, rl
- **Why they're optional** — skip safely if not needed
- **How to fix** — install OS packages or skip gracefully

### 3. ✅ Updated setup-hermes.sh Script
Improvements made:
- Better tinker-atropos detection and installation
- Interactive prompt to clone tinker (optional)
- Clear messaging about what's required vs optional
- Graceful fallback if clone fails
- Better error handling

### 4. ✅ Fixed Your Start Script
- Updated `start-memetrader.sh` to use correct venv paths
- Now runs: `venv/bin/python3` instead of system `python3`
- Now runs: `venv/bin/hermes` instead of `.venv/bin/hermes`

---

## Understanding the Warnings

### "System Dependency Not Met" = Optional Features
```
⚠ image_gen (system dependency not met)       → Can skip
⚠ messaging (system dependency not met)       → Can skip  
⚠ homeassistant (system dependency not met)   → Can skip (needs Home Assistant)
⚠ social (system dependency not met)          → Can skip
⚠ rl (missing TINKER_API_KEY)                 → Can skip (or clone tinker-atropos)
```

These do **NOT** prevent Hermes from working. They're specialized tools you only need for specific tasks.

---

## Tinker-Atropos Setup (Optional)

If you want reinforcement learning tools:

### Method 1: Manual Clone (Recommended)
```bash
cd /workspaces/Memetrader

# Clone the tinker repo
git clone https://github.com/Fragfolio-arch/tinker-atropos.git tinker-atropos

# Install it
source venv/bin/activate
pip install -e ./tinker-atropos

# Verify
hermes doctor  # Should show tinker installed
```

### Method 2: Let Setup Script Clone It
```bash
./setup-hermes.sh
# When prompted "Clone tinker-atropos now? [y/N]" just type: y
```

---

## Quick Verification Checklist

✅ **Virtual environment created?**
```bash
ls -d venv/  # Should show venv directory
```

✅ **Dependencies installed?**
```bash
source venv/bin/activate
pip list | grep -E "anthropic|uvicorn|fastapi"  # Should show packages
```

✅ **Hermes CLI working?**
```bash
source venv/bin/activate
hermes doctor  # Full health check
```

✅ **Services started?**
```bash
./start-memetrader.sh
# Should show services starting on ports 8643 and 8642
```

---

## Files Modified/Created

| File | Change | Purpose |
|------|--------|---------|
| `QUICK-START-HERMES.md` | Created | 60-second setup guide |
| `SYSTEM-DEPENDENCIES-GUIDE.md` | Created | Explains system deps, tinker setup |
| `setup-hermes.sh` | Updated | Better tinker-atropos handling |
| `start-memetrader.sh` | Updated | Uses correct venv paths |
| `Setup-MemeTrader-Run-first` | Created | Step-by-step initial setup |

---

## Recommended Next Steps

### 1. Start Fresh Install (Optional - Very Safe)
```bash
# Fresh Python & dependencies
rm -rf venv
./setup-hermes.sh
# Respond "n" (no) to clone tinker unless you need RL
```

### 2. Test Hermes CLI
```bash
source venv/bin/activate
hermes doctor         # Full health check
hermes -m "Hello"    # Quick test conversation
```

### 3. Start Services
```bash
./start-memetrader.sh
# Wait 10 seconds for startup
curl http://127.0.0.1:8643/health  # Should work now
```

### 4. Access Web UI
```bash
# Open in browser:
http://127.0.0.1:8643
```

### 5. (Optional) Set Up Tinker If Needed
```bash
git clone <tinker-url> tinker-atropos
pip install -e ./tinker-atropos
hermes doctor  # Verify installation
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Permission denied` on scripts | `chmod +x script.sh` |
| `ModuleNotFoundError` | Activate venv: `source venv/bin/activate` |
| Port 8643 already in use | `pkill -f fastapi_server` then restart |
| Tinker clone fails | Check GitHub URL, ensure network access |
| `hermes doctor` shows warnings | Review SYSTEM-DEPENDENCIES-GUIDE.md — they're optional! |

---

## Final Notes

- **System dependencies are safe to ignore** — they're for optional features
- **Tinker-Atropos is optional** — only needed for RL training
- **Setup script is now more user-friendly** — will prompt for tinker with clear explanation
- **All core Hermes functionality works without these optional tools**

---

## Key Documentation

- 📖 **Quick Start**: `QUICK-START-HERMES.md`
- 📖 **System Dependencies**: `SYSTEM-DEPENDENCIES-GUIDE.md`
- 📖 **Initial Setup Guide**: `Setup-MemeTrader-Run-first`
- 📖 **Architecture Reference**: `AGENTS.md` (provided by project team)

---

**You're all set! Hermes Agent is ready to use. 🚀**
