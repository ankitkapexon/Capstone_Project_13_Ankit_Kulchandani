import ast
import json
import os
import re
from typing import Any, Dict, List, Set

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from agents.core.appium_agent import AppiumScriptAgent

ANTI_PATTERNS = [
    (re.compile(r"time\.sleep\("), "Hardcoded time.sleep() call - use the base page's wait helpers instead."),
    (re.compile(r"//\*\["), "Fragile wildcard XPath locator (//*[...]) - prefer accessibility id / id locators."),
    (re.compile(r"find_element_by_"), "Deprecated find_element_by_* API - use driver.find_element(*locator)."),
]


def _check_appium_script(script: str) -> List[str]:
    """Return a list of issue strings: syntax errors and known Appium anti-patterns."""
    issues: List[str] = []
    try:
        ast.parse(script)
    except SyntaxError as exc:
        issues.append(f"Invalid Python syntax: {exc}")
        return issues

    for pattern, message in ANTI_PATTERNS:
        if pattern.search(script):
            issues.append(message)
    return issues


def _extract_class_methods(source: str) -> Set[str]:
    """Public method names defined on any class in source; empty set if unparsable."""
    methods: Set[str] = set()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return methods
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                    methods.add(item.name)
    return methods


def _extract_fixture_calls(test_source: str, fixture_name: str) -> Set[str]:
    """Method names called on `fixture_name.<method>(...)` anywhere in test_source."""
    calls: Set[str] = set()
    try:
        tree = ast.parse(test_source)
    except SyntaxError:
        return calls
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            value = node.func.value
            if isinstance(value, ast.Name) and value.id == fixture_name:
                calls.add(node.func.attr)
    return calls


def _check_pom_consistency(page_source: str, test_source: str, fixture_name: str, class_name: str) -> List[str]:
    """Deterministic cross-file check: every page-object method the test calls must
    actually be defined on the page object. This is what closes the gap that per-file
    syntax checking can't catch (AttributeError only surfaces at test execution time)."""
    issues: List[str] = []

    if f"class {class_name}" not in page_source:
        issues.append(f"Page object does not define the expected class '{class_name}'.")

    if fixture_name not in test_source:
        issues.append(f"Test module never references the expected page-object fixture '{fixture_name}'.")
        return issues

    class_methods = _extract_class_methods(page_source)
    called_methods = _extract_fixture_calls(test_source, fixture_name)
    for name in sorted(called_methods - class_methods):
        issues.append(
            f"Test module calls {fixture_name}.{name}(), which is not defined as a method on {class_name}."
        )
    return issues


