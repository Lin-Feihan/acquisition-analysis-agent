"""Persist core outputs before attempting optional document exports."""
import json
from pathlib import Path


def write_json(path, data):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def save_report(result, output_directory, *, save_docx=True, save_pdf=False):
    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    markdown = directory / "report.md"
    markdown.write_text(result.text, encoding="utf-8")
    evidence = directory / "evidence.json"
    # Core outputs are required. Evidence write failures must fail the run.
    write_json(evidence, {"provider": result.provider, "citations": result.citations,
                          "sources": result.sources, "metadata": result.metadata})
    warnings = []
    if not result.citations:
        warnings.append("No structured inline URL citations were returned; review factual support manually.")
    if not result.sources:
        warnings.append("No structured sources were returned; this report has not been independently verified.")
    paths = {"markdown": str(markdown), "evidence": str(evidence), "docx": None, "pdf": None}
    if save_docx or save_pdf:
        docx_path = directory / "report.docx"
        try:
            from .exports import markdown_to_docx
            markdown_to_docx(result.text, docx_path)
            paths["docx"] = str(docx_path)
        except Exception as exc:
            warnings.append(f"DOCX export unavailable ({type(exc).__name__}); core outputs are preserved.")
        if save_pdf:
            if not paths["docx"]:
                warnings.append("PDF export skipped because DOCX export failed.")
            else:
                try:
                    from .exports import export_pdf
                    pdf_path = directory / "report.pdf"
                    export_pdf(docx_path, pdf_path)
                    paths["pdf"] = str(pdf_path)
                except Exception as exc:
                    warnings.append(f"PDF export unavailable ({type(exc).__name__}); core outputs are preserved.")
    paths["warnings"] = warnings
    return paths
