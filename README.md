# WaspWatch 🐝

**Production WASP benchmark Green Agent for AgentBeats competition.** Evaluates web agents against prompt injection attacks using official Meta FAIR WASP benchmark.

## Features

- 🐛 **Official WASP** - facebookresearch/wasp integration
- 📊 **3 Metrics** - `asr_intermediate`, `asr_end_to_end`, `utility`
- 🐳 **Docker** - Playwright + VisualWebArena + multi-platform
- 🔄 **Fallback** - CPU-only rendering (AgentBeats compatible)
- ⚡ **FastAPI** - `/health`, `/assess`, `/webhook` endpoints
- 🏆 **4 Leaderboard Queries** - Custom AgentBeats rankings

## Quick Start

```bash
# Run
podman run -d -p 8000:8000 ghcr.io/craftofknowing/waspwatch:latest

# Health check
curl http://localhost:8000/health

# Assess purple agent
curl -X POST http://localhost:8000/assess \
  -H "Content-Type: application/json" \
  -d '{"purple":{"image":"your-agent:latest"}}'
```

## AgentBeats Registration

```
Image: ghcr.io/craftofknowing/waspwatch:latest
Health: /health
Assess: /assess
Metrics: asr_intermediate,asr_end_to_end,utility
Repo: https://github.com/craftofknowing/waspwatch-agent
```

**Leaderboard Queries:**
```json
[
  {"name":"Attack Success Rate","query":"SELECT avg(asr_intermediate) as asr FROM results WHERE agent_type='green' ORDER BY asr DESC"},
  {"name":"End-to-End Compromise","query":"SELECT avg(asr_end_to_end) as asr_e2e FROM results ORDER BY asr_e2e DESC"},
  {"name":"Utility Score","query":"SELECT avg(utility) as util FROM results ORDER BY util DESC"},
  {"name":"Overall WaspWatch","query":"SELECT id, (asr_intermediate + asr_end_to_end + utility)/3 as score FROM results ORDER BY score DESC"}
]
```

## Architecture

```
Purple Agent → POST /assess → WaspWatch
                        ↓
                 VisualWebArena + WASP
                        ↓
GitLab/Reddit Tasks ← Prompt Injections ← Metrics JSON
                        ↓
                   AgentBeats Leaderboard 🥇
```

## Local Development

```bash
git clone https://github.com/craftofknowing/waspwatch-agent
cd waspwatch-agent
podman build -t waspwatch:local .
podman run -d -p 8000:8000 waspwatch:local

# Test suite
curl http://localhost:8000/health
curl -X POST http://localhost:8000/webhook \
  -d '{"query":"SELECT avg(asr_intermediate) FROM results"}'
```

## Production Deployment

**GHCR:** [ghcr.io/craftofknowing/waspwatch](https://github.com/craftofknowing/waspwatch-agent/pkgs/container/waspwatch)

```bash
podman run -d --gpus all -p 8000:8000 ghcr.io/craftofknowing/waspwatch:latest
```

## Webhook Integration

**GitHub → AgentBeats auto-validation:**

```
1. agentbeats.dev → Copy webhook URL
2. Repo → Settings → Webhooks → Add webhook
3. Payload URL: [AgentBeats webhook URL]
4. Content-Type: application/json
5. Events: Pushes ✓
```

## Leaderboard Metrics

| Metric | Description | Higher = Better |
|--------|-------------|-----------------|
| `asr_intermediate` | Hijack detection rate | 🥇 |
| `asr_end_to_end` | Full compromise detection | 🥇 |
| `utility` | Benign task success | 🥇 |

## Credits

- [WASP Benchmark](https://github.com/facebookresearch/wasp) - Meta FAIR
- [VisualWebArena](https://github.com/web-arena-x/visualwebarena)
- [AgentBeats](https://agentbeats.dev) - Berkeley RDI
- Playwright - Browser automation

## License

[MIT License](LICENSE) © 2026 craftofknowing

***

**Built for AgentBeats Green Agent Track → Targeting #1 🏆**  
`ghcr.io/craftofknowing/waspwatch:v1.0.6` → Ready for judging!
