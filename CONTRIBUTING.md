# Mobile Test Generator POC — Team Steering Document

## Purpose

This project is a proof-of-concept (POC) pipeline that automates three things:

1. **Screenshot → Screen Semantic Model (SSM):** A vision LLM analyses a mobile app screenshot and produces a structured JSON object describing the screen's name, purpose, and UI elements.
2. **SSM JSON → Manual Test Cases:** A language model reads the SSM JSON and generates human-readable manual test cases tailored to the screen's actual UI components.
3. **SSM JSON + Manual Test Cases → Appium Page Object Model:** An LLM-backed agent turns the manual test cases into a runnable Android (UiAutomator2) Appium Page Object + pytest test module pair per screen.

The output is designed to accelerate mobile QA by reducing the time needed to draft manual test cases and automation scripts from scratch.

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
        │
        ▼  (Step 3 — LangChain tool-calling agent)
artifacts/appium_scripts/           ← pages/<screen>_page.py + tests/test_<screen>.py per screen,
                                       plus static conftest.py + core/base_page.py
```

Each step is **loosely coupled** — Step 2 only needs the JSON files from Step 1, and Step 3 only needs the JSON from Step 1 plus the text files from Step 2. You can re-run any step independently given its inputs on disk.

The full target architecture (per the project brief) is:

```
Screenshot → Vision Agent → SSM → Test Case Generation Agent → Appium Script Generator Agent
    → Reviewer Agent → Locator Enrichment Agent → Execution Agent
```

This repo currently implements Vision Agent, Test Case Generation Agent, and the **Appium Script
Generator Agent**. Reviewer, Locator Enrichment, and Execution agents are planned next.

---

## Folder Structure

```
MobileTestGeneratorPOC/
├── agents/
│   ├── core/
│   │   ├── vision_agent.py         # Abstract base: VisionAgent
│   │   ├── testcase_agent.py       # Abstract base: TestCaseAgent
│   │   └── appium_agent.py         # Abstract base: AppiumScriptAgent
│   ├── vision_agent.py             # Concrete: OpenAIVisionAgent, MockVisionAgent, factory
│   └── __init__.py
├── models/
│   └── ssm.py                      # Single Pydantic schema for ScreenSemanticModel
├── services/
│   ├── config.py                   # Loads .env into the environment
│   ├── testcase_agent.py           # Concrete: OpenAITestCaseAgent, MockTestCaseAgent, factory
│   └── appium_agent.py             # Concrete: OpenAIAppiumScriptAgent, MockAppiumScriptAgent, factory
├── pipelines/
│   ├── ssm_generator.py            # Step 1 entry point — run this directly
│   ├── testcase_generator.py       # Step 2 entry point — run this directly
│   ├── appium_script_generator.py  # Step 3 entry point — run this directly
│   └── templates/
│       ├── appium_conftest.py      # Static driver fixture template (Android), copied into artifacts/appium_scripts/
│       └── appium_base_page.py     # Static BasePage template, copied into artifacts/appium_scripts/core/
├── prompts/
│   ├── vision_analysis.txt         # LLM prompt for Step 1 (edit to tune vision output)
│   ├── test_generation.txt         # LLM prompt for Step 2 (edit to tune test case style)
│   ├── appium_script_generation.txt # LLM prompt for Step 3 (edit to tune the POM contract/style)
│   ├── review_prompt.txt           # Stub for the planned Reviewer agent
│   └── locator_prompt.txt          # Stub for the planned Locator Enrichment agent
├── artifacts/
│   ├── input_screenshots/          # DROP SCREENSHOTS HERE before running Step 1
│   ├── ssm_json_output/            # Step 1 writes here (auto-created)
│   ├── manual_testcases/           # Step 2 writes here (auto-created)
│   └── appium_scripts/             # Step 3 writes here (auto-created), see layout below
├── demo_mobile_apps/
│   ├── mda-2.2.0-25.apk            # Android demo app used by ANDROID_APP_PATH
│   └── SauceLabs-Demo-App.ipa      # iOS demo app, reserved for when iOS support is added
├── tests/
│   ├── test_ssm_model.py           # Unit tests — run before committing changes
│   └── test_appium_agent.py        # Unit tests for the Appium Script Generator Agent
├── scripts/
│   ├── setup_env.ps1               # Windows: creates .venv and installs deps
│   └── setup_env.sh                # macOS/Linux: creates .venv and installs deps
├── .venv/                          # Active virtual environment (Python 3.11/3.12)
├── .env                            # API keys — NEVER commit this file
├── requirements.txt                # Runtime dependencies
└── README.md                       # Quick-start guide
```

Step 3's output layout (`artifacts/appium_scripts/`, per screen):

```
artifacts/appium_scripts/
├── conftest.py              # driver fixture - static, Android only, iOS raises NotImplementedError
├── core/
│   └── base_page.py         # BasePage: waitForVisible/click/typeText/isVisible/getText - static
├── pages/
│   └── login_page.py        # class LoginPage(BasePage) - LOCATORS dict + camelCase action methods
└── tests/
    └── test_login.py        # thin test flow: only calls loginPage.<method>(), asserts on results
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
APPIUM_AGENT_PROVIDER=openai
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_BASE=https://api.openai.com/v1   # override for internal gateways

