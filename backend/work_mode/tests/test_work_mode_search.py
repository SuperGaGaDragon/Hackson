"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from unittest import TestCase
from unittest.mock import patch

from work_mode.search import DuckDuckGoLiteSearchProvider, _parse_duckduckgo_lite_results


class WorkModeSearchTest(TestCase):
    def test_duckduckgo_lite_parser_returns_bounded_normalized_results(self) -> None:
        html = """
        <html><body>
          <a rel="nofollow" class="result-link" href="/l/?uddg=https%3A%2F%2Fexample.com%2Fa">Source A</a>
          <td class="result-snippet">First snippet.</td>
          <a rel="nofollow" class="result-link" href="https://example.org/b">Source B</a>
          <td class="result-snippet">Second snippet.</td>
        </body></html>
        """

        results = _parse_duckduckgo_lite_results(html, limit=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Source A")
        self.assertEqual(results[0]["url"], "https://example.com/a")
        self.assertEqual(results[0]["source"], "example.com")
        self.assertEqual(results[0]["snippet"], "First snippet.")

    def test_provider_falls_back_from_site_query_to_filtered_results(self) -> None:
        calls: list[str] = []

        def fake_get(url: str, params: dict, timeout: float, headers: dict) -> FakeResponse:
            calls.append(params["q"])
            if params["q"] == "Haitian Revolution site:britannica.com -site:wikipedia.org":
                return FakeResponse("<html></html>")
            return FakeResponse(
                """
                <html><body>
                  <a class="result-link" href="https://en.wikipedia.org/wiki/Haitian_Revolution">Wiki</a>
                  <td class="result-snippet">Blocked result.</td>
                  <a class="result-link" href="https://www.britannica.com/topic/Haitian-Revolution">Britannica</a>
                  <td class="result-snippet">Allowed result.</td>
                </body></html>
                """
            )

        provider = DuckDuckGoLiteSearchProvider(timeout_seconds=1)

        with patch("work_mode.search.httpx.get", side_effect=fake_get):
            result = provider.search(
                {
                    "query": "Haitian Revolution",
                    "maxResults": 5,
                    "allowedDomains": ["britannica.com"],
                    "blockedDomains": ["wikipedia.org"],
                }
            )

        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["fallbackApplied"])
        self.assertEqual(result["fallbackReason"], "no_results_after_primary_query")
        self.assertEqual(result["effectiveQuery"], "Haitian Revolution")
        self.assertEqual(result["attemptCount"], 2)
        self.assertEqual(calls, ["Haitian Revolution site:britannica.com -site:wikipedia.org", "Haitian Revolution"])
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["source"], "britannica.com")

    def test_provider_compacts_long_query_before_returning_no_results(self) -> None:
        calls: list[str] = []

        def fake_get(url: str, params: dict, timeout: float, headers: dict) -> FakeResponse:
            calls.append(params["q"])
            if params["q"] == "Haitian Revolution literature historiography consequences slavery":
                return FakeResponse(
                    """
                    <html><body>
                      <a class="result-link" href="https://example.edu/haiti">Compact hit</a>
                      <td class="result-snippet">Compact query result.</td>
                    </body></html>
                    """
                )
            return FakeResponse("<html></html>")

        query = "Haitian Revolution literature review historiography causes consequences slavery colonialism"
        provider = DuckDuckGoLiteSearchProvider(timeout_seconds=1)

        with patch("work_mode.search.httpx.get", side_effect=fake_get):
            result = provider.search({"query": query, "maxResults": 5, "allowedDomains": [], "blockedDomains": []})

        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["fallbackApplied"])
        self.assertEqual(result["effectiveQuery"], "Haitian Revolution literature historiography consequences slavery")
        self.assertEqual(result["attemptCount"], 2)
        self.assertEqual(calls, [query, "Haitian Revolution literature historiography consequences slavery"])
        self.assertEqual(result["results"][0]["title"], "Compact hit")


class FakeResponse:
    def __init__(self, text: str):
        self.text = text

    def raise_for_status(self) -> None:
        return None
