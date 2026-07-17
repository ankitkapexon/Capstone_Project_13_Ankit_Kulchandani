# Mobile Test Generator POC

A three-step pipeline that turns mobile app screenshots into manual test cases, then into a runnable
Android Appium Page Object Model test framework, using LLMs.

---

## What This Repo Does

- Turns a mobile app screenshot into structured screen data (Vision Agent)
- Turns that screen data into manual test cases (Test Case Agent)
- Turns those test cases into runnable Android Appium test scripts, following
  Page Object Model - locators + actions in one file, test steps in another
  (Appium Script Generator Agent)
- Works with OpenAI directly, any OpenAI-compatible LLM gateway (including an
  internal company LLM), or fully offline in mock mode with no API key

---

## Project Structure

```
MobileTestGeneratorPOC/
├── agents/
│   ├── core/
│   │   ├── vision_agent.py         # Abstract base for vision agents
│   │   ├── testcase_agent.py       # Abstract base for test case agents
│   │   └── appium_agent.py         # Abstract base for Appium script generator agents (generate() -> {path: content})
│   ├── vision_agent.py             # OpenAIVisionAgent + MockVisionAgent + factory
│   └── __init__.py
├── models/
│   └── ssm.py                      # Single canonical Screen Semantic Model (Pydantic)
├── services/
│   ├── config.py                   # Loads .env environment variables
│   ├── pipeline.py                 # analyze_screenshot / save_semantic_model helpers
│   ├── testcase_agent.py           # OpenAITestCaseAgent + MockTestCaseAgent + factory
│   └── appium_agent.py             # OpenAIAppiumScriptAgent (LangChain self-validating POM agent) + MockAppiumScriptAgent + factory
├── pipelines/
│   ├── ssm_generator.py            # Step 1 – screenshots → SSM JSON
│   ├── testcase_generator.py       # Step 2 – SSM JSON → manual test cases
│   ├── appium_script_generator.py  # Step 3 – SSM JSON + manual test cases → Appium Page Object + test files
│   └── templates/
│       ├── appium_conftest.py      # Static driver fixture (Android), copied into artifacts/appium_scripts/ each run
│       └── appium_base_page.py     # Static BasePage (waitForVisible/click/typeText/...), copied into appium_scripts/core/ each run
```

Step 3's output layout (per screen, written under `artifacts/appium_scripts/`):

```
artifacts/appium_scripts/
├── conftest.py              # driver fixture (static)
├── core/
│   └── base_page.py         # BasePage shared helpers (static)
├── pages/
│   └── login_page.py        # LOCATORS + camelCase action methods (LLM-generated)
└── tests/
    └── test_login.py        # thin test flow using the page object only (LLM-generated)
```

---

## Setup

### 1. Create a virtual environment

**Windows PowerShell:**
```powershell
cd C:\Users\priyanka.pattewar\MobileTestGeneratorPOC
.\scripts\setup_env.ps1 -PythonExe python
```

**macOS / Linux:**
```bash
cd /path/to/MobileTestGeneratorPOC
bash scripts/setup_env.sh
```

> Use Python 3.11 or 3.12. Python 3.15+ may not support all dependencies cleanly.

### 2. Configure your `.env` file

Copy the template and fill in your values:
```bash
cp .env.example .env
```
Ask your team lead for the real `OPENAI_API_KEY` / `OPENAI_API_BASE` / `OPENAI_MODEL`
values (or your own OpenAI key). `.env` is gitignored - never commit it.

To run fully offline with no LLM, set all three `*_AGENT_PROVIDER` vars in `.env` to `mock`.

---

## Running the Pipeline

### Step 1 – Screenshots → SSM JSON

Place your screenshots inside `artifacts/input_screenshots/`, then run:

```powershell
python pipelines/ssm_generator.py artifacts/input_screenshots artifacts/ssm_json_output --clean
```

Output: one `ssm_<ScreenName>_<timestamp>.json` file per screenshot in `artifacts/ssm_json_output/`.

### Step 2 – SSM JSON → Manual Test Cases

```powershell
python pipelines/testcase_generator.py artifacts/ssm_json_output artifacts/manual_testcases --clean
```

Output: one `manual_testcases_<name>_<timestamp>.txt` file per SSM JSON in `artifacts/manual_testcases/`.

### Step 3 – SSM JSON + Manual Test Cases → Appium Page Object Model

