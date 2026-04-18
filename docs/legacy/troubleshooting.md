# Troubleshooting Guide

## Common Issues and Solutions

---

## Hermes Issues

### ❌ Hermes CLI Won't Start

**Symptom**: `hermes` command not found

**Solution**:
```bash
source ~/.bashrc  # or: source ~/.zshrc
hermes
```

---

### ❌ No Messaging Platforms Enabled

**Symptom**: `WARNING: No messaging platforms enabled.`

**Solution**: Configure at least one platform:
```bash
hermes gateway setup
# Follow wizard to configure Telegram, Discord, etc.
```

---

### ❌ API Key Errors

**Symptom**: `Invalid API key` or `Authentication failed`

**Solution**:
```bash
# Check config.yaml
cat ~/.hermes/config.yaml

# Set key directly
hermes config set openai_api_key YOUR_KEY
hermes config set anthropic_api_key YOUR_KEY
```

---

## NOFX Issues

### ❌ NOFX Won't Build

**Symptom**: Go build errors

**Solution**:
```bash
cd nofx
go mod download
go build -o nofx ./cmd/nofx
```

---

### ❌ NOFX API Not Responding

**Symptom**: Connection refused on port 8080

**Solution**:
```bash
# Check if NOFX is running
lsof -i :8080

# Start NOFX
cd nofx && ./nofx
```

---

### ❌ Exchange Connection Failed

**Symptom**: `Failed to connect to exchange`

**Solution**: 
1. Verify API credentials in `nofx/.env`
2. Check exchange status at https://status.exchange.com
3. Verify IP whitelist on exchange

---

## NOFX UI Issues

### ❌ Blank Dashboard

**Symptom**: No data showing in dashboard

**Solution**:
1. Ensure NOFX Go is running on port 8080
2. Check browser console for CORS errors
3. Verify `JWT_SECRET` is set

---

### ❌ Can't Login

**Symptom**: Authentication failed

**Solution**:
```bash
# Generate new JWT token in NOFX
# Or set in environment
export JWT_SECRET=your-secret
```

---

## Integration Issues

### ❌ Hermes Can't Reach NOFX

**Symptom**: `nofx_positions` returns error

**Solution**:
```bash
# Verify NOFX is running
curl http://localhost:8080/api/status

# Check configuration
hermes config set nofx.api_url http://localhost:8080
hermes config set nofx.api_token YOUR_TOKEN
```

---

### ❌ Trading Tools Not Available

**Symptom**: Unknown tool `nofx_trade`

**Solution**:
```bash
# Enable NOFX toolset
hermes tools enable nofx
hermes
```

---

## Port Conflicts

### ❌ Port Already in Use

**Symptom**: `Address already in use`

**Solution**:
```bash
# Find process using port
lsof -i :8643  # Or 8642, 8080, 3000

# Kill process
kill -9 PID

# Or use different port
hermes config set api_port 8644
```

---

## Database Issues

### ❌ SQLite Errors

**Symptom**: `database is locked` or `corrupted`

**Solution**:
```bash
# Backup and recreate
cp ~/.hermes/hermes.db ~/.hermes/hermes.db.bak
rm ~/.hermes/hermes.db
# Restart Hermes to recreate
```

---

## Performance Issues

### ❌ Slow Responses

**Symptom**: Commands take very long

**Solution**:
1. Check API key rate limits
2. Reduce context window size
3. Disable unused toolsets

---

## Get More Help

| Resource | URL |
|----------|-----|
| Discord | https://discord.gg/NousResearch |
| Issues | https://github.com/NousResearch/Memetrader/issues |
| Docs | https://hermes-agent.nousresearch.com/docs/ |

---

## Diagnostic Commands

```bash
# Health check
curl http://127.0.0.1:8643/health

# Gateway status
hermes gateway status

# NOFX status
curl http://localhost:8080/api/status

# List processes
lsof -i :8643 -i :8642 -i :8080 -i :3000
```