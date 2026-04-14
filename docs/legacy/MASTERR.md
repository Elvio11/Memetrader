# MemeTrader — Master Documentation Reference

> **Generated**: 2026-04-12  
> **Total .md Files**: 651  
> **Purpose**: Complete reference guide to all documentation in the repository

---

## Table of Contents

1. [Overview](#1-overview)
2. [Root Level](#2-root-level)
3. [Core Docs](#3-core-docs)
4. [NOFX Documentation](#4-nofx-documentation)
5. [Hermes Website Docs](#5-hermes-website-docs)
6. [Optional Skills](#6-optional-skills)
7. [Memory Plugins](#7-memory-plugins)
8. [Built-in Skills](#8-built-in-skills)
9. [Release Notes](#9-release-notes)
10. [Archive Candidates](#10-archive-candidates)

---

## 1. Overview

### Repository Structure

| Directory | .md Count | Description |
|-----------|----------|-------------|
| `/` | 14 | Root level files |
| `/docs/` | 11 | Core documentation |
| `/nofx/docs/` | 77 | NOFX trading system docs |
| `/website/docs/` | 102 | Hermes website (Docusaurus) |
| `/optional-skills/` | 112 | Optional skill packages |
| `/plugins/memory/` | 8 | Memory plugin READMEs |
| `/skills/` | 284 | Built-in skills |
| Other | 43 | Plans, GitHub, packaging |

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MEMETRADER                             │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────┐  │
│  │   Hermes    │    │    NOFX     │    │  NOFX UI   │  │
│  │   Python   │───▶│     Go      │───▶│   React   │  │
│  │   Port 8643│    │   Port 8080 │    │  Port 3000│  │
│  └──────────────┘    └──────────────┘    └────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Root Level

**Location**: `/workspaces/Memetrader/`

| File | Description |
|------|-------------|
| [README.md](./README.md) | Main entry point — MemeTrader unified overview |
| [AGENTS.md](./AGENTS.md) | Development guide for AI coding assistants |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Contribution guidelines |
| [AUDIT.md](./AUDIT.md) | Engineering audit documentation |
| [TASKS.md](./TASKS.md) | Implementation task tracking |
| [UNIFICATION_PLAN.md](./UNIFICATION_PLAN.md) | Hermes + NOFX integration plan |
| [DECISION_paper_trading_migration.md](./DECISION_paper_trading_migration.md) | Paper trading migration decision |
| [RELEASE_v0.2.0.md](./RELEASE_v0.2.0.md) | v0.2.0 release notes |
| [RELEASE_v0.3.0.md](./RELEASE_v0.3.0.md) | v0.3.0 release notes |
| [RELEASE_v0.4.0.md](./RELEASE_v0.4.0.md) | v0.4.0 release notes |
| [RELEASE_v0.5.0.md](./RELEASE_v0.5.0.md) | v0.5.0 release notes |
| [RELEASE_v0.6.0.md](./RELEASE_v0.6.0.md) | v0.6.0 release notes |
| [RELEASE_v0.7.0.md](./RELEASE_v0.7.0.md) | v0.7.0 release notes |
| [RELEASE_v0.8.0.md](./RELEASE_v0.8.0.md) | v0.8.0 release notes (latest) |

---

## 3. Core Docs

**Location**: `/workspaces/Memetrader/docs/`

| File | Description |
|------|-------------|
| [overview.md](./docs/overview.md) | System overview — 3 projects summary |
| [getting-started.md](./docs/getting-started.md) | Installation and setup |
| [architecture.md](./docs/architecture.md) | System architecture diagrams |
| [cross-project-understanding.md](./docs/cross-project-understanding.md) | How the 3 projects integrate |
| [development-guide.md](./docs/development-guide.md) | How to develop new features |
| [troubleshooting.md](./docs/troubleshooting.md) | Common issues and solutions |
| [cleanup-refactoring-guidance.md](./docs/cleanup-refactoring-guidance.md) | Cleanup actions |
| [honcho-integration-spec.md](./docs/honcho-integration-spec.md) | Honcho memory spec |
| [migration/openclaw.md](./docs/migration/openclaw.md) | OpenClaw migration |
| [acp-setup.md](./docs/acp-setup.md) | ACP server setup |
| [plans/2026-03-16-pricing-accuracy-architecture-design.md](./docs/plans/2026-03-16-pricing-accuracy-architecture-design.md) | Pricing architecture design |

---

## 4. NOFX Documentation

**Location**: `/workspaces/Memetrader/nofx/docs/`

### Architecture

| File | Description |
|------|-------------|
| [architecture/README.md](../nofx/docs/architecture/README.md) | NOFX architecture overview |
| [architecture/README.zh-CN.md](../nofx/docs/architecture/README.zh-CN.md) | Architecture (Chinese) |
| [architecture/STRATEGY_MODULE.md](../nofx/docs/architecture/STRATEGY_MODULE.md) | Strategy module — coin selection → AI → execution |
| [architecture/STRATEGY_MODULE.zh-CN.md](../nofx/docs/architecture/STRATEGY_MODULE.zh-CN.md) | Strategy (Chinese) |
| [architecture/X402_STREAMING_PAYMENT.md](../nofx/docs/architecture/X402_STREAMING_PAYMENT.md) | x402 streaming payments |

### API Reference

| File | Description |
|------|-------------|
| [api/API_REFERENCE.md](../nofx/docs/api/API_REFERENCE.md) | External API docs |

### Getting Started & Guides

| File | Description |
|------|-------------|
| [getting-started/README.md](../nofx/docs/getting-started/README.md) | Deployment guide |
| [getting-started/README.zh-CN.md](../nofx/docs/getting-started/README.zh-CN.md) | Getting started (Chinese) |
| [guides/README.md](../nofx/docs/guides/README.md) | User guides |
| [guides/README.zh-CN.md](../nofx/docs/guides/README.zh-CN.md) | Guides (Chinese) |

### Community

| File | Description |
|------|-------------|
| [community/README.md](../nofx/docs/community/README.md) | Community info |
| [community/MIGRATION_ANNOUNCEMENT.md](../nofx/docs/community/MIGRATION_ANNOUNCEMENT.md) | Migration announcement |
| [community/OFFICIAL_ACCOUNTS.md](../nofx/docs/community/OFFICIAL_ACCOUNTS.md) | Official accounts |
| [community/bounty-hyperliquid.md](../nofx/docs/community/bounty-hyperliquid.md) | Hyperliquid bounty |

### i18n (Internationalization)

| File | Description |
|------|-------------|
| [i18n/README.md](../nofx/docs/i18n/README.md) | Translation guidelines |
| [i18n/zh-CN/README.md](../nofx/docs/i18n/zh-CN/README.md) | Chinese translations |
| [i18n/ja/README.md](../nofx/docs/i18n/ja/README.md) | Japanese translations |
| [i18n/ko/README.md](../nofx/docs/i18n/ko/README.md) | Korean translations |
| [i18n/ru/README.md](../nofx/docs/i18n/ru/README.md) | Russian translations |
| [i18n/uk/README.md](../nofx/docs/i18n/uk/README.md) | Ukrainian translations |
| [i18n/vi/README.md](../nofx/docs/i18n/vi/README.md) | Vietnamese translations |

### Roadmap & Maintainers

| File | Description |
|------|-------------|
| [roadmap/README.md](../nofx/docs/roadmap/README.md) | Product roadmap |
| [roadmap/README.zh-CN.md](../nofx/docs/roadmap/README.zh-CN.md) | Roadmap (Chinese) |
| [maintainers/README.md](../nofx/docs/maintainers/README.md) | Maintainer info |
| [maintainers/README.zh-CN.md](../nofx/docs/maintainers/README.zh-CN.md) | Maintainers (Chinese) |

### Research & Misc

| File | Description |
|------|-------------|
| [research/AI-Trader-Analysis-Report.md](../nofx/docs/research/AI-Trader-Analysis-Report.md) | HKUDS AI Trader report |
| [pnl.md](../nofx/docs/pnl.md) | PNL calculation design |
| [market-regime-classification-en.md](../nofx/docs/market-regime-classification-en.md) | Market regime classification |

### NOFX Root Files

**Location**: `/workspaces/Memetrader/nofx/`

| File | Description |
|------|-------------|
| [nofx/README.md](../nofx/README.md) | NOFX main README |
| [nofx/README.ja.md](../nofx/README.ja.md) | NOFX README (Japanese) |
| [nofx/CHANGELOG.md](../nofx/CHANGELOG.md) | Changelog |
| [nofx/CHANGELOG.zh-CN.md](../nofx/CHANGELOG.zh-CN.md) | Changelog (Chinese) |
| [nofx/CONTRIBUTING.md](../nofx/CONTRIBUTING.md) | NOFX contributing |
| [nofx/DISCLAIMER.md](../nofx/DISCLAIMER.md) | Risk disclaimer |
| [nofx/SECURITY.md](../nofx/SECURITY.md) | Security policy |
| [nofx/CODE_OF_CONDUCT.md](../nofx/CODE_OF_CONDUCT.md) | Code of conduct |
| [nofx/ENCRYPTION_README.md](../nofx/ENCRYPTION_README.md) | Encryption info |

---

## 5. Hermes Website Docs

**Location**: `/workspaces/Memetrader/website/docs/`

### Getting Started (5 files)

| File | Description |
|------|-------------|
| [getting-started/installation.md](../website/docs/getting-started/installation.md) | Install guide |
| [getting-started/quickstart.md](../website/docs/getting-started/quickstart.md) | 2-minute tutorial |
| [getting-started/learning-path.md](../website/docs/getting-started/learning-path.md) | Learning path |
| [getting-started/nix-setup.md](../website/docs/getting-started/nix-setup.md) | Nix setup |
| [getting-started/updating.md](../website/docs/getting-started/updating.md) | Update guide |

### User Guide (53 files)

#### Features (20 files)

| File | Description |
|------|-------------|
| [user-guide/features/overview.md](../website/docs/user-guide/features/overview.md) | All features |
| [user-guide/features/tools.md](../website/docs/user-guide/features/tools.md) | 40+ tools |
| [user-guide/features/skills.md](../website/docs/user-guide/features/skills.md) | Skills system |
| [user-guide/features/memory.md](../website/docs/user-guide/features/memory.md) | Persistent memory |
| [user-guide/features/mcp.md](../website/docs/user-guide/features/mcp.md) | MCP integration |
| [user-guide/features/cron.md](../website/docs/user-guide/features/cron.md) | Cron scheduling |
| [user-guide/features/voice-mode.md](../website/docs/user-guide/features/voice-mode.md) | Voice mode |
| [user-guide/features/vision.md](../website/docs/user-guide/features/vision.md) | Vision analysis |
| [user-guide/features/tts.md](../website/docs/user-guide/features/tts.md) | Text-to-speech |
| [user-guide/features/image-generation.md](../website/docs/user-guide/features/image-generation.md) | Image generation |
| [user-guide/features/browser.md](../website/docs/user-guide/features/browser.md) | Browser automation |
| [user-guide/features/code-execution.md](../website/docs/user-guide/features/code-execution.md) | Code execution |
| [user-guide/features/delegation.md](../website/docs/user-guide/features/delegation.md) | Subagent delegation |
| [user-guide/features/batch-processing.md](../website/docs/user-guide/features/batch-processing.md) | Batch processing |
| [user-guide/features/acp.md](../website/docs/user-guide/features/acp.md) | ACP adapter |
| [user-guide/features/api-server.md](../website/docs/user-guide/features/api-server.md) | FastAPI server |
| [user-guide/features/provider-routing.md](../website/docs/user-guide/features/provider-routing.md) | Provider routing |
| [user-guide/features/fallback-providers.md](../website/docs/user-guide/features/fallback-providers.md) | Fallback providers |
| [user-guide/features/personality.md](../website/docs/user-guide/features/personality.md) | Personality/SOUL.md |
| [user-guide/features/context-files.md](../website/docs/user-guide/features/context-files.md) | Context files |

#### Configuration & Security

| File | Description |
|------|-------------|
| [user-guide/configuration.md](../website/docs/user-guide/configuration.md) | 1100-line config ref |
| [user-guide/security.md](../website/docs/user-guide/security.md) | Security model |
| [user-guide/profiles.md](../website/docs/user-guide/profiles.md) | Multi-profile support |
| [user-guide/sessions.md](../website/docs/user-guide/sessions.md) | Session management |
| [user-guide/cli.md](../website/docs/user-guide/cli.md) | CLI usage |
| [user-guide/docker.md](../website/docs/user-guide/docker.md) | Docker deployment |

#### Messaging (15 platforms)

| File | Description |
|------|-------------|
| [user-guide/messaging/index.md](../website/docs/user-guide/messaging/index.md) | Gateway overview |
| [user-guide/messaging/telegram.md](../website/docs/user-guide/messaging/telegram.md) | Telegram bot |
| [user-guide/messaging/discord.md](../website/docs/user-guide/messaging/discord.md) | Discord bot |
| [user-guide/messaging/slack.md](../website/docs/user-guide/messaging/slack.md) | Slack bot |
| [user-guide/messaging/whatsapp.md](../website/docs/user-guide/messaging/whatsapp.md) | WhatsApp |
| [user-guide/messaging/signal.md](../website/docs/user-guide/messaging/signal.md) | Signal |
| [user-guide/messaging/email.md](../website/docs/user-guide/messaging/email.md) | Email |
| [user-guide/messaging/sms.md](../website/docs/user-guide/messaging/sms.md) | SMS |
| [user-guide/messaging/homeassistant.md](../website/docs/user-guide/messaging/homeassistant.md) | Home Assistant |
| [user-guide/messaging/mattermost.md](../website/docs/user-guide/messaging/mattermost.md) | Mattermost |
| [user-guide/messaging/matrix.md](../website/docs/user-guide/messaging/matrix.md) | Matrix |
| [user-guide/messaging/dingtalk.md](../website/docs/user-guide/messaging/dingtalk.md) | DingTalk |
| [user-guide/messaging/feishu.md](../website/docs/user-guide/messaging/feishu.md) | Feishu |
| [user-guide/messaging/wecom.md](../website/docs/user-guide/messaging/wecom.md) | WeCom |
| [user-guide/messaging/webhooks.md](../website/docs/user-guide/messaging/webhooks.md) | Webhooks |

#### Other Features

| File | Description |
|------|-------------|
| [user-guide/features/memory-providers.md](../website/docs/user-guide/features/memory-providers.md) | Memory providers |
| [user-guide/features/skills/godmode.md](../website/docs/user-guide/features/skills/godmode.md) | Godmode skill |
| [user-guide/features/hooks.md](../website/docs/user-guide/features/hooks.md) | Pre/post hooks |
| [user-guide/features/plugins.md](../website/docs/user-guide/features/plugins.md) | Plugin system |
| [user-guide/features/context-references.md](../website/docs/user-guide/features/context-references.md) | Context refs |
| [user-guide/features/credential-pools.md](../website/docs/user-guide/features/credential-pools.md) | Credential pools |
| [user-guide/features/rl-training.md](../website/docs/user-guide/features/rl-training.md) | RL training |
| [user-guide/features/skins.md](../website/docs/user-guide/features/skins.md) | CLI skins |
| [user-guide/features/honcho.md](../website/docs/user-guide/features/honcho.md) | Honcho integration |
| [user-guide/git-worktrees.md](../website/docs/user-guide/git-worktrees.md) | Git worktrees |
| [user-guide/checkpoints-and-rollback.md](../website/docs/user-guide/checkpoints-and-rollback.md) | Checkpoint/rollback |

### Reference (10 files)

| File | Description |
|------|-------------|
| [reference/cli-commands.md](../website/docs/reference/cli-commands.md) | CLI commands |
| [reference/toolsets-reference.md](../website/docs/reference/toolsets-reference.md) | 20+ toolsets |
| [reference/slash-commands.md](../website/docs/reference/slash-commands.md) | Slash commands |
| [reference/tools-reference.md](../website/docs/reference/tools-reference.md) | Tool reference |
| [reference/environment-variables.md](../website/docs/reference/environment-variables.md) | 130+ env vars |
| [reference/faq.md](../website/docs/reference/faq.md) | FAQ |
| [reference/profile-commands.md](../website/docs/reference/profile-commands.md) | Profile commands |
| [reference/mcp-config-reference.md](../website/docs/reference/mcp-config-reference.md) | MCP config |
| [reference/optional-skills-catalog.md](../website/docs/reference/optional-skills-catalog.md) | Optional skills |
| [reference/skills-catalog.md](../website/docs/reference/skills-catalog.md) | Skills catalog |

### Guides (13 files)

| File | Description |
|------|-------------|
| [guides/tips.md](../website/docs/guides/tips.md) | Best practices |
| [guides/delegation-patterns.md](../website/docs/guides/delegation-patterns.md) | Delegation patterns |
| [guides/build-a-hermes-plugin.md](../website/docs/guides/build-a-hermes-plugin.md) | Plugin tutorial |
| [guides/python-library.md](../website/docs/guides/python-library.md) | Python lib |
| [guides/use-mcp-with-hermes.md](../website/docs/guides/use-mcp-with-hermes.md) | MCP guide |
| [guides/use-voice-mode-with-hermes.md](../website/docs/guides/use-voice-mode-with-hermes.md) | Voice guide |
| [guides/use-soul-with-hermes.md](../website/docs/guides/use-soul-with-hermes.md) | SOUL.md guide |
| [guides/work-with-skills.md](../website/docs/guides/work-with-skills.md) | Skills guide |
| [guides/migrate-from-openclaw.md](../website/docs/guides/migrate-from-openclaw.md) | Migration |
| [guides/automate-with-cron.md](../website/docs/guides/automate-with-cron.md) | Cron automation |
| [guides/daily-briefing-bot.md](../website/docs/guides/daily-briefing-bot.md) | Briefing bot |
| [guides/team-telegram-assistant.md](../website/docs/guides/team-telegram-assistant.md) | Team assistant |
| [guides/local-llm-on-mac.md](../website/docs/guides/local-llm-on-mac.md) | Local LLM |

### Integrations (2 files)

| File | Description |
|------|-------------|
| [integrations/index.md](../website/docs/integrations/index.md) | Integrations |
| [integrations/providers.md](../website/docs/integrations/providers.md) | LLM providers |

### Developer Guide (18 files)

| File | Description |
|------|-------------|
| [developer-guide/architecture.md](../website/docs/developer-guide/architecture.md) | Architecture |
| [developer-guide/contributing.md](../website/docs/developer-guide/contributing.md) | Contributing |
| [developer-guide/code-style.md](../website/docs/developer-guide/code-style.md) | Code style |
| [developer-guide/testing.md](../website/docs/developer-guide/testing.md) | Testing |
| [developer-guide/documentation.md](../website/docs/developer-guide/documentation.md) | Docs guide |
| [developer-guide/security.md](../website/docs/developer-guide/security.md) | Security |
| [developer-guide/deployment.md](../website/docs/developer-guide/deployment.md) | Deployment |
| [developer-guide/updating.md](../website/docs/developer-guide/updating.md) | Updating |
| [developer-guide/mcp-server.md](../website/docs/developer-guide/mcp-server.md) | MCP server |
| [developer-guide/prompting.md](../website/docs/developer-guide/prompting.md) | Prompting |
| [developer-guide/trajectory.md](../website/docs/developer-guide/trajectory.md) | Trajectory format |
| [developer-guide/rl-training.md](../website/docs/developer-guide/rl-training.md) | RL training |
| [developer-guide/honcho-integration.md](../website/docs/developer-guide/honcho-integration.md) | Honcho |
| [developer-guide/session-format.md](../website/docs/developer-guide/session-format.md) | Session format |
| [developer-guide/memory-providers.md](../website/docs/developer-guide/memory-providers.md) | Memory providers |
| [developer-guide/skills.md](../website/docs/developer-guide/skills.md) | Skills |
| [developer-guide/gateway.md](../website/docs/developer-guide/gateway.md) | Gateway |
| [developer-guide/provider-routing.md](../website/docs/developer-guide/provider-routing.md) | Provider routing |

---

## 6. Optional Skills

**Location**: `/workspaces/Memetrader/optional-skills/`

### By Category (112 files)

#### Creative (4 skills)

| File | Description |
|------|-------------|
| [creative/blender-mcp/SKILL.md](../optional-skills/creative/blender-mcp/SKILL.md) | Blender MCP |
| [creative/meme-generation/SKILL.md](../optional-skills/creative/meme-generation/SKILL.md) | Meme generation |
| [creative/meme-generation/EXAMPLES.md](../optional-skills/creative/meme-generation/EXAMPLES.md) | Meme examples |
| [creative/p5js/SKILL.md](../optional-skills/creative/p5js/SKILL.md) | p5.js |

#### MLOps (30+ skills)

| File | Description |
|------|-------------|
| [mlops/llava/SKILL.md](../optional-skills/mlops/llava/SKILL.md) | LLaVA vision-language |
| [mlops/pytorch-lightning/SKILL.md](../optional-skills/mlops/pytorch-lightning/SKILL.md) | PyTorch Lightning |
| [mlops/flash-attention/SKILL.md](../optional-skills/mlops/flash-attention/SKILL.md) | Flash attention |
| [mlops/qdrant/SKILL.md](../optional-skills/mlops/qdrant/SKILL.md) | Qdrant vector DB |
| [mlops/chroma/SKILL.md](../optional-skills/mlops/chroma/SKILL.md) | Chroma vector DB |
| [mlops/pinecone/SKILL.md](../optional-skills/mlops/pinecone/SKILL.md) | Pinecone |
| [mlops/huggingface-tokenizers/SKILL.md](../optional-skills/mlops/huggingface-tokenizers/SKILL.md) | HF tokenizers |
| [mlops/nemo-curator/SKILL.md](../optional-skills/mlops/nemo-curator/SKILL.md) | NeMo Curator |
| [mlops/instructor/SKILL.md](../optional-skills/mlops/instructor/SKILL.md) | Instructor |
| [mlops/saelens/SKILL.md](../optional-skills/mlops/saelens/SKILL.md) | Saelens |
| [mlops/accelerate/SKILL.md](../optional-skills/mlops/accelerate/SKILL.md) | Accelerate |
| [mlops/simpo/SKILL.md](../optional-skills/mlops/simpo/SKILL.md) | SimPO |
| [mlops/torchtitan/SKILL.md](../optional-skills/mlops/torchtitan/SKILL.md) | TorchTitan |
| [mlops/tensorrt-llm/SKILL.md](../optional-skills/mlops/tensorrt-llm/SKILL.md) | TensorRT-LLM |
| [mlops/lambda-labs/SKILL.md](../optional-skills/mlops/lambda-labs/SKILL.md) | Lambda Labs |
| [mlops/hermes-atropos-environments/SKILL.md](../optional-skills/mlops/hermes-atropos-environments/SKILL.md) | Atropos Envs |
| [mlops/faiss/SKILL.md](../optional-skills/mlops/faiss/SKILL.md) | FAISS |
| [mlops/slime/SKILL.md](../optional-skills/mlops/slime/SKILL.md) | SLIME |
| [mlops/instructor/references/](../optional-skills/mlops/instructor/references/) | Full refs |

#### Research (8 skills)

| File | Description |
|------|-------------|
| [research/bioinformatics/SKILL.md](../optional-skills/research/bioinformatics/SKILL.md) | Bioinformatics |
| [research/scrapling/SKILL.md](../optional-skills/research/scrapling/SKILL.md) | Scrapling |
| [research/duckduckgo-search/SKILL.md](../optional-skills/research/duckduckgo-search/SKILL.md) | DuckDuckGo |
| [research/domain-intel/SKILL.md](../optional-skills/research/domain-intel/SKILL.md) | Domain intel |
| [research/parallel-cli/SKILL.md](../optional-skills/research/parallel-cli/SKILL.md) | Parallel CLI |
| [research/qmd/SKILL.md](../optional-skills/research/qmd/SKILL.md) | QMD |
| [research/gitnexus-explorer/SKILL.md](../optional-skills/research/gitnexus-explorer/SKILL.md) | GitNexus |

#### Security (4 skills)

| File | Description |
|------|-------------|
| [security/1password/SKILL.md](../optional-skills/security/1password/SKILL.md) | 1Password |
| [security/sherlock/SKILL.md](../optional-skills/security/sherlock/SKILL.md) | Sherlock |
| [security/oss-forensics/SKILL.md](../optional-skills/security/oss-forensics/SKILL.md) | OSS forensics |

#### DevOps (2 skills)

| File | Description |
|------|-------------|
| [devops/cli/SKILL.md](../optional-skills/devops/cli/SKILL.md) | DevOps CLI |
| [devops/docker-management/SKILL.md](../optional-skills/devops/docker-management/SKILL.md) | Docker mgmt |

#### Blockchain (2 skills)

| File | Description |
|------|-------------|
| [blockchain/solana/SKILL.md](../optional-skills/blockchain/solana/SKILL.md) | Solana |
| [blockchain/base/SKILL.md](../optional-skills/blockchain/base/SKILL.md) | Base |

#### Other Categories

| File | Description |
|------|-------------|
| [autonomous-ai-agents/honcho/SKILL.md](../optional-skills/autonomous-ai-agents/honcho/SKILL.md) | Honcho |
| [autonomous-ai-agents/blackbox/SKILL.md](../optional-skills/autonomous-ai-agents/blackbox/SKILL.md) | Blackbox |
| [email/agentmail/SKILL.md](../optional-skills/email/agentmail/SKILL.md) | AgentMail |
| [productivity/siyuan/SKILL.md](../optional-skills/productivity/siyuan/SKILL.md) | Siyuan |
| [productivity/memento-flashcards/SKILL.md](../optional-skills/productivity/memento-flashcards/SKILL.md) | Flashcards |
| [productivity/telephony/SKILL.md](../optional-skills/productivity/telephony/SKILL.md) | Telephony |
| [productivity/canvas/SKILL.md](../optional-skills/productivity/canvas/SKILL.md) | Canvas |
| [health/neuroskill-bci/SKILL.md](../optional-skills/health/neuroskill-bci/SKILL.md) | NeuroSkill BCI |
| [communication/one-three-one-rule/SKILL.md](../optional-skills/communication/one-three-one-rule/SKILL.md) | 1:1:1 rule |
| [mcp/fastmcp/SKILL.md](../optional-skills/mcp/fastmcp/SKILL.md) | FastMCP |
| [migration/openclaw-migration/SKILL.md](../optional-skills/migration/openclaw-migration/SKILL.md) | OpenClaw migrate |

---

## 7. Memory Plugins

**Location**: `/workspaces/Memetrader/plugins/memory/`

| File | Description |
|------|-------------|
| [honcho/README.md](../plugins/memory/honcho/README.md) | Dialectic Q&A, semantic search |
| [mem0/README.md](../plugins/memory/mem0/README.md) | Server-side LLM extraction |
| [supermemory/README.md](../plugins/memory/supermemory/README.md) | Semantic long-term memory |
| [holographic/README.md](../plugins/memory/holographic/README.md) | Holographic |
| [hindsight/README.md](../plugins/memory/hindsight/README.md) | Hindsight |
| [retaindb/README.md](../plugins/memory/retaindb/README.md) | RetainDB |
| [openviking/README.md](../plugins/memory/openviking/README.md) | OpenViking |
| [byterover/README.md](../plugins/memory/byterover/README.md) | ByteRover |

---

## 8. Built-in Skills

**Location**: `/workspaces/Memetrader/skills/`

284 skills in categories:
- research/
- creative/
- mlops/
- productivity/
- devops/
- autonomous-ai-agents/
- and more...

*(Full list available via `hermes skills browse`)*

---

## 9. Release Notes

| Version | Date | Highlights |
|---------|------|-----------|
| [RELEASE_v0.8.0.md](./RELEASE_v0.8.0.md) | 2026-04-08 — Intelligence release |
| [RELEASE_v0.7.0.md](./RELEASE_v0.7.0.md) | Pluggable memory, credential pools |
| [RELEASE_v0.6.0.md](./RELEASE_v0.6.0.md) | Profiles, MCP server mode |
| [RELEASE_v0.5.0.md](./RELEASE_v0.5.0.md) | Docker, fallback providers |
| [RELEASE_v0.4.0.md](./RELEASE_v0.4.0.md) | Gateway expansion |
| [RELEASE_v0.3.0.md](./RELEASE_v0.3.0.md) | Skills system |
| [RELEASE_v0.2.0.md](./RELEASE_v0.2.0.md) | MCP integration |

---

## 10. Archive Candidates

Files identified for potential archival (duplicate, outdated, or unneeded):

### Duplicates
- `.plans/` → 2 files (plans moved to `docs/plans/`)
- `.github/PULL_REQUEST_TEMPLATE/` → Can use default

### Outdated
- Old release notes (v0.2–v0.5) → Keep latest 3 only

### Unneeded Build Artifacts
- `__pycache__/` directories (not .md but noted)
- `*.egg-info/` directories

---

## Quick Reference

### Port Mapping

| Service | Port | Purpose |
|---------|------|---------|
| Hermes FastAPI | 8643 | AI chat, sessions |
| Hermes Gateway | 8642 | Messaging platforms |
| NOFX Go | 8080 | Trading execution |
| NOFX UI | 3000 | Dashboard |

### Key Commands

```bash
hermes              # Start CLI
hermes model        # Switch LLM
hermes tools        # Configure tools
hermes gateway     # Messaging

# NOFX
cd nofx && go run main.go
cd nofx-ui && npm run dev
```

---

*End of Master Reference*