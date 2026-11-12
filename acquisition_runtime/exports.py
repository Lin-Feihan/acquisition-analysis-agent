"""DOCX layout adapted from the existing due-diligence agent."""
import re
import subprocess
import sys
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

def set_cell_shading(
    cell,
    fill="E9EDF2"
):
    tc_pr = (
        cell._tc
        .get_or_add_tcPr()
    )

    shading = OxmlElement(
        "w:shd"
    )

    shading.set(
        qn("w:fill"),
        fill
    )

    tc_pr.append(
        shading
    )


def set_repeat_table_header(row):

    tr_pr = (
        row._tr
        .get_or_add_trPr()
    )

    tbl_header = OxmlElement(
        "w:tblHeader"
    )

    tbl_header.set(
        qn("w:val"),
        "true"
    )

    tr_pr.append(
        tbl_header
    )


def format_run(
    run,
    font_size=10.5,
    bold=False
):

    run.font.name = "Arial"

    run.font.size = Pt(
        font_size
    )

    run.bold = bold


def add_inline_text(
    paragraph,
    text,
    font_size=10.5
):

    parts = re.split(
        r"(\*\*.*?\*\*)",
        text
    )

    for part in parts:

        if not part:
            continue

        if (
            part.startswith("**")
            and part.endswith("**")
        ):

            run = paragraph.add_run(
                part[2:-2]
            )

            format_run(
                run,
                font_size,
                True
            )

        else:

            run = paragraph.add_run(
                part
            )

            format_run(
                run,
                font_size
            )

def configure_document(document):

    section = (
        document.sections[0]
    )

    section.top_margin = Inches(
        0.7
    )

    section.bottom_margin = Inches(
        0.7
    )

    section.left_margin = Inches(
        0.7
    )

    section.right_margin = Inches(
        0.7
    )

    normal = (
        document.styles[
            "Normal"
        ]
    )

    normal.font.name = "Arial"
    normal.font.size = Pt(
        10.5
    )


def is_table_separator(line):

    stripped = line.strip()

    if not (
        stripped.startswith("|")
        and stripped.endswith("|")
    ):
        return False

    cells = [
        x.strip()
        for x in (
            stripped
            .strip("|")
            .split("|")
        )
    ]

    for cell in cells:

        if not re.fullmatch(
            r":?-{3,}:?",
            cell
        ):
            return False

    return True


def parse_table_row(line):

    return [
        x.strip()
        for x in (
            line
            .strip()
            .strip("|")
            .split("|")
        )
    ]


def add_table(
    document,
    rows
):

    if not rows:
        return

    columns = max(
        len(row)
        for row in rows
    )

    table = document.add_table(
        rows=len(rows),
        cols=columns
    )

    table.style = (
        "Table Grid"
    )

    for row_index, row_data in enumerate(
        rows
    ):

        row = table.rows[
            row_index
        ]

        if row_index == 0:
            set_repeat_table_header(
                row
            )

        for col_index in range(
            columns
        ):

            cell = (
                row.cells[
                    col_index
                ]
            )

            text = (
                row_data[col_index]
                if col_index < len(row_data)
                else ""
            )

            paragraph = (
                cell.paragraphs[0]
            )

            add_inline_text(
                paragraph,
                text,
                8
            )

            if row_index == 0:

                set_cell_shading(
                    cell
                )

    document.add_paragraph()


def add_heading(
    document,
    text,
    level
):

    paragraph = document.add_heading(
        text,
        level=min(
            level,
            4
        )
    )

    return paragraph


def markdown_to_docx(
    report,
    docx_path
):

    document = Document()

    configure_document(
        document
    )

    lines = report.splitlines()

    index = 0

    while index < len(lines):

        line = (
            lines[index]
            .rstrip()
        )

        if not line.strip():

            index += 1
            continue


        heading = re.match(
            r"^(#{1,6})\s+(.+)$",
            line
        )

        if heading:

            level = len(
                heading.group(1)
            )

            add_heading(
                document,
                heading.group(2),
                level
            )

            index += 1
            continue


        if (
            line.strip().startswith("|")
            and index + 1 < len(lines)
            and is_table_separator(
                lines[index + 1]
            )
        ):

            rows = [
                parse_table_row(
                    line
                )
            ]

            index += 2

            while (
                index < len(lines)
                and lines[index]
                .strip()
                .startswith("|")
            ):

                rows.append(
                    parse_table_row(
                        lines[index]
                    )
                )

                index += 1


            add_table(
                document,
                rows
            )

            continue


        if line.startswith("- "):

            paragraph = document.add_paragraph(
                style="List Bullet"
            )

            add_inline_text(
                paragraph,
                line[2:]
            )

            index += 1
            continue


        paragraph = document.add_paragraph()

        add_inline_text(
            paragraph,
            line
        )

        index += 1


    document.save(
        str(docx_path)
    )



def export_pdf(docx_path, pdf_path):
    """Optional Word-based conversion; bounded and isolated from core output saving."""
    subprocess.run([sys.executable, "-c",
                    "from docx2pdf import convert; import sys; convert(sys.argv[1], sys.argv[2])",
                    str(docx_path), str(pdf_path)],
                   check=True, timeout=120, capture_output=True)
    if not pdf_path.is_file():
        raise RuntimeError("PDF conversion did not produce a file.")
