import importlib.util
from pathlib import Path
import tempfile
import unittest


@unittest.skipUnless(importlib.util.find_spec("docx"), "Optional python-docx is not installed")
class ExportTests(unittest.TestCase):
    def test_docx_preserves_headings_tables_and_source_urls(self):
        from docx import Document
        from acquisition_runtime.output_handler import save_report
        from acquisition_runtime.providers import ResearchResult
        text = "# Test report\n\n## 1. Executive Summary\n\nA **supported** statement.\n\n| Input | Value |\n|---|---|\n| Revenue | 10 |\n\nSource: https://example.com/filing\n"
        with tempfile.TemporaryDirectory() as temp:
            result = save_report(ResearchResult(text, "test-only"), temp, save_docx=True)
            self.assertIsNotNone(result["docx"])
            document = Document(result["docx"])
            self.assertEqual(document.tables[0].cell(1, 1).text, "10")
            paragraphs = "\n".join(p.text for p in document.paragraphs)
            self.assertIn("Executive Summary", paragraphs)
            self.assertIn("https://example.com/filing", paragraphs)
            self.assertTrue(Path(result["markdown"]).exists())


if __name__ == "__main__":
    unittest.main()