# Step 3 (Appium script generation / execution) only - Android is the current focus.
# MOBILE_PLATFORM=ios is reserved for later; conftest.py raises NotImplementedError for it today.
MOBILE_PLATFORM=android
APPIUM_SERVER_URL=http://127.0.0.1:4723
ANDROID_APP_PATH=demo_mobile_apps/mda-2.2.0-25.apk
```

For offline / no-key testing:
```dotenv
VISION_AGENT_PROVIDER=mock
TESTCASE_AGENT_PROVIDER=mock
APPIUM_AGENT_PROVIDER=mock
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

### 6 — Run Step 3 (SSM JSON + manual test cases → Appium scripts)

```powershell
python pipelines/appium_script_generator.py artifacts/ssm_json_output artifacts/manual_testcases artifacts/appium_scripts --clean
```

This pairs each SSM JSON file with its matching manual test case file (by filename), writes
`pages/<screen>_page.py` + `tests/test_<screen>.py` per screen, and copies the static
`conftest.py` + `core/base_page.py` templates into the output directory. Sanity-check without a
real device/emulator:

```powershell
python -m pytest artifacts/appium_scripts --collect-only
```

Running the suite for real (`python -m pytest artifacts/appium_scripts`) requires a live Appium
server at `APPIUM_SERVER_URL` and a connected emulator/simulator or BrowserStack/Sauce Labs session.

### Full end-to-end (single command)

```powershell
python pipelines/ssm_generator.py artifacts/input_screenshots artifacts/ssm_json_output --clean ; python pipelines/testcase_generator.py artifacts/ssm_json_output artifacts/manual_testcases --clean ; python pipelines/appium_script_generator.py artifacts/ssm_json_output artifacts/manual_testcases artifacts/appium_scripts --clean
```

---

## How to Change the LLM Behaviour

All LLM instructions are externalised as plain text files. **No code changes needed.**

| File | Controls |
|---|---|
| `prompts/vision_analysis.txt` | How the vision model describes screens and elements |
| `prompts/test_generation.txt` | How the language model formats and writes test cases |
| `prompts/appium_script_generation.txt` | How the LLM structures generated Appium scripts (locator style, wait strategy, method naming) |

Edit any file, re-run the corresponding step, and compare outputs.

---

## How to Switch Providers

Set the environment variables before running:

| Variable | Values |
|---|---|
| `VISION_AGENT_PROVIDER` | `openai` \| `mock` |
| `TESTCASE_AGENT_PROVIDER` | `openai` \| `mock` |
| `APPIUM_AGENT_PROVIDER` | `openai` \| `mock` |
| `OPENAI_MODEL` | Any chat-completion model name (e.g. `gpt-4o`, `gpt-4o-mini`) |
| `OPENAI_API_BASE` | Override the base URL for internal API gateways |
| `MOBILE_PLATFORM` | `android` (only supported value today; `ios` raises `NotImplementedError` in `conftest.py`) |
| `APPIUM_SERVER_URL` | Appium server the generated `conftest.py` driver fixture connects to |
| `ANDROID_APP_PATH` | App under test — defaults to the Android demo app in `demo_mobile_apps/` |

Adding a new provider (e.g. Azure, Anthropic) requires only:
1. Create a new class that extends `agents/core/vision_agent.py::VisionAgent`, `agents/core/testcase_agent.py::TestCaseAgent`, or `agents/core/appium_agent.py::AppiumScriptAgent`
2. Register it in the `create_vision_agent()` / `create_testcase_agent()` / `create_appium_agent()` factory function

---

## Data Model

The **Screen Semantic Model (SSM)** is the shared contract between Step 1, Step 2, and Step 3.
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

Step 3's generated Page Objects derive their `LOCATORS` dict directly from each element's `label`
(as `AppiumBy.ACCESSIBILITY_ID`, keyed by camelCase) and derive action methods from `type`/`actions`
(e.g. `textfield` + `enter_text` → `enter<Element>(self, value)` calling `self.typeText(...)`,
`button` + `tap` → `tap<Element>(self)` calling `self.click(...)`). The test module never sees the
SSM directly — it only calls the methods the Page Object exposes.

