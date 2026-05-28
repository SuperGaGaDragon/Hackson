"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

import httpx


class SearchProviderError(RuntimeError):
    """Stable search provider failure used by Work Mode tool execution."""

    def __init__(self, code: str, retryable: bool = False):
        super().__init__(code)
        self.code = code
        self.retryable = retryable


class DuckDuckGoLiteSearchProvider:
    """Small read-only search provider that returns normalized sourced snippets."""

    def __init__(self, base_url: str = "https://lite.duckduckgo.com/lite/", timeout_seconds: float = 10.0):
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds

    def search(self, request: dict[str, Any]) -> dict[str, Any]:
        limit = int(request.get("maxResults") or 5)
        requested_query = _base_query(request)
        attempts = _fallback_attempts(request)
        last_effective_query = attempts[-1].query if attempts else requested_query
        for index, attempt in enumerate(attempts, start=1):
            results = self._search_once(attempt.query, limit * 3)
            results = _filter_results(results, request)
            if results:
                bounded = results[:limit]
                return {
                    "status": "ok",
                    "results": bounded,
                    "truncated": len(results) > limit or len(bounded) >= limit,
                    "provider": "duckduckgo_lite",
                    "query": requested_query,
                    "effectiveQuery": attempt.query,
                    "fallbackApplied": index > 1,
                    "fallbackReason": None if index == 1 else "no_results_after_primary_query",
                    "attemptCount": index,
                }
            last_effective_query = attempt.query
        return {
            "status": "failed",
            "code": "search_no_results",
            "retryable": False,
            "provider": "duckduckgo_lite",
            "results": [],
            "truncated": False,
            "query": requested_query,
            "effectiveQuery": last_effective_query,
            "fallbackApplied": len(attempts) > 1,
            "fallbackReason": "no_results_after_primary_query" if len(attempts) > 1 else None,
            "attemptCount": len(attempts),
        }

    def _search_once(self, query: str, limit: int) -> list[dict[str, str | None]]:
        try:
            response = httpx.get(
                self.base_url,
                params={"q": query},
                timeout=self.timeout_seconds,
                headers={"User-Agent": "HacksonWorkMode/1.0"},
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise SearchProviderError("search_timeout", retryable=True) from exc
        except httpx.HTTPStatusError as exc:
            retryable = exc.response.status_code in {408, 409, 425, 429, 500, 502, 503, 504}
            code = "search_rate_limited" if exc.response.status_code == 429 else "search_provider_unavailable"
            raise SearchProviderError(code, retryable=retryable) from exc
        except httpx.HTTPError as exc:
            raise SearchProviderError("search_provider_unavailable", retryable=True) from exc
        return _parse_duckduckgo_lite_results(response.text, limit)


@dataclass(frozen=True)
class _SearchAttempt:
    query: str


def _fallback_attempts(request: dict[str, Any]) -> list[_SearchAttempt]:
    candidates = [
        _query_with_domains(request),
        _base_query(request),
        _compact_query(_base_query(request)),
    ]
    unique: list[_SearchAttempt] = []
    seen: set[str] = set()
    for candidate in candidates:
        query = candidate.strip()
        if query and query not in seen:
            unique.append(_SearchAttempt(query=query))
            seen.add(query)
    return unique


def _filter_results(results: list[dict[str, str | None]], request: dict[str, Any]) -> list[dict[str, str | None]]:
    allowed = [_normalize_domain(domain) for domain in request.get("allowedDomains") or [] if domain]
    blocked = [_normalize_domain(domain) for domain in request.get("blockedDomains") or [] if domain]
    filtered: list[dict[str, str | None]] = []
    for item in results:
        source = _normalize_domain(str(item.get("source") or _source(str(item.get("url") or ""))))
        if blocked and any(_domain_matches(source, domain) for domain in blocked):
            continue
        if allowed and not any(_domain_matches(source, domain) for domain in allowed):
            continue
        filtered.append(item)
    return filtered


def _compact_query(query: str) -> str:
    tokens = [token for token in query.replace(",", " ").split() if token]
    if len(tokens) <= 5:
        return query
    preferred = [token for token in tokens if token[:1].isupper() or len(token) > 6]
    compact = preferred[:6] if len(preferred) >= 3 else tokens[:6]
    return " ".join(compact)


def _base_query(request: dict[str, Any]) -> str:
    return str(request.get("query") or "").strip()
            return {
                "status": "failed",
                "code": "search_no_results",
                "retryable": False,
                "provider": "duckduckgo_lite",
                "results": [],
                "truncated": False,
            }
        return {
            "status": "ok",
            "results": results,
            "truncated": len(results) >= int(request.get("maxResults") or 5),
            "provider": "duckduckgo_lite",
        }


class _DuckDuckGoLiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict[str, str | None]] = []
        self._current_link: dict[str, str | None] | None = None
        self._capture_link_text = False
        self._last_link: dict[str, str | None] | None = None
        self._capture_snippet = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag == "a" and "result-link" in (attrs_dict.get("class") or ""):
            self._current_link = {"title": "", "url": _normalize_duckduckgo_url(attrs_dict.get("href") or "")}
            self._capture_link_text = True
            return
        if tag == "td" and "result-snippet" in (attrs_dict.get("class") or ""):
            self._capture_snippet = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._capture_link_text and self._current_link is not None:
            self._current_link["title"] = (self._current_link.get("title") or "").strip()
            if self._current_link["title"] and self._current_link["url"]:
                self.results.append({**self._current_link, "snippet": "", "source": _source(self._current_link["url"])})
                self._last_link = self.results[-1]
            self._current_link = None
            self._capture_link_text = False
            return
        if tag == "td" and self._capture_snippet:
            self._capture_snippet = False

    def handle_data(self, data: str) -> None:
        if self._capture_link_text and self._current_link is not None:
            self._current_link["title"] = f"{self._current_link.get('title') or ''}{data}"
            return
        if self._capture_snippet and self._last_link is not None:
            self._last_link["snippet"] = f"{self._last_link.get('snippet') or ''}{data}".strip()


