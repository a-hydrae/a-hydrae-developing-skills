import importlib.util
import io
import json
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_SEARCH_PATH = ROOT / "a-hydrae-developing-skills" / "scripts" / "source_search.py"


def load_source_search():
    spec = importlib.util.spec_from_file_location("source_search", SOURCE_SEARCH_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SourceSearchTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_source_search()

    def test_catalog_json_contains_required_sources(self):
        catalog = self.mod.load_catalog()
        source_ids = {source["source_id"] for source in catalog["sources"]}
        self.assertIn("microsoft-learn", source_ids)
        self.assertIn("stackexchange", source_ids)
        self.assertIn("github", source_ids)
        self.assertIn("pypi", source_ids)
        github = next(source for source in catalog["sources"] if source["source_id"] == "github")
        self.assertEqual(github["base_weight"], 55)

    def test_untrusted_defaults(self):
        self.assertFalse(
            self.mod.default_untrusted(
                "microsoft-learn-1",
                "official",
                "https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew",
            )
        )
        self.assertFalse(
            self.mod.default_untrusted(
                "python-docs-1",
                "official",
                "https://docs.python.org/3/library/asyncio-task.html",
            )
        )
        self.assertTrue(
            self.mod.default_untrusted(
                "github-1",
                "primary-or-community",
                "https://github.com/python/cpython",
            )
        )
        self.assertTrue(
            self.mod.default_untrusted(
                "stackexchange-1",
                "community",
                "https://stackoverflow.com/questions/1/example",
            )
        )

    def test_direct_url_extracts_catalog_scope_and_snippets(self):
        html = b"""
        <html>
          <head>
            <title>CreateFileW function (fileapi.h) - Win32 apps</title>
            <meta name="description" content="Creates or opens a file or I/O device.">
          </head>
          <body>
            <main>
              <p>HANDLE CreateFileW LPCWSTR lpFileName DWORD dwFlagsAndAttributes.</p>
              <p>Use FILE_FLAG_OVERLAPPED for asynchronous file operations.</p>
            </main>
          </body>
        </html>
        """

        def fake_fetch(url, timeout):
            return self.mod.FetchResult(
                url=url,
                status=200,
                headers={"content-type": "text/html; charset=utf-8"},
                body=html,
            )

        original_fetch = self.mod.fetch_url
        self.mod.fetch_url = fake_fetch
        try:
            sources, solutions, registry = self.mod.direct_url(
                ["https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew"],
                timeout=1,
                query="CreateFileW FILE_FLAG_OVERLAPPED",
            )
        finally:
            self.mod.fetch_url = original_fetch

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["category"], "official")
        self.assertEqual(sources[0]["screening_status"], "accepted")
        self.assertFalse(sources[0]["untrusted"])
        self.assertEqual(sources[0]["extensions"]["matched_catalog_source"], "microsoft-learn")
        self.assertTrue(sources[0]["extensions"]["extracted_snippets"])
        self.assertEqual(solutions[0]["type"], "documented")
        self.assertTrue(any(item["field"] == "extracted_snippets" for item in registry))

    def test_pypi_project_normalizes_metadata(self):
        payload = {
            "info": {
                "name": "example-pkg",
                "version": "1.2.3",
                "summary": "Example package.",
                "requires_python": ">=3.11",
                "package_url": "https://pypi.org/project/example-pkg/",
                "classifiers": ["Programming Language :: Python :: 3"],
                "project_urls": {"Source": "https://example.test/source"},
                "license": "MIT",
            }
        }

        def fake_request_json(url, timeout):
            return payload, None, 200

        original_request_json = self.mod.request_json
        self.mod.request_json = fake_request_json
        try:
            sources, solutions, registry = self.mod.pypi_project("example-pkg", timeout=1)
        finally:
            self.mod.request_json = original_request_json

        self.assertEqual(sources[0]["source_id"], "pypi-example-pkg")
        self.assertTrue(sources[0]["untrusted"])
        self.assertEqual(sources[0]["extensions"]["latest_version"], "1.2.3")
        self.assertEqual(sources[0]["extensions"]["requires_python"], ">=3.11")
        self.assertEqual(solutions[0]["status"], "accepted")
        self.assertTrue(any(item["field"] == "latest_version" for item in registry))

    def test_github_search_uses_repositories_not_issues(self):
        captured = {}
        payload = {
            "items": [
                {
                    "id": 123,
                    "full_name": "example/windows-service",
                    "name": "windows-service",
                    "html_url": "https://github.com/example/windows-service",
                    "description": "Example Windows service implementation.",
                    "created_at": "2026-01-01T00:00:00Z",
                    "updated_at": "2026-02-01T00:00:00Z",
                    "pushed_at": "2026-02-02T00:00:00Z",
                    "language": "C#",
                    "stargazers_count": 42,
                    "forks_count": 7,
                    "license": {"key": "mit", "name": "MIT License"},
                    "archived": False,
                    "disabled": False,
                }
            ]
        }

        def fake_request_json(url, timeout):
            captured["url"] = url
            return payload, None, 200

        original_request_json = self.mod.request_json
        self.mod.request_json = fake_request_json
        try:
            sources, solutions, registry = self.mod.github_search("windows service", limit=1, timeout=1)
        finally:
            self.mod.request_json = original_request_json

        self.assertIn("/search/repositories?", captured["url"])
        self.assertNotIn("/search/issues?", captured["url"])
        self.assertIn("sort=stars", captured["url"])
        self.assertIn("order=desc", captured["url"])
        self.assertEqual(sources[0]["source_id"], "github-repo-123")
        self.assertEqual(sources[0]["title"], "example/windows-service")
        self.assertTrue(sources[0]["untrusted"])
        self.assertEqual(sources[0]["extensions"]["language"], "C#")
        self.assertEqual(solutions[0]["type"], "source-code")
        self.assertTrue(any(item["field"] == "repository_full_name" for item in registry))

    def test_cli_error_without_provider_or_inputs(self):
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                self.mod.parse_args([])

    def test_normalizer_output_is_json_serializable(self):
        args = self.mod.parse_args(["--provider", "pypi", "--pypi-package", "example", "--language", "Python"])
        doc = self.mod.base_document(args)
        json.dumps(doc)


if __name__ == "__main__":
    unittest.main()