---

## Running Tests

```powershell
python -m unittest tests.test_ssm_model tests.test_appium_agent
```

Run this before merging any changes that touch `models/ssm.py`, `agents/vision_agent.py`, or
`services/appium_agent.py`.

---

## What is NOT in scope (yet)

| Capability | Status |
|---|---|
| Reviewer agent (Appium best-practice review, anti-pattern suggestions) | Planned |
| Locator agent (verified UI element XPath/ID resolution) | Planned |
| Execution agent + BrowserStack/Sauce Labs execution reports | Planned |
| iOS support (XCUITest capabilities, populated `"ios"` locators) | Deferred — structurally reserved (`"ios": {}` in every `LOCATORS` dict, `NotImplementedError` in `conftest.py`) but not implemented |
| CI/CD integration | Not started |
| Multi-app support beyond the two bundled demo apps | Not started |

---

## Key Design Decisions

| Decision | Reason |
|---|---|
| Single `models/ssm.py` schema | Eliminated 4 duplicate model files; one source of truth |
| Abstract base classes in `agents/core/` | Allows new LLM providers without changing pipeline code |
| Prompts as `.txt` files | QA / non-developer team members can tune output without touching Python |
| `--clean` flag on runners | Explicitly clears output before a run; safe for reruns |
| `mock` provider mode | Full pipeline runs offline for demos or CI without an API key |
| `.venv` (Python 3.11/3.12) as active env | Stable; all dependencies install cleanly; tested end to end |
| LangChain tool-calling loop scoped to Step 3's self-validation only | The project brief calls out "LangChain Agents" and "Agentic AI"; the genuine decision-making payoff is a generate → validate → retry loop, not the single-shot SSM/test-case transformations, which stay plain LLM calls for consistency with Steps 1–2 |
| Built on `ChatOpenAI.bind_tools()` + a manual invoke loop, not `langchain.agents.AgentExecutor` | `AgentExecutor`'s internal streaming call dropped the connection against a real OpenAI-compatible gateway (LiteLLM proxy) on realistic multi-turn payload sizes ("peer closed connection... incomplete chunked read"). The lower-level loop is the same tool-calling pattern without that code path, verified directly against the gateway |
| `conftest.py` and `core/base_page.py` kept as static templates (`pipelines/templates/`), copied into output on every run | Driver setup and wait/click boilerplate are identical across every screen and don't need per-screen LLM judgment; keeping them static removes an entire class of generation risk and keeps them from being wiped by `--clean` |
| Page Object generation scoped to 2 files per screen (page + test), not 3 (no separate `locators/` file) | A third generated file with cross-file references (locator keys defined in one file, used in another) is pure surface area for the LLM to drift on; locators live inside the Page Object alongside the actions that use them, which the model handles far more reliably within one response than across files |
| `validate_pom_files` checks cross-file consistency (test-called methods must exist on the page object), not just per-file syntax | `ast.parse` and `pytest --collect-only` both only catch import/syntax-time errors — a test calling a page-object method that doesn't exist is an `AttributeError` that only surfaces when the test actually *runs*. This mechanical check (not an LLM judgment call) catches it before the script is ever accepted, and feeds the issue back into the same retry loop |
| Class/fixture/file names computed deterministically from `screen_name`, injected into the prompt as a fixed contract | Removes an entire class of hallucination risk (the model inventing a class name in one file and a different one in the import of another) by not asking the LLM to make naming decisions it has to remember across the multi-turn tool-calling loop |
| camelCase for all identifiers in generated Page Objects/tests (`enterUsername`, `tapLogin`); `test_` prefix on test functions is non-negotiable | Matches conventional Selenium/Appium POM style requested for readability; pytest's default `python_functions = test_*` discovery pattern requires the literal `test_` prefix, so only the remainder of each test function name is camelCase |
| Android only; iOS deferred but structurally reserved (`"ios": {}` locator entries, `NotImplementedError` in `conftest.py`) | Matches current focus without closing the door — adding iOS later means populating locators and implementing `XCUITestOptions`, not rewriting any generated page object or test |
| Generated locators are best-effort placeholders (`# LOCATOR_TODO`) | Locator Enrichment is a separate, later agent's responsibility; Step 3 only needs scripts to be structurally correct and runnable-shaped now |

---

## Contact / Ownership

Update this section with team contacts, Jira board links, and repo details before sharing.
