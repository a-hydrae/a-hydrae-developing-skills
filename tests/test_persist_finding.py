import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PERSIST_PATH = ROOT / "a-hydrae-developing-skills" / "scripts" / "persist_finding.py"


def load_persist_finding():
    spec = importlib.util.spec_from_file_location("persist_finding", PERSIST_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PersistFindingTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_persist_finding()

    def sample_doc(self):
        return {
            "question": {
                "user_request": "CreateFileW FILE_FLAG_OVERLAPPED",
                "normalized_question": "CreateFileW FILE_FLAG_OVERLAPPED",
                "languages": ["C++"],
                "platforms": ["Windows"],
                "runtimes": [],
                "versions": [],
                "project_constraints": [],
            },
            "sources": [
                {
                    "source_id": "microsoft-learn-1",
                    "title": "CreateFileW function",
                    "url": "https://learn.microsoft.com/example",
                    "category": "official",
                    "base_weight": 100,
                    "screening_status": "accepted",
                }
            ],
            "candidate_solutions": [
                {
                    "id": "solution-microsoft-learn-1",
                    "summary": "Use CreateFileW documented signature.",
                    "source_ids": ["microsoft-learn-1"],
                    "type": "documented",
                    "status": "accepted",
                    "version_constraints": [],
                    "risks": [],
                    "screening": {
                        "authority": "official",
                        "recency": "current enough",
                        "version_match": "Windows API",
                        "reproducibility": "not applicable",
                        "security": "review required",
                        "license": "docs",
                    },
                }
            ],
            "decision": {
                "selected_solution_id": "solution-microsoft-learn-1",
                "rationale": "Official source.",
                "decisive_source_ids": ["microsoft-learn-1"],
                "resolved_conflicts": [],
                "rejected_options": [],
            },
            "application": {
                "affected_files": [],
                "implementation_notes": "Use documented flags.",
                "verification": ["unit test placeholder"],
                "residual_limits": [],
            },
            "extension_registry": [],
        }

    def test_stable_id_is_stable(self):
        doc = self.sample_doc()
        self.assertEqual(self.mod.stable_id(doc), self.mod.stable_id(doc))

    def test_persist_creates_note_json_and_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "finding.json"
            wiki = Path(tmp) / "wiki"
            input_path.write_text(json.dumps(self.sample_doc()), encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                rc = self.mod.main(["--input", str(input_path), "--wiki", str(wiki), "--print-path"])
            self.assertEqual(rc, 0)

            notes = list((wiki / "resolved" / "cpp").glob("*.md"))
            json_files = list((wiki / "data" / "findings").glob("*.json"))
            self.assertEqual(len(notes), 1)
            self.assertEqual(len(json_files), 1)
            note = notes[0].read_text(encoding="utf-8")
            index = (wiki / "resolved" / "Index.md").read_text(encoding="utf-8")
            self.assertIn('status: "verified"', note)
            self.assertIn("CreateFileW FILE_FLAG_OVERLAPPED", note)
            self.assertIn("[[resolved/cpp/", index)

    def test_refuses_overwrite_without_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = Path(tmp) / "finding.json"
            wiki = Path(tmp) / "wiki"
            input_path.write_text(json.dumps(self.sample_doc()), encoding="utf-8")
            self.assertEqual(self.mod.main(["--input", str(input_path), "--wiki", str(wiki)]), 0)
            with redirect_stderr(io.StringIO()):
                self.assertEqual(self.mod.main(["--input", str(input_path), "--wiki", str(wiki)]), 2)


if __name__ == "__main__":
    unittest.main()