def _strip_code_fences(text: str) -> str:
    text = (text or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return text


def _words(name: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9]+", name or "") or ["Screen"]


def _pascal_case(name: str) -> str:
    return "".join(w.capitalize() for w in _words(name))


def _camel_case(name: str) -> str:
    words = _words(name)
    return words[0].lower() + "".join(w.capitalize() for w in words[1:])


def _snake_case(name: str) -> str:
    return "_".join(w.lower() for w in _words(name))


def _screen_contract(screen_name: str) -> Dict[str, str]:
    """Deterministic naming contract for a screen - computed by us, not left to the
    LLM to invent, so class/fixture/file names can never drift from what the pipeline
    expects to write to disk."""
    slug = _snake_case(screen_name)
    return {
        "class_name": f"{_pascal_case(screen_name)}Page",
        "fixture_name": f"{_camel_case(screen_name)}Page",
        "page_file": f"pages/{slug}_page.py",
        "test_file": f"tests/test_{slug}.py",
    }


class OpenAIAppiumScriptAgent(AppiumScriptAgent):
    """Generates a Page Object + test module pair via an LLM, self-validated and
    retried through a LangChain tool-calling loop bounded by max_retries.

    Uses ChatOpenAI.bind_tools() + a manual invoke loop rather than langchain.agents'
    AgentExecutor: AgentExecutor's internal streaming call is incompatible with some
    OpenAI-compatible gateways (e.g. LiteLLM proxies) on larger multi-turn payloads,
    dropping the connection mid-response. This loop is the same tool-calling pattern
    (LLM decides whether/when to call validate_pom_files and when to stop) built on
    lower-level LangChain primitives that don't hit that code path.

    The validation tool takes page_object/test_module as structured arguments (not
    free text), so the model's tool-call arguments are themselves the final output -
    no delimiter/marker parsing of a combined text blob is needed.
    """

    def __init__(self, prompt_template: str | None = None, max_retries: int = 2):
        self.prompt_template = prompt_template
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_base = os.getenv("OPENAI_API_BASE")
        self.max_retries = max_retries
        self._llm = None

    def _get_llm(self) -> ChatOpenAI:
        if self._llm is None:
            kwargs: Dict[str, Any] = {"model": self.model, "api_key": self.api_key}
            if self.api_base:
                kwargs["base_url"] = self.api_base
            # ChatOpenAI defaults temperature to 0.7 when unset (unlike the raw openai
            # SDK), so gpt-5 models need it pinned to 1 explicitly, not just left unset.
            kwargs["temperature"] = 1 if "gpt-5" in self.model.lower() else 0
            self._llm = ChatOpenAI(**kwargs)
        return self._llm

    def _build_prompt(self, ssm_json: str, testcases_text: str, contract: Dict[str, str]) -> str:
        if self.prompt_template:
            text = self.prompt_template
            for key, value in contract.items():
                text = text.replace(f"{{{{{key}}}}}", value)
            return text.replace("{{ssm_json}}", ssm_json).replace("{{testcases_text}}", testcases_text)
        return (
            f"Generate a Page Object named {contract['class_name']} and a pytest test module "
            f"using a fixture named {contract['fixture_name']} for this screen.\n\n"
            f"SSM_JSON:\n{ssm_json}\n\nMANUAL_TEST_CASES:\n{testcases_text}"
        )

    def generate(self, ssm_data: Dict[str, Any], testcases_text: str, **kwargs) -> Dict[str, str]:
        screen_name = ssm_data.get("screen_name") or "Screen"
        contract = _screen_contract(screen_name)
        ssm_json = json.dumps(ssm_data, indent=2)
        base_prompt = self._build_prompt(ssm_json, testcases_text, contract)
        llm = self._get_llm()

        @tool("validate_pom_files")
        def validate_pom_files(page_object: str, test_module: str) -> str:
            """Validate the drafted Page Object and test module. Checks Python syntax,
            known Appium anti-patterns (hardcoded sleeps, fragile XPaths, deprecated
            APIs) in each file, and cross-file consistency: every page-object method
            the test module calls must actually be defined on the page object class.
            Returns a JSON array of issue strings; an empty array means both files are
            clean and consistent."""
            issues = []
            issues += [f"[page object] {i}" for i in _check_appium_script(page_object)]
            issues += [f"[test module] {i}" for i in _check_appium_script(test_module)]
            issues += _check_pom_consistency(page_object, test_module, contract["fixture_name"], contract["class_name"])
            return json.dumps(issues)

        llm_with_tools = llm.bind_tools([validate_pom_files])

        messages: List[Any] = [
            SystemMessage(content=(
                "You are a Senior SDET generating a Page Object Model Appium test bundle for one screen. "
                f"Define exactly one class named {contract['class_name']} in the page object, and exactly one "
                f"pytest fixture named {contract['fixture_name']} in the test module that returns "
                f"{contract['class_name']}(driver). "
                "You MUST call the validate_pom_files tool with your complete drafted page_object and "
                "test_module every turn - never respond with plain text. If it reports issues, revise both "
                "files and call the tool again. Stop calling the tool once it reports an empty issue array."
            )),
            HumanMessage(content=base_prompt),
        ]

        last_page, last_test = "", ""
        try:
            for _ in range(self.max_retries + 1):
                ai_msg = llm_with_tools.invoke(messages)
                messages.append(ai_msg)

                if not ai_msg.tool_calls:
                    break

                tool_call = ai_msg.tool_calls[0]
                page_arg = tool_call["args"].get("page_object", "")
                test_arg = tool_call["args"].get("test_module", "")
                if page_arg:
                    last_page = page_arg
                if test_arg:
                    last_test = test_arg

                tool_result = validate_pom_files.invoke(tool_call["args"])
                messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call["id"]))

                if json.loads(tool_result) == []:
                    break
        except Exception as exc:
            raise RuntimeError(f"Appium script generation failed: {exc}")

        if not last_page.strip() or not last_test.strip():
            raise RuntimeError("Appium script generation returned incomplete output")

        return {
            contract["page_file"]: _strip_code_fences(last_page) + "\n",
            contract["test_file"]: _strip_code_fences(last_test) + "\n",
        }


