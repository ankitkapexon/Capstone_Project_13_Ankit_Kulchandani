# Mobile Test Generator POC — Team Steering Document

## Purpose

This project is a proof-of-concept (POC) pipeline that automates two things:

1. **Screenshot → Screen Semantic Model (SSM):** A vision LLM analyses a mobile app screenshot and produces a structured JSON object describing the screen's name, purpose, and UI elements.
2. **SSM JSON → Manual Test Cases:** A language model reads the SSM JSON and generates human-readable manual test cases tailored to the screen's actual UI components.

The output is designed to accelerate mobile QA by reducing the time needed to draft manual test cases from scratch.

---

## Architecture at a Glance

```
artifacts/input_screenshots/
        │
        ▼  (Step 1 — vision LLM)
artifacts/ssm_json_output/          ← structured JSON per screen
        │
        ▼  (Step 2 — language LLM)
artifacts/manual_testcases/         ← plain-text test cases per screen
```

Both steps are **loosely coupled** — Step 2 only needs the JSON files from Step 1. You can re-run either step independently.

---

## Folder Structure

```
MobileTestGeneratorPOC/
├── agents/
│   ├── core/
│   │   ├── vision_agent.py         # Abstract base: VisionAgent
│   │   └── testcase_agent.py       # Abstract base: TestCaseAgent
│   ├── vision_agent.py             # Concrete: OpenAIVisionAgent, MockVisionAgent, factory
│   └── __init__.py
├── models/
│   └── ssm.py                      # Single Pydantic schema for ScreenSemanticModel
├── services/
│   ├── config.py                   # Loads .env into the environment
│   └── testcase_agent.py           # Concrete: OpenAITestCaseAgent, MockTestCaseAgent, factory
├── pipelines/
│   ├── ssm_generator.py            # Step 1 entry point — run this directly
│   └── testcase_generator.py       # Step 2 entry point — run this directly
├── prompts/
│   ├── vision_analysis.txt         # LLM prompt for Step 1 (edit to tune vision output)
│   └── test_generation.txt         # LLM prompt for Step 2 (edit to tune test case style)
├── artifacts/
│   ├── input_screenshots/          # DROP SCREENSHOTS HERE before running Step 1
│   ├── ssm_json_output/            # Step 1 writes here (auto-created)
│   └── manual_testcases/           # Step 2 writes here (auto-created)
├── tests/
│   └── test_ssm_model.py           # Unit tests — run before committing changes
├── scripts/
│   ├── setup_env.ps1               # Windows: creates .venv and installs deps
│   └── setup_env.sh                # macOS/Linux: creates .venv and installs deps
├── .venv/                          # Active virtual environment (Python 3.11)
├── .env                            # API keys — NEVER commit this file
├── requirements.txt                # Runtime dependencies
└── README.md                       # Quick-start guide
```

---

## How to Run

### Prerequisites
- Python 3.11 or 3.12 (3.14+ not recommended — see `requirements.txt`)
- An OpenAI-compatible API key OR use `mock` mode for offline testing

### 1 — Set up the environment (first time only)

**Windows:**
```powershell
.\scripts\setup_env.ps1 -PythonExe python
```
**macOS / Linux:**
```bash
bash scripts/setup_env.sh
```

### 2 — Configure `.env`

Copy `.env.example` (or create `.env`) with:
```dotenv
VISION_AGENT_PROVIDER=openai
TESTCASE_AGENT_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_BASE=https://api.openai.com/v1   # override for internal gateways
```

For offline / no-key testing:
```dotenv
VISION_AGENT_PROVIDER=mock
TESTCASE_AGENT_PROVIDER=mock
```

### 3 — Place screenshots

Drop your `.png` / `.jpg` / `.jpeg` / `.webp` / `.bmp` screenshots into:
```
artifacts/input_screenshots/
```

### 4 — Run Step 1 (screenshots → SSM JSON)

```powershell
python pipelines/ssm_generator.py artifacts/input_screenshots artifacts/ssm_json_output --clean
```

### 5 — Run Step 2 (SSM JSON → manual test cases)

```powershell
python pipelines/testcase_generator.py artifacts/ssm_json_output artifacts/manual_testcases --clean
```

### Full end-to-end (single command)

```powershell
python pipelines/ssm_generator.py artifacts/input_screenshots artifacts/ssm_json_output --clean ; python pipelines/testcase_generator.py artifacts/ssm_json_output artifacts/manual_testcases --clean
```

---

## How to Change the LLM Behaviour

All LLM instructions are externalised as plain text files. **No code changes needed.**

| File | Controls |
|---|---|
| `prompts/vision_analysis.txt` | How the vision model describes screens and elements |
| `prompts/test_generation.txt` | How the language model formats and writes test cases |

Edit either file, re-run the corresponding step, and compare outputs.

---

## How to Switch Providers

Set the environment variables before running:

| Variable | Values |
|---|---|
| `VISION_AGENT_PROVIDER` | `openai` \| `mock` |
| `TESTCASE_AGENT_PROVIDER` | `openai` \| `mock` |
| `OPENAI_MODEL` | Any chat-completion model name (e.g. `gpt-4o`, `gpt-4o-mini`) |
| `OPENAI_API_BASE` | Override the base URL for internal API gateways |

Adding a new provider (e.g. Azure, Anthropic) requires only:
1. Create a new class that extends `agents/core/vision_agent.py::VisionAgent` or `agents/core/testcase_agent.py::TestCaseAgent`
2. Register it in the `create_vision_agent()` / `create_testcase_agent()` factory function

---

## Data Model

The **Screen Semantic Model (SSM)** is the shared contract between Step 1 and Step 2.  
Schema is defined in `models/ssm.py`.

```json
{
  "screen_name": "Login",
  "screen_purpose": "Authenticate the user",
  "elements": [
    { "label": "Username", "type": "textfield", "actions": ["enter_text"] },
    { "label": "Password", "type": "textfield", "actions": ["enter_text"] },
    { "label": "Login",    "type": "button",    "actions": ["tap"] }
  ]
}
```

---

## Running Tests

```powershell
python -m unittest tests.test_ssm_model
```

Run this before merging any changes that touch `models/ssm.py` or `agents/vision_agent.py`.

---

## What is NOT in scope (yet)

| Capability | Status |
|---|---|
| Appium script generation | Planned — next phase |
| Reviewer agent (test case review) | Planned |
| Locator agent (UI element XPath/ID detection) | Planned |
| CI/CD integration | Not started |
| Multi-app / multi-platform support | Not started |

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| Single `models/ssm.py` schema | Eliminated 4 duplicate model files; one source of truth |
| Abstract base classes in `agents/core/` | Allows new LLM providers without changing pipeline code |
| Prompts as `.txt` files | QA / non-developer team members can tune output without touching Python |
| `--clean` flag on runners | Explicitly clears output before a run; safe for reruns |
| `mock` provider mode | Full pipeline runs offline for demos or CI without an API key |
| `.venv` (Python 3.11) as active env | Stable; all dependencies install cleanly; tested end to end |

---

## Contact / Ownership

Update this section with team contacts, Jira board links, and repo details before sharing.
