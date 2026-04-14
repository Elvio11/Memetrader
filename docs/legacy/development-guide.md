# Development Guide - MemeTrader

## Developing New Features

### Where to Add Code

| Feature Type | Location | Example |
|------------|---------|---------|
| New Hermes Tool | `tools/{feature}_tool.py` | `tools/nofx_trading_tool.py` |
| New Hermes CLI Command | `hermes_cli/commands.py` | Add to `COMMAND_REGISTRY` |
| New NOFX Endpoint | `nofx/api/` | Add to `api/server.go` |
| New Exchange Connector | `nofx/trader/` | New exchange folder |
| New NOFX UI Page | `nofx-ui/src/pages/` | New page component |
| New Memory Plugin | `plugins/memory/` | New plugin folder |

---

## How to Add a New Hermes Tool

### Step 1: Create Tool File

Create `tools/my_new_tool.py`:

```python
import json
from tools.registry import registry

def my_new_tool(param: str, task_id: str = None) -> str:
    """Description of what the tool does."""
    return json.dumps({"success": True, "data": param})

registry.register(
    name="my_new_tool",
    toolset="my_toolset",
    schema={
        "name": "my_new_tool",
        "description": "Description of what the tool does",
        "parameters": {
            "type": "object",
            "properties": {
                "param": {"type": "string", "description": "The parameter"}
            }
        }
    },
    handler=lambda args, **kw: my_new_tool(
        param=args.get("param", ""), 
        task_id=kw.get("task_id")
    ),
)
```

### Step 2: Register Tool

In `model_tools.py`, add import:

```python
from tools import my_new_tool
```

### Step 3: Add to Toolset

In `toolsets.py`, add to appropriate toolset list.

---

## How to Add a New NOFX Endpoint

### Step 1: Create Handler

In `nofx/api/handlers/`:

```go
func GetMyData(c *gin.Context) {
    // Fetch data from store or trader
    c.JSON(200, gin.H{"data": "example"})
}
```

### Step 2: Register Route

In `nofx/api/server.go`:

```go
router.GET("/api/my-data", handlers.GetMyData)
```

---

## Avoiding Breaking Integrations

### Hermes → NOFX Integration Rules

1. **Never change API URL format** - Existing tools expect `/api/{resource}`
2. **Maintain backward compatibility** - New fields should be optional
3. **Return valid JSON** - Tools expect JSON response
4. **Handle errors gracefully** - Return `{"error": "message"}` not crash

### NOFX → Exchange Integration Rules

1. **Handle rate limits** - Add retry with exponential backoff
2. **Validate inputs** - Check params before API calls
3. **Log errors** - Use structured logging

---

## Testing Strategy

### Hermes Tests

```bash
# Run all tests
python -m pytest tests/ -q

# Run specific test
python -m pytest tests/test_model_tools.py -q
```

### NOFX Tests

```bash
# Run Go tests
cd nofx && go test ./...

# Run specific package
cd nofx && go test ./api/...
```

### NOFX UI Tests

```bash
# Run React tests
cd nofx-ui && npm test
```

---

## Dependency Awareness

### Shared Dependencies

| Dependency | Hermes | NOFX | Notes |
|------------|--------|------|-------|
| Python | 3.11+ | - | Core language |
| Go | - | 1.25+ | Backend |
| SQLite | hermes.db | nofx.db | Separate DBs |

### Environment Variables

| Variable | Used By | Description |
|----------|---------|-------------|
| `NOFX_API_URL` | Hermes | NOFX endpoint |
| `NOFX_API_TOKEN` | Hermes | Auth token |
| `JWT_SECRET` | NOFX | JWT signing |
| `ANTHROPIC_API_KEY` | Hermes | LLM provider |

---

## Code Style

### Python

- Follow PEP 8
- Use type hints where helpful
- Run `black` formatter before commit

### Go

- Follow Go standard format (`go fmt`)
- Use `golangci-lint` for linting
- Add unit tests for new functions

### TypeScript

- Follow ESLint config
- Use functional components with hooks

---

## Best Practices

### Tool Development

1. Always return valid JSON strings
2. Handle errors gracefully
3. Add logging for debugging
4. Use type hints
5. Document in schema description

### API Development

1. Use proper HTTP methods
2. Return appropriate status codes
3. Add request validation
4. Document with comments

---

## Common Pitfalls

| Pitfall | Prevention |
|---------|-----------|
| Breaking existing tools | Test after changes |
| Forgetting registration | Add to tool registry/toolset |
| Wrong port | Check port mapping |
| Auth failures | Verify tokens |
| CORS issues | Add CORS headers in Go |

---

## Next Steps

- [troubleshooting.md](troubleshooting.md) - Common issues and solutions