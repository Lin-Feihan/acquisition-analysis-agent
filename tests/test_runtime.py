import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from acquisition_runtime.output_handler import save_report
from acquisition_runtime.prompt_builder import build_prompt
from acquisition_runtime.providers import OpenAIResearchProvider, ResearchResult, parse_response
from acquisition_runtime.runner import execute_run
from acquisition_runtime.settings import validate_settings

ROOT = Path(__file__).resolve().parents[1]


def settings(role):
    return {"target_company": "Target B", "acquirer_company" if role == "acquirer" else "buyer_company": "Buyer A",
            "research_cutoff_date": "2026-11-08"}


class FakeProvider:
    provider_name = "test-only"
    model = "fake-not-a-research-model"

    def __init__(self, error=None):
        self.prompts = []
        self.error = error

    def run(self, prompt):
        self.prompts.append(prompt)
        if self.error:
            raise self.error
        return ResearchResult("# TEST ONLY\nNot a real research report.", self.provider_name,
                              metadata={"model": self.model, "usage": {"input_tokens": 10}})


class RuntimeTests(unittest.TestCase):
    def test_questions_injected_and_agents_independent(self):
        for role in ("acquirer", "target"):
            root = ROOT / "agents" / role
            manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
            task = settings(role)
            questions = [f for f in manifest["settings_schema"]["fields"] if f["type"] == "longtext" and f["id"] != "additional_context"]
            self.assertEqual(len(questions), 9)
            for index, field in enumerate(questions):
                task[field["id"]] = "ANSWER_" + str(index)
            prompt = build_prompt(root, task)
            for index in range(9):
                self.assertIn("ANSWER_" + str(index), prompt)
            self.assertNotIn("{{output_specification}}", prompt)
            self.assertIn("1. Executive Summary", prompt)
            if role == "acquirer":
                self.assertIn("Stage 6 — Acquisition Returns", prompt)
                self.assertNotIn("Stage 6 — Strategic Alternatives", prompt)
            else:
                self.assertIn("Stage 6 — Strategic Alternatives", prompt)
                self.assertNotIn("Stage 6 — Acquisition Returns", prompt)

    def test_defaults_and_explicit_unknown(self):
        root = ROOT / "agents/acquirer"
        result = validate_settings(root, {**settings("acquirer"), "integration_priorities": "Unknown"})
        self.assertEqual(result["valuation_date"], "2026-11-08")
        self.assertEqual(result["integration_priorities"], "Unknown")
        self.assertEqual(result["funding_and_return_requirements"], "Not specified")

    def test_invalid_input(self):
        root = ROOT / "agents/acquirer"
        for change in ({"target_company": " "}, {"research_cutoff_date": "2026-02-30"},
                       {"research_cutoff_date": "20261108"}, {"proposed_price_and_terms": 10},
                       {"perspective": "target"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_settings(root, {**settings("acquirer"), **change})

    def test_user_braces_are_not_reexpanded(self):
        prompt = build_prompt(ROOT / "agents/acquirer", {**settings("acquirer"),
                               "additional_context": "A supplied formula: {{target_company}}"})
        self.assertIn("A supplied formula: {{target_company}}", prompt)

    def test_schema_template_mismatch(self):
        import shutil
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ("manifest.json", "prompt.md", "output_spec.md"):
                shutil.copy(ROOT / "agents/acquirer" / name, root / name)
            path = root / "prompt.md"
            path.write_text(path.read_text(encoding="utf-8") + "\n{{missing_variable}}", encoding="utf-8")
            with self.assertRaises(ValueError):
                build_prompt(root, settings("acquirer"))

    def test_dry_run_has_no_provider_call(self):
        fake = FakeProvider()
        with tempfile.TemporaryDirectory() as temp:
            out = execute_run(ROOT / "agents/target", settings("target"), fake,
                              output_directory=temp, dry_run=True)
            self.assertEqual(fake.prompts, [])
            self.assertEqual(out["record"]["status"], "prepared")
            self.assertFalse((Path(out["directory"]) / "report.md").exists())
            self.assertTrue((Path(out["directory"]) / "prepared_prompt.md").exists())

    def test_complete_run_outputs_and_isolation(self):
        with tempfile.TemporaryDirectory() as temp:
            outputs = []
            for role in ("acquirer", "target", "acquirer"):
                out = execute_run(ROOT / "agents" / role, settings(role), FakeProvider(),
                                  output_directory=temp, save_docx=False)
                directory = Path(out["directory"])
                self.assertEqual(out["record"]["status"], "completed")
                for name in ("settings.json", "run.json", "evidence.json", "report.md"):
                    self.assertTrue((directory / name).is_file())
                self.assertIsNone(out["record"]["actual_cost_micro"])
                self.assertTrue(out["record"]["warnings"])
                outputs.append(out["directory"])
            self.assertEqual(len(set(outputs)), 3)

    def test_research_failure_is_recorded_and_redacted(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {"OPENAI_API_KEY": "private-test-key"}):
            with self.assertRaises(RuntimeError):
                execute_run(ROOT / "agents/acquirer", settings("acquirer"),
                            FakeProvider(RuntimeError("private-test-key")), output_directory=temp)
            record = json.loads(next(Path(temp).rglob("run.json")).read_text())
            self.assertEqual(record["status"], "failed")
            self.assertNotIn("private-test-key", record["error"])

    def test_core_evidence_failure_fails_run(self):
        from acquisition_runtime.output_handler import write_json as real_write
        def fail_evidence(path, value):
            if Path(path).name == "evidence.json":
                raise OSError("Disk full")
            return real_write(path, value)
        with tempfile.TemporaryDirectory() as temp:
            with patch("acquisition_runtime.output_handler.write_json", side_effect=fail_evidence):
                with self.assertRaises(OSError):
                    execute_run(ROOT / "agents/acquirer", settings("acquirer"), FakeProvider(),
                                output_directory=temp, save_docx=False)
            record = json.loads(next(Path(temp).rglob("run.json")).read_text())
            self.assertEqual(record["status"], "failed")
            self.assertTrue(next(Path(temp).rglob("report.md")).exists())

    def test_optional_export_failure_preserves_core(self):
        with tempfile.TemporaryDirectory() as temp:
            # Inject a broken exporter without requiring optional dependencies.
            exporter = SimpleNamespace(markdown_to_docx=lambda *a: (_ for _ in ()).throw(RuntimeError("Export failed")))
            with patch.dict(sys.modules, {"acquisition_runtime.exports": exporter}):
                out = save_report(ResearchResult("Report", "test"), temp, save_pdf=True)
            self.assertTrue(Path(out["markdown"]).exists())
            self.assertTrue(Path(out["evidence"]).exists())
            self.assertIsNone(out["docx"])
            self.assertIsNone(out["pdf"])
            self.assertTrue(any("DOCX export" in w for w in out["warnings"]))

    def test_cli_preview_for_both_agents(self):
        with tempfile.TemporaryDirectory() as temp:
            for role in ("acquirer", "target"):
                done = subprocess.run([sys.executable, "-m", f"agents.{role}.runtime.main", "--dry-run",
                        "--settings", f"agents/{role}/examples/hypothetical.json", "--output", temp],
                        cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
                self.assertIn("no research call", done.stdout)


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"OPENAI_BASE_URL": "", "RESEARCH_MODEL": ""})
        self.env.start()
        self.addCleanup(self.env.stop)

    def fake_client(self, responses):
        values = iter(responses)
        calls = []
        def create(**kwargs):
            calls.append(kwargs)
            return next(values)
        return SimpleNamespace(responses=SimpleNamespace(create=create,
            retrieve=lambda *a, **kw: next(values), cancel=lambda *a: None)), calls

    def test_native_background_polling(self):
        client, calls = self.fake_client([{"id": "r1", "status": "queued"},
                                        {"id": "r1", "status": "completed", "output_text": "Done"}])
        provider = OpenAIResearchProvider("test", {"model": "test-model"}, client=client, sleep=lambda _: None)
        self.assertEqual(provider.run("Task").text, "Done")
        self.assertTrue(calls[0]["background"])

    def test_gateway_is_synchronous_and_preserves_usage(self):
        with patch.dict(os.environ, {"OPENAI_BASE_URL": "https://example.invalid/v1", "RESEARCH_MODEL": "gateway-model"}):
            client, calls = self.fake_client([{"output_text": "Done", "usage": {"input_tokens": 123}}])
            provider = OpenAIResearchProvider("test", {}, client=client)
            result = provider.run("Task")
            self.assertEqual(result.provider, "commonstack")
            self.assertEqual(result.metadata["usage"]["input_tokens"], 123)
            self.assertNotIn("background", calls[0])
            self.assertEqual(calls[0]["tools"], [{"type": "web_search"}])
            self.assertIsNone(result.metadata["actual_cost_micro"])

    def test_incomplete_failed_and_empty_responses(self):
        for response in ({"status": "failed"}, {"status": "incomplete", "output_text": "Partial"},
                         {"status": "completed", "output_text": ""}):
            client, _ = self.fake_client([response])
            with self.subTest(response=response), self.assertRaises((RuntimeError, ValueError)):
                OpenAIResearchProvider("test", {"model": "test"}, client=client).run("Task")

    def test_timeout_attempts_cancellation(self):
        client, _ = self.fake_client([{"id": "r1", "status": "in_progress"}])
        clock = iter([0, 2])
        cancelled = []
        client.responses.cancel = cancelled.append
        provider = OpenAIResearchProvider("test", {"model": "test", "timeout_seconds": 1}, client=client,
                                           clock=lambda: next(clock))
        with self.assertRaises(TimeoutError):
            provider.run("Task")
        self.assertEqual(cancelled, ["r1"])

    def test_parse_citations_sources_and_tool_evidence(self):
        response = {"status": "completed", "output": [
            {"type": "message", "id": "m", "content": [{"type": "output_text", "text": "Result",
             "annotations": [{"type": "url_citation", "url": "https://example.com", "title": "Source"}]}]},
            {"type": "web_search_call", "action": {"sources": [{"url": "https://example.com"}]}},
            {"type": "code_interpreter_call", "code": "1+1", "outputs": [{"type": "logs", "logs": "2"}]},
            {"type": "reasoning", "summary": [{"text": "Do not store this"}]}
        ]}
        result = parse_response(response, "test", "test")
        self.assertEqual(result.text, "Result")
        self.assertEqual(len(result.citations), 1)
        self.assertEqual(len(result.sources), 1)
        self.assertNotIn("Do not store this", json.dumps(result.metadata))
        self.assertIn("1+1", json.dumps(result.metadata))


if __name__ == "__main__":
    unittest.main()