class MockAppiumScriptAgent(AppiumScriptAgent):
    """Offline, deterministic POM generator - builds a page object + test module
    straight from SSM elements so the pipeline runs end-to-end without an LLM, for
    demos/CI. Since both files are built from the same element list in one pass,
    method names naturally stay consistent between them."""

    def _element_key(self, element: Dict[str, Any], index: int) -> str:
        label = element.get("label") or element.get("id") or f"element{index}"
        return _camel_case(str(label))

    def _action_method_name(self, element: Dict[str, Any], key: str) -> str:
        actions = [str(a).lower() for a in element.get("actions") or []]
        pascal_key = key[0].upper() + key[1:]
        if "enter_text" in actions:
            return f"enter{pascal_key}"
        if "tap" in actions or "select" in actions:
            return f"tap{pascal_key}"
        return f"is{pascal_key}Visible"

    def _build_page_object(self, contract: Dict[str, str], elements: List[Dict[str, Any]]) -> str:
        keys = [self._element_key(el, i) for i, el in enumerate(elements)]
        lines: List[str] = [
            "import os",
            "",
            "from appium.webdriver.common.appiumby import AppiumBy",
            "",
            "from core.base_page import BasePage",
            "",
            "",
            f"class {contract['class_name']}(BasePage):",
            "    LOCATORS = {",
            '        "android": {',
        ]
        for el, key in zip(elements, keys):
            value = str(el.get("label") or el.get("id") or key).replace('"', '\\"')
            lines.append(f'            "{key}": (AppiumBy.ACCESSIBILITY_ID, "{value}"),  # LOCATOR_TODO: verify/replace once Locator Enrichment Agent resolves real selectors')
        lines.extend([
            "        },",
            '        "ios": {},  # LOCATOR_TODO: populate when iOS support is implemented',
            "    }",
            "",
            '    PLATFORM = os.getenv("MOBILE_PLATFORM", "android").lower()',
            "",
            "    def _locator(self, key):",
            "        return self.LOCATORS[self.PLATFORM][key]",
            "",
        ])
        for el, key in zip(elements, keys):
            method = self._action_method_name(el, key)
            actions = [str(a).lower() for a in el.get("actions") or []]
            if "enter_text" in actions:
                lines.append(f"    def {method}(self, value):")
                lines.append(f'        self.typeText(self._locator("{key}"), value)')
            elif "tap" in actions or "select" in actions:
                lines.append(f"    def {method}(self):")
                lines.append(f'        self.click(self._locator("{key}"))')
            else:
                lines.append(f"    def {method}(self, timeout=5):")
                lines.append(f'        return self.isVisible(self._locator("{key}"), timeout=timeout)')
            lines.append("")
        if not elements:
            lines.append("    # No SSM elements available to automate for this screen.")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def _build_test_module(self, contract: Dict[str, str], screen_name: str, elements: List[Dict[str, Any]], testcases_text: str) -> str:
        keys = [self._element_key(el, i) for i, el in enumerate(elements)]
        methods = [self._action_method_name(el, key) for el, key in zip(elements, keys)]
        visibility_methods = [m for m in methods if m.startswith("is") and m.endswith("Visible")]
        page_module = contract["page_file"][len("pages/"):-len(".py")]

        titles = re.findall(r"Test Case \d+:\s*(.+)", testcases_text or "") or [f"Validate {screen_name} screen"]

        lines: List[str] = [
            "import pytest",
            "",
            f"from pages.{page_module} import {contract['class_name']}",
            "",
            "",
            "@pytest.fixture",
            f"def {contract['fixture_name']}(driver):",
            f"    return {contract['class_name']}(driver)",
            "",
            "",
        ]
        for i, title in enumerate(titles, start=1):
            clean_title = title.strip().rstrip(".")
            slug = _camel_case(clean_title)[:60] or f"case{i}"
            lines.append(f"def test_{slug}({contract['fixture_name']}):")
            lines.append(f'    """Test Case {i}: {clean_title}"""')
            for el, key, method in zip(elements, keys, methods):
                actions = [str(a).lower() for a in el.get("actions") or []]
                if "enter_text" in actions:
                    lines.append(f'    {contract["fixture_name"]}.{method}("sample_value")')
                elif "tap" in actions or "select" in actions:
                    lines.append(f"    {contract['fixture_name']}.{method}()")
            if visibility_methods:
                lines.append(f"    assert {contract['fixture_name']}.{visibility_methods[0]}(), \"LOCATOR_TODO: replace with a real expected-result assertion\"")
            else:
                lines.append(f"    assert {contract['fixture_name']} is not None  # LOCATOR_TODO: replace with a real expected-result assertion")
            lines.append("")
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    def generate(self, ssm_data: Dict[str, Any], testcases_text: str, **kwargs) -> Dict[str, str]:
        screen_name = ssm_data.get("screen_name") or "Screen"
        elements = ssm_data.get("elements", [])
        contract = _screen_contract(screen_name)

        return {
            contract["page_file"]: self._build_page_object(contract, elements),
            contract["test_file"]: self._build_test_module(contract, screen_name, elements, testcases_text),
        }


def create_appium_agent(provider: str = None, prompt_template: str = None) -> AppiumScriptAgent:
    provider = (provider or os.getenv("APPIUM_AGENT_PROVIDER") or "").lower().strip()
    if not provider:
        provider = "openai" if os.getenv("OPENAI_API_KEY") else "mock"
    if provider == "openai":
        return OpenAIAppiumScriptAgent(prompt_template=prompt_template)
    if provider == "mock":
        return MockAppiumScriptAgent()
    raise ValueError(f"Unsupported appium provider: {provider}")
