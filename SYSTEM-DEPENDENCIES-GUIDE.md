# System Dependencies & Tinker Setup Guide

## What Does "System Dependency Not Met" Mean?

When `hermes doctor` shows **"(system dependency not met)"**, it means the tool requires **OS-level packages or services** that aren't installed on your system—not just Python packages.

### Tools with System Dependencies

| Tool | System Requirement | What It Does | Fix |
|------|-------------------|--------------|-----|
| **image_gen** | ImageMagick / Pillow support | Generate and manipulate images | ⚠️ Optional — skip if not needed |
| **messaging** | Dbus/system services | Send desktop notifications | ⚠️ Optional — skip in headless environments |
| **homeassistant** | Home Assistant service running | Control smart home devices | ⚠️ Optional — requires separate Home Assistant instance |
| **social** | System notify-daemon | Post to social media | ⚠️ Optional — skip if not needed |
| **rl** (RL training) | Requires tinker-atropos submodule | Reinforcement learning tools | **See setup below** |

### Why These Are Optional
These tools are **not required** for core Hermes functionality. They enable specialized features:
- **Image Gen** — AI image generation (requires external APIs)
- **Messaging** — Desktop notifications (Linux/macOS system services)
- **HomeAssistant** — Smart home control (requires running HA instance)
- **Social** — Social media posting (requires API keys + system notify)

### How to Fix System Dependencies

#### Option 1: Skip (Recommended for Testing)
System dependencies don't affect core Agent functionality. Ignore them if you don't need these features.

#### Option 2: Install Required Packages
On **Ubuntu/Debian**:
```bash
sudo apt install -y libmagic1 libnotify-bin  # For image_gen + messaging
```

On **macOS**:
```bash
brew install imagemagick libnotify  # For image_gen + messaging
```

---

## Setting Up Tinker-Atropos (RL Training Backend)

Tinker-Atropos is an optional RL training environment. It's a submodule that needs to be explicitly cloned.

### Step 1: Clone the Tinker Submodule

Since `.gitmodules` isn't configured, clone it manually as a local folder:

```bash
cd /workspaces/Memetrader

# Clone directly from the repo (adjust URL if needed)
git clone https://github.com/Fragfolio-arch/tinker-atropos.git tinker-atropos
# OR if it's in the same org:
# git clone https://github.com/Fragfolio-arch/tinker-atropos-rl.git tinker-atropos

cd tinker-atropos
ls -la  # Verify pyproject.toml exists
```

### Step 2: Install Tinker Locally

```bash
cd /workspaces/Memetrader
source venv/bin/activate

# Install the local tinker package
pip install -e ./tinker-atropos
```

### Step 3: Verify Installation

```bash
hermes doctor  # Should no longer warn about tinker-atropos
```

---

## Update to setup-hermes.sh (Automatic)

The script has been updated to:
1. ✅ Check if `tinker-atropos/` folder exists
2. ✅ Auto-install if found with `pyproject.toml`
3. ✅ Warn gracefully if not found
4. ✅ Provide explicit clone command for manual setup

**What changed:**
- Improved error messages
- Option to clone tinker-atropos interactively (optional)
- Better handling of missing submodules

### Run Setup Again (After Cloning Tinker)

```bash
./setup-hermes.sh
```

The script will now:
- Detect the `tinker-atropos/` folder
- Install its dependencies
- Show ✓ confirmation (instead of warning)

---

## Quick Reference

| Scenario | Command |
|----------|---------|
| Clone tinker manually | `git clone <url> tinker-atropos` |
| Install after clone | `pip install -e ./tinker-atropos` |
| Check tool status | `hermes doctor` |
| Verify venv activated | `which python` (should show `venv/bin/python`) |
| Run setup fresh | `./setup-hermes.sh` |

---

## FAQ

**Q: Do I need tinker-atropos?**
A: No, unless you're doing RL training. It's optional for core Agent features.

**Q: Can I skip "system dependency not met" warnings?**
A: Yes! They're safe to ignore unless you specifically need that tool.

**Q: What if tinker-atropos fails to clone?**
A: Check the GitHub URL — the repo may be private or use a different name. Ask the maintainer for the correct URL.

**Q: Does RL require GPU?**
A: Likely yes. Tinker-Atropos may need CUDA. Check its README for GPU setup after cloning.

---

## Next Steps

1. ✅ Understand system dependencies (read above)
2. 📦 Clone tinker-atropos (if needed)
3. 🔧 Run `./setup-hermes.sh` again
4. ✓ Verify with `hermes doctor`
5. 🚀 Run `./start-memetrader.sh` to start services