```powershell
python pipelines/appium_script_generator.py artifacts/ssm_json_output artifacts/manual_testcases artifacts/appium_scripts --clean
```

Output per screen: `pages/<screen>_page.py` (locators + camelCase action methods, e.g. `enterUsername`,
`tapLogin`) and `tests/test_<screen>.py` (thin test flow that only calls page-object methods — no
locators, no raw `driver` calls, no assertions-on-elements). `conftest.py` and `core/base_page.py` are
static, copied in every run, not LLM-generated. Run the generated suite with:

```powershell
python -m pytest artifacts/appium_scripts --collect-only   # sanity-check without a real Appium server
python -m pytest artifacts/appium_scripts                  # requires a running Appium server
```

Locators are best-effort placeholders derived from the SSM (`# LOCATOR_TODO` comments) — the planned
Locator Enrichment Agent resolves these to verified selectors later in the pipeline. Each page object
reserves an empty `"ios": {}` entry in its `LOCATORS` dict so iOS support can be added later without
touching any generated method.

### Full end-to-end (single command)

```powershell
python pipelines/ssm_generator.py artifacts/input_screenshots artifacts/ssm_json_output --clean ; python pipelines/testcase_generator.py artifacts/ssm_json_output artifacts/manual_testcases --clean ; python pipelines/appium_script_generator.py artifacts/ssm_json_output artifacts/manual_testcases artifacts/appium_scripts --clean
```

---

## Supported Image Formats

`png`, `jpg`, `jpeg`, `webp`, `bmp`

---

## Running Tests

```powershell
python -m unittest tests.test_ssm_model tests.test_appium_agent
```

---

## Architecture Notes

- **Steps are loosely coupled.** Step 1 writes SSM JSON, Step 2 reads SSM JSON and writes manual test cases, Step 3 reads both and writes an Appium Page Object Model bundle. Each can run independently given its inputs on disk.
- **Providers are swappable.** Set `VISION_AGENT_PROVIDER`, `TESTCASE_AGENT_PROVIDER`, or `APPIUM_AGENT_PROVIDER` to `openai` or `mock`.
- **Single canonical model.** All screen data uses `models/ssm.py` — no duplicate schema files.
- **Prompts are externalized.** Edit `prompts/vision_analysis.txt`, `prompts/test_generation.txt`, or `prompts/appium_script_generation.txt` to tune LLM behaviour without touching code.
- **No root-level runner scripts.** Run the pipeline files in `pipelines/` directly — no wrappers needed.
- **Appium script generation (Step 3) follows Page Object Model.** For each screen the LLM generates exactly two files — a Page Object (`pages/<screen>_page.py`: locators + camelCase action methods, e.g. `enterUsername`, `tapLogin`, built on the shared `BasePage`) and a test module (`tests/test_<screen>.py`: thin, only calls page-object methods, no locators or raw driver calls). `conftest.py` and `core/base_page.py` are static templates, not LLM-generated — the model never has to reinvent driver setup or wait boilerplate.
- **Self-validating generation loop.** `OpenAIAppiumScriptAgent` uses `ChatOpenAI.bind_tools()` (not `langchain.agents.AgentExecutor` — its internal streaming call was incompatible with some OpenAI-compatible gateways on larger payloads) in a manual tool-calling loop: the model drafts both files, calls `validate_pom_files` on its own draft, and retries (capped) until clean. That tool checks Python syntax (`ast.parse`), Appium anti-patterns (`time.sleep`, fragile `//*` XPath, deprecated `find_element_by_*`), **and** cross-file consistency — every page-object method the test file calls must actually be defined on the page object, since an `AttributeError` from a name mismatch only surfaces at test *execution* time and `pytest --collect-only` doesn't catch it. `MockAppiumScriptAgent` builds the same POM shape deterministically from the SSM, offline, for demos/CI.
- **Locators are placeholders pending enrichment.** Generated page objects use SSM label/accessibility-id best guesses tagged `# LOCATOR_TODO`; the planned Locator Enrichment Agent resolves real, verified selectors later in the pipeline. Reviewer and Execution agents are also still planned.
- **Android only for now, iOS door left open.** `conftest.py` raises `NotImplementedError` for `MOBILE_PLATFORM=ios`, and every generated `LOCATORS` dict reserves an empty `"ios": {}` entry — adding iOS later is additive (populate locators + implement `XCUITestOptions`), not a rewrite of any generated page object or test.
