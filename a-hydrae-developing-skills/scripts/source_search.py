#!/usr/bin/env python3
"""Read-only source acquisition for the a-hydrae-developing-skills skill.

The script intentionally uses only the Python standard library. It returns the
normalizer JSON shape used by the skill, with provider-specific metadata under
`extensions`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import html
import json
import re
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


USER_AGENT = "a-hydrae-developing-skills/0.1 (+read-only source acquisition)"


SOURCE_WEIGHTS = {
    "official": 100,
    "official-like-reference": 85,
    "primary": 80,
    "primary-or-community": 55,
    "community": 55,
    "blog": 40,
}


@dataclass
class FetchResult:
    url: str
    status: int | None
    headers: dict[str, str]
    body: bytes
    error: str | None = None


class SimpleHTMLExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self.meta: dict[str, str] = {}
        self._in_title = False
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {k.lower(): v or "" for k, v in attrs}
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            name = attrs_dict.get("name") or attrs_dict.get("property")
            content = attrs_dict.get("content")
            if name and content:
                self.meta[name.lower()] = html.unescape(content).strip()

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self._skip_depth:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        stripped = " ".join(data.split())
        if not stripped:
            return
        if self._in_title:
            self.title_parts.append(stripped)
        elif len(stripped) > 30:
            self.text_parts.append(stripped)

    @property
    def title(self) -> str:
        return " ".join(self.title_parts).strip()

    @property
    def description(self) -> str:
        return (
            self.meta.get("description")
            or self.meta.get("og:description")
            or first_nonempty(self.text_parts)
        )


def first_nonempty(items: list[str]) -> str:
    for item in items:
        if item.strip():
            return item.strip()
    return ""


def today() -> str:
    return dt.date.today().isoformat()


def load_catalog() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[1] / "references" / "source-catalog.json"
    return json.loads(path.read_text(encoding="utf-8"))


def source_catalog_entry(source_id: str) -> dict[str, Any] | None:
    for source in load_catalog().get("sources", []):
        if source.get("source_id") == source_id:
            return source
    return None


def default_untrusted(source_id: str, category: str, url: str) -> bool:
    if category in {"official", "official-like-reference"}:
        return False
    if category in {"community", "primary-or-community", "blog"}:
        return True
    if source_id.startswith(("github", "stackexchange", "reddit", "pypi")):
        return True
    return False


def request_json(url: str, timeout: float) -> tuple[Any | None, str | None, int | None]:
    result = fetch_url(url, timeout=timeout)
    if result.error:
        return None, result.error, result.status
    try:
        return json.loads(result.body.decode("utf-8")), None, result.status
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc}", result.status


def fetch_url(url: str, timeout: float) -> FetchResult:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json,text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.5",
            "Accept-Encoding": "gzip",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            headers = {k.lower(): v for k, v in resp.headers.items()}
            if headers.get("content-encoding", "").lower() == "gzip":
                raw = gzip.decompress(raw)
            return FetchResult(url=resp.geturl(), status=resp.status, headers=headers, body=raw)
    except urllib.error.HTTPError as exc:
        body = exc.read() if hasattr(exc, "read") else b""
        return FetchResult(url=url, status=exc.code, headers={}, body=body, error=f"HTTP {exc.code}: {exc.reason}")
    except urllib.error.URLError as exc:
        return FetchResult(url=url, status=None, headers={}, body=b"", error=f"URL error: {exc.reason}")
    except TimeoutError:
        return FetchResult(url=url, status=None, headers={}, body=b"", error="timeout")


def normalize_text(value: str, limit: int = 500) -> str:
    value = html.unescape(re.sub(r"\s+", " ", value or "")).strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "..."


def source_record(
    *,
    source_id: str,
    title: str,
    url: str,
    category: str,
    base_weight: int,
    scope_match: dict[str, list[str]] | None = None,
    retrieved_at: str | None = None,
    published_at: str | None = None,
    updated_at: str | None = None,
    freshness: str = "unknown",
    screening_status: str = "needs-check",
    untrusted: bool | None = None,
    notes: str = "",
    extensions: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "source_id": source_id,
        "title": normalize_text(title, 240),
        "url": url,
        "category": category,
        "base_weight": base_weight,
        "scope_match": scope_match or {"languages": [], "platforms": [], "layers": [], "topics": []},
        "retrieved_at": retrieved_at or today(),
        "published_at": published_at,
        "updated_at": updated_at,
        "freshness": freshness,
        "screening_status": screening_status,
        "untrusted": default_untrusted(source_id, category, url) if untrusted is None else untrusted,
        "notes": notes,
        "extensions": extensions or {},
    }


def candidate_solution(
    *,
    source_id: str,
    summary: str,
    kind: str,
    status: str,
    pros: list[str] | None = None,
    cons: list[str] | None = None,
    risks: list[str] | None = None,
    version_constraints: list[str] | None = None,
    screening: dict[str, Any] | None = None,
) -> dict[str, Any]:
    safe_id = re.sub(r"[^a-z0-9]+", "-", source_id.lower()).strip("-")
    return {
        "id": f"solution-{safe_id}",
        "summary": normalize_text(summary, 700),
        "source_ids": [source_id],
        "type": kind,
        "pros": pros or [],
        "cons": cons or [],
        "risks": risks or [],
        "version_constraints": version_constraints or [],
        "screening": screening or {},
        "status": status,
    }


def stackexchange_search(query: str, limit: int, timeout: float, site: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    params = {
        "order": "desc",
        "sort": "relevance",
        "q": query,
        "site": site,
        "pagesize": str(limit),
        "filter": "default",
    }
    url = "https://api.stackexchange.com/2.3/search/advanced?" + urllib.parse.urlencode(params)
    data, error, status = request_json(url, timeout)
    registry = [
        extension("accepted_answer_id", "integer", "source", "stackexchange", "Accepted answer is a useful consensus signal."),
        extension("answer_count", "integer", "source", "stackexchange", "Question activity and answer availability."),
        extension("question_score", "integer", "source", "stackexchange", "Community signal; not normative."),
        extension("is_answered", "boolean", "source", "stackexchange", "Whether Stack Exchange considers the question answered."),
        extension("tags", "array[string]", "source", "stackexchange", "Tags help language and framework routing."),
    ]
    if error:
        return [
            source_record(
                source_id="stackexchange-error",
                title="Stack Exchange API error",
                url=url,
                category="community",
                base_weight=55,
                screening_status="reject",
                notes=error,
                extensions={"http_status": status},
            )
        ], [], registry

    sources: list[dict[str, Any]] = []
    solutions: list[dict[str, Any]] = []
    for item in data.get("items", []):
        question_id = item.get("question_id")
        sid = f"stackexchange-{question_id}"
        tags = item.get("tags") or []
        title = html.unescape(item.get("title", "Stack Exchange result"))
        link = item.get("link", "")
        answered = bool(item.get("is_answered"))
        accepted = item.get("accepted_answer_id")
        score = int(item.get("score", 0))
        status_name = "needs-official-confirmation"
        if answered and score >= 3:
            status_name = "accepted"
        sources.append(
            source_record(
                source_id=sid,
                title=title,
                url=link,
                category="community",
                base_weight=55,
                scope_match={"languages": tags, "platforms": [], "layers": [], "topics": tags},
                published_at=from_unix(item.get("creation_date")),
                updated_at=from_unix(item.get("last_activity_date")),
                freshness="check-version",
                screening_status=status_name,
                notes="Community Q&A. Use as candidate evidence only.",
                extensions={
                    "question_id": question_id,
                    "accepted_answer_id": accepted,
                    "answer_count": item.get("answer_count"),
                    "question_score": score,
                    "is_answered": answered,
                    "tags": tags,
                },
            )
        )
        summary = f"Community discussion found: {title}"
        solutions.append(
            candidate_solution(
                source_id=sid,
                summary=summary,
                kind="community-workaround",
                status=status_name,
                pros=["May capture a problem already encountered by developers."],
                cons=["Requires official or local verification before implementation."],
                risks=["May be outdated, version-bound, or license-sensitive if copied directly."],
                screening={
                    "authority": "community",
                    "recency": "check last_activity_date",
                    "version_match": "unknown until answer content is reviewed",
                    "reproducibility": "unknown",
                    "security": "unknown",
                    "license": "Stack Overflow content requires attribution under its license terms.",
                    "conflicts": [],
                },
            )
        )
    return sources, solutions, registry


def github_search(query: str, limit: int, timeout: float) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    params = {"q": query, "per_page": str(limit), "sort": "stars", "order": "desc"}
    url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(params)
    data, error, status = request_json(url, timeout)
    registry = [
        extension("repository_full_name", "string", "source", "github", "Repository identity."),
        extension("language", "string", "source", "github", "Primary repository language."),
        extension("stars", "integer", "source", "github", "Popularity signal; not authority."),
        extension("forks", "integer", "source", "github", "Reuse/activity signal; not authority."),
        extension("license", "object", "source", "github", "Repository license metadata."),
        extension("pushed_at", "string", "source", "github", "Recent maintenance signal."),
    ]
    if error:
        return [
            source_record(
                source_id="github-error",
                title="GitHub Repository Search API error",
                url=url,
                category="primary-or-community",
                base_weight=55,
                screening_status="reject",
                notes=error,
                extensions={"http_status": status},
            )
        ], [], registry

    sources: list[dict[str, Any]] = []
    solutions: list[dict[str, Any]] = []
    for item in data.get("items", []):
        repo_id = item.get("id")
        sid = f"github-repo-{repo_id}"
        full_name = item.get("full_name", "")
        repo_url = item.get("html_url", "")
        status_name = "needs-screening"
        license_info = item.get("license")
        sources.append(
            source_record(
                source_id=sid,
                title=full_name or item.get("name", "GitHub repository"),
                url=repo_url,
                category="primary-or-community",
                base_weight=55,
                published_at=item.get("created_at"),
                updated_at=item.get("updated_at") or item.get("pushed_at"),
                freshness="check-version",
                screening_status=status_name,
                notes=normalize_text(item.get("description") or "GitHub repository search result. Treat code as untrusted until reviewed.", 300),
                extensions={
                    "repository_full_name": full_name,
                    "language": item.get("language"),
                    "stars": item.get("stargazers_count"),
                    "forks": item.get("forks_count"),
                    "license": license_info,
                    "pushed_at": item.get("pushed_at"),
                    "archived": item.get("archived"),
                    "disabled": item.get("disabled"),
                },
            )
        )
        solutions.append(
            candidate_solution(
                source_id=sid,
                summary=f"GitHub repository candidate: {full_name or item.get('name', '')}",
                kind="source-code",
                status=status_name,
                pros=["May provide real-world implementation examples or upstream source context."],
                cons=["Repository search is broad; popularity and stars are not proof of correctness."],
                risks=["Public code is untrusted; verify license, security, maintenance, and version fit before reuse."],
                screening={
                    "authority": "candidate source-code evidence only; primary only if this is the relevant upstream repository",
                    "recency": "check pushed_at/updated_at",
                    "version_match": "check tags, releases, docs, and dependency versions",
                    "reproducibility": "requires local review/test",
                    "security": "must review before reuse",
                    "license": "check repository license before copying code",
                    "conflicts": [],
                },
            )
        )
    return sources, solutions, registry


def reddit_search(query: str, limit: int, timeout: float, subreddit: str | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    if subreddit:
        base = f"https://www.reddit.com/r/{urllib.parse.quote(subreddit)}/search.json"
        params = {"q": query, "restrict_sr": "1", "sort": "relevance", "limit": str(limit)}
    else:
        base = "https://www.reddit.com/search.json"
        params = {"q": query, "sort": "relevance", "limit": str(limit)}
    url = base + "?" + urllib.parse.urlencode(params)
    data, error, status = request_json(url, timeout)
    registry = [
        extension("subreddit", "string", "source", "reddit", "Subreddit context affects relevance."),
        extension("score", "integer", "source", "reddit", "Community signal; weak and non-normative."),
        extension("num_comments", "integer", "source", "reddit", "Discussion activity signal."),
        extension("upvote_ratio", "number", "source", "reddit", "Community signal; weak and non-normative."),
    ]
    if error:
        return [
            source_record(
                source_id="reddit-error",
                title="Reddit acquisition error",
                url=url,
                category="community",
                base_weight=35,
                screening_status="reject",
                notes=error,
                extensions={"http_status": status},
            )
        ], [], registry

    sources: list[dict[str, Any]] = []
    solutions: list[dict[str, Any]] = []
    children = data.get("data", {}).get("children", [])
    for child in children[:limit]:
        item = child.get("data", {})
        post_id = item.get("id")
        sid = f"reddit-{post_id}"
        title = item.get("title", "Reddit result")
        permalink = item.get("permalink") or ""
        link = urllib.parse.urljoin("https://www.reddit.com", permalink)
        score = int(item.get("score") or 0)
        comments = int(item.get("num_comments") or 0)
        status_name = "needs-official-confirmation"
        if score >= 10 and comments >= 5:
            status_name = "workaround-only"
        sources.append(
            source_record(
                source_id=sid,
                title=title,
                url=link,
                category="community",
                base_weight=35,
                scope_match={
                    "languages": [],
                    "platforms": [],
                    "layers": [],
                    "topics": [item.get("subreddit", "")],
                },
                published_at=from_unix(item.get("created_utc")),
                updated_at=None,
                freshness="check-version",
                screening_status=status_name,
                notes="Reddit discussion. Use only as weak practical signal.",
                extensions={
                    "subreddit": item.get("subreddit"),
                    "score": score,
                    "num_comments": comments,
                    "upvote_ratio": item.get("upvote_ratio"),
                    "author": item.get("author"),
                },
            )
        )
        solutions.append(
            candidate_solution(
                source_id=sid,
                summary=f"Reddit discussion signal: {title}",
                kind="community-workaround",
                status=status_name,
                pros=["May surface practical developer experience or regressions."],
                cons=["Weak evidence; must not override official or primary sources."],
                risks=["May be anecdotal, outdated, biased, or incomplete."],
                screening={
                    "authority": "community weak signal",
                    "recency": "check post date and comments",
                    "version_match": "unknown",
                    "reproducibility": "unknown",
                    "security": "unknown",
                    "license": "Do not copy substantial content; cite/link if used.",
                    "conflicts": [],
                },
            )
        )
    return sources, solutions, registry


def pypi_project(package: str, timeout: float) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    quoted = urllib.parse.quote(package)
    url = f"https://pypi.org/pypi/{quoted}/json"
    data, error, status = request_json(url, timeout)
    registry = [
        extension("latest_version", "string", "source", "pypi", "Latest package version from PyPI metadata."),
        extension("requires_python", "string", "source", "pypi", "Python version applicability."),
        extension("classifiers", "array[string]", "source", "pypi", "Runtime, license, and topic metadata."),
        extension("project_urls", "object", "source", "pypi", "Official links such as docs, homepage, source, tracker."),
    ]
    if error:
        return [
            source_record(
                source_id=f"pypi-{package}-error",
                title="PyPI JSON API error",
                url=url,
                category="primary",
                base_weight=75,
                screening_status="reject",
                notes=error,
                extensions={"http_status": status},
            )
        ], [], registry

    info = data.get("info", {})
    name = info.get("name") or package
    sid = f"pypi-{re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')}"
    project_urls = info.get("project_urls") or {}
    summary = info.get("summary") or ""
    latest = info.get("version")
    requires_python = info.get("requires_python")
    source = source_record(
        source_id=sid,
        title=f"PyPI project: {name}",
        url=info.get("package_url") or url,
        category="primary",
        base_weight=75,
        scope_match={"languages": ["Python"], "platforms": [], "layers": ["packaging"], "topics": ["dependency metadata"]},
        updated_at=None,
        freshness="current-metadata",
        screening_status="accepted",
        notes=normalize_text(summary, 300),
        extensions={
            "latest_version": latest,
            "requires_python": requires_python,
            "classifiers": info.get("classifiers") or [],
            "project_urls": project_urls,
            "docs_url": info.get("docs_url"),
            "home_page": info.get("home_page"),
            "license": info.get("license"),
        },
    )
    solution = candidate_solution(
        source_id=sid,
        summary=f"Package metadata for {name}: latest={latest}, requires_python={requires_python or 'unspecified'}.",
        kind="documented",
        status="accepted",
        pros=["Primary package registry metadata."],
        cons=["Does not replace project documentation or changelog."],
        risks=["Metadata can be incomplete or maintained separately from docs."],
        version_constraints=[f"latest={latest}"] if latest else [],
        screening={
            "authority": "primary package registry",
            "recency": "current API response",
            "version_match": "check project constraints",
            "reproducibility": "metadata only",
            "security": "does not assess package safety",
            "license": info.get("license") or "unknown",
            "conflicts": [],
        },
    )
    return [source], [solution], registry


def direct_url(urls: list[str], timeout: float, query: str | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    sources: list[dict[str, Any]] = []
    solutions: list[dict[str, Any]] = []
    registry = [
        extension("http_status", "integer", "source", "direct-url", "Fetch status for diagnostics."),
        extension("content_type", "string", "source", "direct-url", "Parser selection and confidence."),
        extension("meta_description", "string", "source", "direct-url", "Short page summary from HTML metadata."),
        extension("extracted_snippets", "array[string]", "source", "direct-url", "Query-relevant snippets extracted from page text."),
    ]
    for idx, url in enumerate(urls, start=1):
        result = fetch_url(url, timeout=timeout)
        domain_source = infer_source_for_url(url)
        category = domain_source.get("category", "blog") if domain_source else "blog"
        base_weight = int(domain_source.get("base_weight", SOURCE_WEIGHTS.get(category, 40))) if domain_source else SOURCE_WEIGHTS.get(category, 40)
        sid_prefix = domain_source.get("source_id", "direct-url") if domain_source else "direct-url"
        sid = f"{sid_prefix}-{idx}"
        if result.error:
            sources.append(
                source_record(
                    source_id=sid,
                    title="Direct URL fetch error",
                    url=url,
                    category=category,
                    base_weight=base_weight,
                    screening_status="reject",
                    notes=result.error,
                    extensions={"http_status": result.status},
                )
            )
            continue
        content_type = result.headers.get("content-type", "")
        text = result.body.decode(detect_charset(content_type), errors="replace")
        title = url
        description = ""
        if "html" in content_type or text.lstrip().startswith("<"):
            parser = SimpleHTMLExtractor()
            parser.feed(text[:1_500_000])
            title = parser.title or parser.meta.get("og:title") or url
            description = parser.description
            snippets = relevant_snippets(parser.text_parts, query)
        else:
            title = url.rsplit("/", 1)[-1] or url
            description = text[:1000]
            snippets = relevant_snippets([text], query)
        officialish = category in {"official", "primary", "official-like-reference"}
        status_name = "accepted" if officialish else "needs-check"
        sources.append(
            source_record(
                source_id=sid,
                title=title,
                url=result.url,
                category=category,
                base_weight=base_weight,
                scope_match=domain_source.get("scopes") if domain_source else None,
                freshness="unknown",
                screening_status=status_name,
                notes=normalize_text(description, 500),
                extensions={
                    "http_status": result.status,
                    "content_type": content_type,
                    "meta_description": normalize_text(description, 500),
                    "extracted_snippets": snippets,
                    "matched_catalog_source": domain_source.get("source_id") if domain_source else None,
                },
            )
        )
        summary_source = first_nonempty(snippets) or description or title
        solutions.append(
            candidate_solution(
                source_id=sid,
                summary=summary_source,
                kind="documented" if officialish else "inferred",
                status=status_name,
                pros=["Directly retrieved source page."],
                cons=["Only page-level metadata/snippet extracted by prototype parser."],
                risks=["Need targeted reading for exact API semantics before implementation."],
                screening={
                    "authority": category,
                    "recency": "unknown unless page metadata says otherwise",
                    "version_match": "unknown until page content is reviewed",
                    "reproducibility": "not applicable",
                    "security": "unknown",
                    "license": "check source page terms before copying text/code",
                    "conflicts": [],
                },
            )
        )
    return sources, solutions, registry


def relevant_snippets(text_parts: list[str], query: str | None, limit: int = 5) -> list[str]:
    if not text_parts:
        return []
    if not query:
        return [normalize_text(part, 500) for part in text_parts[: min(2, len(text_parts))]]
    tokens = [token.lower() for token in re.findall(r"[A-Za-z0-9_+#.:-]{3,}", query)]
    if not tokens:
        return [normalize_text(part, 500) for part in text_parts[: min(2, len(text_parts))]]
    scored: list[tuple[int, str]] = []
    for part in text_parts:
        low = part.lower()
        score = sum(1 for token in tokens if token in low)
        if score:
            scored.append((score, part))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [normalize_text(part, 500) for _, part in scored[:limit]]


def infer_source_for_url(url: str) -> dict[str, Any] | None:
    host = urllib.parse.urlparse(url).netloc.lower()
    for source in load_catalog().get("sources", []):
        base_host = urllib.parse.urlparse(source.get("base_url", "")).netloc.lower()
        if base_host and (host == base_host or host.endswith("." + base_host)):
            return source
    return None


def detect_charset(content_type: str) -> str:
    match = re.search(r"charset=([\w.-]+)", content_type or "", re.I)
    return match.group(1) if match else "utf-8"


def from_unix(value: Any) -> str | None:
    if not value:
        return None
    try:
        return dt.datetime.fromtimestamp(int(value), tz=dt.UTC).date().isoformat()
    except (TypeError, ValueError, OSError):
        return None


def extension(field: str, type_: str, scope: str, introduced_by: str, reason: str) -> dict[str, Any]:
    return {
        "field": field,
        "type": type_,
        "scope": scope,
        "introduced_by_source_id": introduced_by,
        "reason": reason,
        "stability": "experimental",
        "approved": False,
    }


def merge_registry(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    merged: list[dict[str, Any]] = []
    for entry in entries:
        key = (entry.get("field", ""), entry.get("scope", ""))
        if key in seen:
            continue
        seen.add(key)
        merged.append(entry)
    return merged


def base_document(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "question": {
            "user_request": args.user_request or args.query or "",
            "normalized_question": args.query or args.user_request or "",
            "languages": args.language or [],
            "platforms": args.platform or [],
            "runtimes": args.runtime or [],
            "versions": args.version or [],
            "project_constraints": args.constraint or [],
        },
        "sources": [],
        "candidate_solutions": [],
        "decision": {
            "selected_solution_id": "",
            "rationale": "Acquisition only. A model must screen and decide before implementation.",
            "decisive_source_ids": [],
            "resolved_conflicts": [],
            "rejected_options": [],
        },
        "application": {
            "affected_files": [],
            "implementation_notes": "",
            "verification": [],
            "residual_limits": [],
        },
        "extension_registry": [],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Acquire source evidence and emit a-hydrae-developing-skills normalizer JSON.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Examples:
              source_search.py --query "CreateFileW FILE_FLAG_OVERLAPPED" --provider stackexchange
              source_search.py --provider pypi --pypi-package requests
              source_search.py --provider direct-url --url https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew
            """
        ),
    )
    parser.add_argument("--query", help="Technical query to search for.")
    parser.add_argument("--user-request", help="Original user request, if different from query.")
    parser.add_argument("--provider", action="append", choices=["stackexchange", "github", "reddit", "pypi", "direct-url"], help="Provider to run. Repeatable.")
    parser.add_argument("--url", action="append", default=[], help="Direct URL to fetch. Repeatable.")
    parser.add_argument("--pypi-package", action="append", default=[], help="PyPI package name. Repeatable.")
    parser.add_argument("--stackexchange-site", default="stackoverflow", help="Stack Exchange site, default: stackoverflow.")
    parser.add_argument("--subreddit", help="Restrict Reddit search to a subreddit, e.g. cpp or Python.")
    parser.add_argument("--limit", type=int, default=5, help="Max results per search provider.")
    parser.add_argument("--timeout", type=float, default=12.0, help="Network timeout in seconds.")
    parser.add_argument("--language", action="append", default=[])
    parser.add_argument("--platform", action="append", default=[])
    parser.add_argument("--runtime", action="append", default=[])
    parser.add_argument("--version", action="append", default=[])
    parser.add_argument("--constraint", action="append", default=[])
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    args = parser.parse_args(argv)
    if not args.provider:
        args.provider = ["stackexchange"] if args.query else []
        if args.url:
            args.provider.append("direct-url")
        if args.pypi_package:
            args.provider.append("pypi")
    if not args.provider:
        parser.error("provide --provider, --query, --url, or --pypi-package")
    if any(p in {"stackexchange", "github", "reddit"} for p in args.provider) and not args.query:
        parser.error("--query is required for stackexchange/github/reddit providers")
    if "direct-url" in args.provider and not args.url:
        parser.error("--url is required for direct-url provider")
    if "pypi" in args.provider and not args.pypi_package:
        parser.error("--pypi-package is required for pypi provider")
    return args


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    doc = base_document(args)
    registry: list[dict[str, Any]] = []

    for provider in args.provider:
        if provider == "stackexchange":
            sources, solutions, ext = stackexchange_search(args.query, args.limit, args.timeout, args.stackexchange_site)
        elif provider == "github":
            sources, solutions, ext = github_search(args.query, args.limit, args.timeout)
        elif provider == "reddit":
            sources, solutions, ext = reddit_search(args.query, args.limit, args.timeout, args.subreddit)
        elif provider == "pypi":
            sources, solutions, ext = [], [], []
            for package in args.pypi_package:
                p_sources, p_solutions, p_ext = pypi_project(package, args.timeout)
                sources.extend(p_sources)
                solutions.extend(p_solutions)
                ext.extend(p_ext)
        elif provider == "direct-url":
            sources, solutions, ext = direct_url(args.url, args.timeout, args.query)
        else:
            raise AssertionError(provider)
        doc["sources"].extend(sources)
        doc["candidate_solutions"].extend(solutions)
        registry.extend(ext)

    doc["extension_registry"] = merge_registry(registry)
    json.dump(doc, sys.stdout, indent=2 if args.pretty else None, sort_keys=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
