<div align="center">
  <img alt="OpenJarvis" src="assets/OpenJarvis_Horizontal_Logo.png" width="400">

  <p><i>Your daily Jarvis assistant, powered by 60db.</i></p>

  <p>
    <a href="https://arxiv.org/abs/2605.17172"><img src="https://img.shields.io/badge/arXiv-2605.17172-b31b1b.svg" alt="arXiv"></a>
    <a href="https://openjarvis.stanford.edu/"><img src="https://img.shields.io/badge/project-OpenJarvis-blue" alt="Project"></a>
    <a href="https://docs.60db.ai/introduction"><img src="https://img.shields.io/badge/API-60db-blue" alt="60db API documentation"></a>
    <img src="https://img.shields.io/badge/python-%3E%3D3.10-blue" alt="Python">
    <img src="https://img.shields.io/badge/license-Apache%202.0-green" alt="License">
    <a href="https://discord.gg/CMVBmDQ5Fj"><img src="https://img.shields.io/badge/discord-join-7289da?logo=discord&logoColor=white" alt="Discord"></a>
    <a href="https://x.com/OpenJarvisAI"><img src="https://img.shields.io/badge/X-@OpenJarvisAI-black?logo=x&logoColor=white" alt="X / Twitter"></a>
  </p>
</div>

---

