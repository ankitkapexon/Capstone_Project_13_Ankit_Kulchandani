import unittest

from services.live_locator_agent import MockLiveLocatorAgent, extract_candidates, _validate_against_candidates

SAMPLE_XML = """<?xml version='1.0' encoding='UTF-8'?>
<hierarchy>
  <node resource-id="com.example.app:id/nameET" content-desc="" text="" class="android.widget.EditText" clickable="true" />
  <node resource-id="com.example.app:id/loginBtn" content-desc="Tap to login" text="Login" class="android.widget.Button" clickable="true" />
  <node resource-id="" content-desc="" text="Welcome" class="android.widget.TextView" clickable="false" />
</hierarchy>
"""


class ExtractCandidatesTests(unittest.TestCase):
    def test_extracts_addressable_nodes_only(self) -> None:
        candidates = extract_candidates(SAMPLE_XML)
        resource_ids = {c["resource_id"] for c in candidates if c["resource_id"]}
        self.assertIn("com.example.app:id/nameET", resource_ids)
        self.assertIn("com.example.app:id/loginBtn", resource_ids)

    def test_returns_empty_list_for_unparsable_xml(self) -> None:
        self.assertEqual(extract_candidates("not xml"), [])


class ValidateAgainstCandidatesTests(unittest.TestCase):
    def test_drops_invented_locator_not_present_in_candidates(self) -> None:
        candidates = extract_candidates(SAMPLE_XML)
        elements = [
            {"element": "Username", "locator_strategy": "resource_id", "locator_value": "com.example.app:id/nameET"},
            {"element": "Search", "locator_strategy": "resource_id", "locator_value": "com.example.app:id/searchBar_invented"},
        ]
        verified = _validate_against_candidates(elements, candidates)
        self.assertEqual([e["element"] for e in verified], ["Username"])


class MockLiveLocatorAgentTests(unittest.TestCase):
    def test_resolve_grounds_matching_element_and_drops_unmatched(self) -> None:
        agent = MockLiveLocatorAgent()
        ssm_data = {
            "screen_name": "Login",
            "elements": [
                {"label": "Login", "type": "button", "actions": ["tap"]},
                {"label": "Nonexistent Widget", "type": "button", "actions": ["tap"]},
            ],
        }

        result = agent.resolve(ssm_data, SAMPLE_XML)

        self.assertEqual(result["screen"], "Login")
        elements = result["elements"]
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0]["locator_value"], "com.example.app:id/loginBtn")


if __name__ == "__main__":
    unittest.main()
