# Cleanup & Refactoring Guidance

## 🔴 Critical Issues

### 1. Duplicate Frontend Directory (HIGH PRIORITY)

**Issue**: Two identical React frontend directories exist:
- `nofx/web/` - Original
- `nofx-ui/` - Duplicate (appears to be merge artifact)

**Impact**: Maintenance burden, potential version drift

**Action**: Delete `nofx-ui/` and keep `nofx/web/`, OR vice versa

```bash
# Recommended: Keep nofx/web/ as canonical
rm -rf nofx-ui/
```

---

### 2. Paper Trading vs Live Trading Confusion

**Issue**: Both exist with unclear relationship:
- `tools/trading/` (paper)
- `tools/nofx_trading_tool.py` (live via NOFX)

**Question**: Should NOFX replace paper trading, or coexist?

**Action**: Document the relationship clearly in docs

---

### 3. Inconsistent Port References

**Issue**: Multiple sources reference different ports

| Source | Reference |
|--------|----------|
| README.md | Port 8686 "deprecated" |
| UNIFICATION_PLAN.md | Various ports |
| Actual code | Need verification |

**Action**: Audit all port references, consolidate to single source

---

## 🟡 Improvements

### 4. Authentication Integration

**Issue**: NOFX has JWT but Hermes doesn't use it consistently

**Action**: Document auth flow between systems

---

### 5. No Integration Tests for NOFX Tools

**Issue**: Tools defined but not tested against running NOFX instance

**Action**: Add integration tests:
```python
# tests/tools/test_nofx_integration.py
import pytest
from tools.nofx_trading_tool import nofx_positions

def test_nofx_positions_requires_nofx():
    """Verify NOFX dependency is clear."""
    # Should have clear error if NOFX not running
```

---

### 6. Inconsistent Naming

| Current | Should Be |
|---------|-----------|
| `nofx-ui/` | Either keep as is or move to `web/` |
| `hermes_agent.egg-info/` | Can remove (build artifact) |

**Action**: Standardize directory names

---

### 7. Environment Variable Consolidation

**Issue**: Multiple env var sources:
- `.env.example` (root)
- `nofx/.env.example` (NOFX)
- `config.yaml` (Hermes)

**Action**: Document precedence, consider single source

---

## 🟢 Nice-to-Have Optimizations

### 8. Remove Legacy Code

| File | Status | Recommendation |
|------|--------|------------|
| `__pycache__/` | Build | Safe to delete |
| `hermes_agent.egg-info/` | Build | Safe to delete |
| `*.pyc` | Build | Safe to delete |

---

### 9. Consolidate Documentation

**Issue**: Multiple doc locations:
- Root-level `README.md`
- Root-level `docs/`
- `website/docs/`

**Action**: Keep root-level docs as canonical

---

### 10. Startup Scripts Consolidation

**Issue**: Multiple startup approaches:
- `start-memetrader.sh` (Python-only)
- `start-nofx.sh` (Go-only)

**Action**: Single unified startup script

---

## Summary of Actions

| Priority | Issue | Action |
|----------|-------|-------|
| 🔴 HIGH | Duplicate frontend | Delete `nofx-ui/` |
| 🔴 HIGH | Paper vs Live Trading | Document relationship |
| 🟡 MEDIUM | Port consistency | Audit all references |
| 🟡 MEDIUM | Auth integration | Document flow |
| 🟢 LOW | Environment vars | Document precedence |

---

## File to Remove

```bash
# Safe to delete:
rm -rf nofx-ui/
rm -rf __pycache__/
rm -rf */__pycache__/
rm -rf*/.**/__pycache__/
rm -rf *.egg-info/
rm -rf */**/*.egg-info/
```