def _parse_duckduckgo_lite_results(html: str, limit: int) -> list[dict[str, str | None]]:
    parser = _DuckDuckGoLiteParser()
    parser.feed(html)
    normalized: list[dict[str, str | None]] = []
    for item in parser.results:
        title = (item.get("title") or "").strip()
        url = (item.get("url") or "").strip()
        if not title or not url:
            continue
        normalized.append(
            {
                "title": title[:300],
                "url": url[:2000],
                "source": (item.get("source") or _source(url))[:200],
                "snippet": (item.get("snippet") or "")[:1200],
                "publishedAt": None,
            }
        )
        if len(normalized) >= limit:
            break
    return normalized


def _query_with_domains(request: dict[str, Any]) -> str:
    query = _base_query(request)
    allowed = [domain for domain in request.get("allowedDomains") or [] if domain]
    blocked = [domain for domain in request.get("blockedDomains") or [] if domain]
    domain_terms = [f"site:{domain}" for domain in allowed]
    domain_terms.extend(f"-site:{domain}" for domain in blocked)
    return " ".join([query, *domain_terms]).strip()


def _normalize_duckduckgo_url(raw_url: str) -> str:
    parsed = urlparse(raw_url)
    query = parse_qs(parsed.query)
    if "uddg" in query and query["uddg"]:
        return unquote(query["uddg"][0])
    return raw_url


def _source(url: str) -> str:
    host = urlparse(url).netloc
    return host.removeprefix("www.")


def _normalize_domain(domain: str) -> str:
    parsed = urlparse(domain if "://" in domain else f"https://{domain}")
    return parsed.netloc.removeprefix("www.").lower()


def _domain_matches(source: str, domain: str) -> bool:
    return source == domain or source.endswith(f".{domain}")