[60db API documentation](https://docs.60db.ai/introduction) ·
[60db account and API keys](https://app.60db.ai)

## Jarvis with 60db

This checkout uses **60db** for chat (`60db-tiny`), speech recognition, speech
synthesis, and Judge. One API key and a selected voice are enough to get started.
Your conversations stay in Jarvis; chat requests disable
60db chat-history storage. Audio and prompts are sent to 60db for processing.

## Installation

Install [uv](https://docs.astral.sh/uv/), Python 3.10–3.13, Node.js 22.22 or
newer, and npm 11.19+ (11.x). Run from this checkout:

```bash
uv sync --extra server
uv run --extra server jarvis gui
```

Jarvis installs the frontend dependencies when needed and opens in your browser
at `http://127.0.0.1:5173` by default. Paste your 60db API key, click **Load voices**,
choose a voice, and click **Start using Jarvis**. The same key powers chat,
microphone input, spoken answers, and the **Judge answer** button. Change the
key or voice later in **Settings → 60db**. No local model downloads are needed.

The browser setup stores the key on this computer in an owner-only credentials
file; the native desktop build stores it in the operating system keyring.
The key is never saved in browser storage. Keep the local server on loopback,
or configure server authentication before exposing it remotely.

For the API contracts, see the [60db documentation](https://docs.60db.ai/introduction).
The source desktop build (`cd frontend && npm install && npm run tauri dev`)
has the same setup and requires the Tauri development prerequisites. Upstream
release downloads do not include these changes.

## Quick Start

```bash
uv run --extra server jarvis           # opens the key and voice setup
uv run --extra server jarvis ask "Plan my day"  # after setup
```

### Voice input and spoken replies

Use the microphone button to dictate through 60db and allow microphone access
when your browser asks. Choose **Read aloud** on an assistant reply to hear it
in your selected voice. Enable **Settings → Speech → Speak replies automatically**
to read each finished reply aloud.

TTS removes `**` bold markers before sending text to 60db. For example,
`**Hello**` is spoken as `Hello`; the displayed chat keeps its formatting.
This applies to read-aloud, automatic speech, CLI voice output, and the speech tool.

### Judge

**Judge answer** evaluates a reply against the preceding question and displays
its quality score. It runs only when clicked. Chat, transcription, speech
synthesis, and Judge use your 60db workspace balance.

### Dashboard

Open **Dashboard** in the sidebar or visit `/dashboard` on the running app.
The dashboard shows only:

- Requests
- Input tokens
- Output tokens
- A **View 60db billing** link

The counters show inference usage recorded by Jarvis. Check your 60db account
for actual charges and workspace-wide usage. The old `/comparison` URL now
redirects to `/dashboard`.

### Serve the built app at port 8123

To use `http://127.0.0.1:8123/dashboard` directly, build the frontend once and
serve it with the API:

```bash
cd frontend
npm install
npm run build
cd ..
uv run --extra server jarvis serve --host 127.0.0.1 --port 8123 --engine sixtydb --model 60db-tiny
```

Keep the server running while using Jarvis. Saved 60db settings are reused;
otherwise, the app opens the key and voice setup. After pulling UI changes,
rebuild the frontend and restart the server to apply route changes.

### Troubleshooting

- **Microphone unavailable:** allow microphone access for the local app and
  enable speech-to-text in **Settings → Speech**.
- **Spoken replies unavailable:** check the saved key and voice in
  **Settings → 60db** and enable text-to-speech in **Settings → Speech**.
- **Key or balance error:** check your API key and balance in your 60db account.
- **Old dashboard still visible:** rebuild the frontend, restart the server,
  and reload `/dashboard`.

### Skills

Skills teach agents how to better use tools and improve their reasoning. Every skill is a tool — agents discover them from a catalog and invoke them on demand.

```bash
# Install skills from public sources
jarvis skill install hermes:arxiv
jarvis skill sync hermes --category research

# Use skills with any agent
jarvis ask "Use the code-explainer skill to explain this Python code: for i in range(5): print(i*2)"

# Optimize skills from your trace history
jarvis optimize skills --policy dspy

# Benchmark the impact
jarvis bench skills --max-samples 5 --seeds 42
```

Import from [Hermes Agent](https://github.com/NousResearch/hermes-agent) (~150 skills), [OpenClaw](https://github.com/openclaw/skills) (~13,700 community skills), or any GitHub repo. Skills follow the [agentskills.io](https://agentskills.io/specification) open standard.

See the [Skills User Guide](https://open-jarvis.github.io/OpenJarvis/user-guide/skills/) and [Skills Tutorial](https://open-jarvis.github.io/OpenJarvis/tutorials/skills-workflow/) for details.

### Built-in Agents

OpenJarvis ships with eight built-in agents across three execution modes (on-demand, scheduled, continuous):

| Agent | Type | What it does |
|-------|------|-------------|
| `morning_digest` | Scheduled | Daily briefing from email, calendar, health, news — with TTS audio |
| `deep_research` | On-demand | Multi-hop research with citations across web and local docs |
| `monitor_operative` | Continuous | Long-horizon monitoring with memory, compression, and retrieval |
| `orchestrator` | On-demand | Multi-turn reasoning with automatic tool selection |
| `native_react` | On-demand | ReAct (Thought-Action-Observation) loop agent |
| `operative` | Continuous | Persistent autonomous agent with state management |
| `native_openhands` | On-demand | CodeAct — generates and executes Python code |
| `simple` | On-demand | Single-turn chat, no tools |

See the [User Guide](https://open-jarvis.github.io/OpenJarvis/user-guide/morning-digest/) and [Tutorials](https://open-jarvis.github.io/OpenJarvis/tutorials/) for detailed setup instructions.

The linked upstream guides cover general OpenJarvis features. For the AI API
used by this checkout, see the [60db documentation](https://docs.60db.ai/introduction).

## Community

- **GitHub:** [github.com/open-jarvis/OpenJarvis](https://github.com/open-jarvis/OpenJarvis)
- **Discord:** [discord.gg/CMVBmDQ5Fj](https://discord.gg/CMVBmDQ5Fj)
- **X / Twitter:** [@OpenJarvisAI](https://x.com/OpenJarvisAI)
- **Docs:** [open-jarvis.github.io/OpenJarvis](https://open-jarvis.github.io/OpenJarvis/)

## Contributing

We welcome contributions! See the [Contributing Guide](CONTRIBUTING.md) for incentives, contribution types, and the PR process.

From this checkout:

```bash
uv sync --extra dev --extra server
uv run pre-commit install
uv run pytest tests/ -v
```

Browse the [Roadmap](https://open-jarvis.github.io/OpenJarvis/development/roadmap/) for areas where help is needed. Comment **"take"** on any issue to get auto-assigned.

## About

OpenJarvis is part of [Intelligence Per Watt](https://www.intelligence-per-watt.ai/), a research initiative studying the intelligence efficiency of AI systems. The project is developed at [Hazy Research](https://hazyresearch.stanford.edu/) and the [Scaling Intelligence Lab](https://scalingintelligence.stanford.edu/) at [Stanford SAIL](https://ai.stanford.edu/).

## Citation

```bibtex
@misc{saadfalcon2026openjarvispersonalaipersonal,
      title={OpenJarvis: Personal AI, On Personal Devices}, 
      author={Jon Saad-Falcon and Avanika Narayan and Robby Manihani and Tanvir Bhathal and Herumb Shandilya and Hakki Orhun Akengin and Gabriel Bo and Andrew Park and Matthew Hart and Caia Costello and Chuan Li and Christopher Ré and Azalia Mirhoseini},
      year={2026},
      eprint={2605.17172},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/2605.17172}, 
}
```

## License

[Apache 2.0](LICENSE)
