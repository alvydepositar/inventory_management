from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[2]
SOURCE_MD = ROOT / "docs" / "User_Guide_and_Manual_Rewritten.md"
PDF_READY_MD = ROOT / "docs" / "User_Guide_and_Manual_PDF_Ready.md"
OUTPUT_PDF = ROOT / "docs" / "User_Guide_and_Manual_PDF_Ready.pdf"


@dataclass
class Styles:
    title: ParagraphStyle
    subtitle: ParagraphStyle
    h1: ParagraphStyle
    h2: ParagraphStyle
    h3: ParagraphStyle
    body: ParagraphStyle
    list_item: ParagraphStyle
    small: ParagraphStyle
    toc_item: ParagraphStyle


def build_styles() -> Styles:
    base = getSampleStyleSheet()
    return Styles(
        title=ParagraphStyle(
            "DocTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=30,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        subtitle=ParagraphStyle(
            "DocSubtitle",
            parent=base["Heading2"],
            fontName="Helvetica",
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        h1=ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=24,
            spaceBefore=12,
            spaceAfter=6,
        ),
        h2=ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            spaceBefore=10,
            spaceAfter=4,
        ),
        h3=ParagraphStyle(
            "H3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            spaceBefore=8,
            spaceAfter=4,
        ),
        body=ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=14,
            spaceBefore=1,
            spaceAfter=4,
        ),
        list_item=ParagraphStyle(
            "ListItem",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=14,
            leftIndent=14,
            spaceBefore=0,
            spaceAfter=2,
        ),
        small=ParagraphStyle(
            "Small",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#4a4a4a"),
        ),
        toc_item=ParagraphStyle(
            "TOCItem",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=14,
            leftIndent=12,
            spaceAfter=2,
        ),
    )


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def extract_cover_block(source_text: str) -> tuple[list[str], list[str]]:
    lines = source_text.splitlines()
    cover: list[str] = []
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith("## Revision History"):
            body_start = i
            break
        cover.append(line)
    return cover, lines[body_start:]


def build_toc_entries(lines: Iterable[str]) -> list[str]:
    entries: list[str] = []
    for line in lines:
        m = re.match(r"^(##)\s+(.*)$", line.strip())
        if not m:
            continue
        heading = m.group(2).strip()
        if heading == "Revision History":
            continue
        if heading.startswith("Part ") or re.match(r"^\d+\.", heading):
            entries.append(heading)
    return entries


def compose_pdf_ready_markdown(source_text: str) -> str:
    cover_lines, body_lines = extract_cover_block(source_text)
    toc_entries = build_toc_entries(body_lines)

    out: list[str] = []
    out.append("<!-- COVER PAGE -->")
    out.extend(cover_lines)
    out.append("")
    out.append("\\newpage")
    out.append("")
    out.append("<!-- TABLE OF CONTENTS -->")
    out.append("## Table of Contents")
    out.append("")
    for i, entry in enumerate(toc_entries, start=1):
        out.append(f"{i}. {entry}")
    out.append("")
    out.append("\\newpage")
    out.append("")

    for line in body_lines:
        if line.startswith("## Part A:") or line.startswith("## Part B:") or line.startswith("## 12. Appendix") or line.startswith("## 13. Appendix"):
            out.append("\\newpage")
            out.append("")
        out.append(line)

    return "\n".join(out).rstrip() + "\n"


def clean_inline(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return text


def parse_markdown_table(block_lines: list[str]) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in block_lines:
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(re.fullmatch(r"[:\- ]+", c or "") for c in cells):
            continue
        rows.append(cells)
    return rows


def markdown_to_story(md_text: str, styles: Styles):
    story = []
    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            story.append(Spacer(1, 3))
            i += 1
            continue

        if stripped == "\\newpage":
            story.append(PageBreak())
            i += 1
            continue

        if stripped.startswith("<!--"):
            i += 1
            continue

        if stripped == "---":
            story.append(Spacer(1, 6))
            i += 1
            continue

        if stripped.startswith("|"):
            table_block: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_block.append(lines[i])
                i += 1
            rows = parse_markdown_table(table_block)
            if rows:
                normalized = [r + [""] * (max(len(x) for x in rows) - len(r)) for r in rows]
                tbl = Table(normalized, repeatRows=1)
                tbl.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f4f7")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                            ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                            ("LINEABOVE", (0, 0), (-1, 0), 0.8, colors.HexColor("#9aa4b2")),
                            ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.HexColor("#9aa4b2")),
                            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d0d5dd")),
                            ("LEFTPADDING", (0, 0), (-1, -1), 5),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                            ("TOPPADDING", (0, 0), (-1, -1), 4),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ]
                    )
                )
                story.append(tbl)
                story.append(Spacer(1, 6))
            continue

        m_h1 = re.match(r"^#\s+(.*)$", stripped)
        if m_h1:
            story.append(Paragraph(clean_inline(m_h1.group(1)), styles.title))
            i += 1
            continue

        m_h2 = re.match(r"^##\s+(.*)$", stripped)
        if m_h2:
            heading = m_h2.group(1).strip()
            story.append(Paragraph(clean_inline(heading), styles.h2))
            i += 1
            continue

        m_h3 = re.match(r"^###\s+(.*)$", stripped)
        if m_h3:
            story.append(Paragraph(clean_inline(m_h3.group(1).strip()), styles.h3))
            i += 1
            continue

        m_num = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if m_num:
            story.append(Paragraph(clean_inline(f"{m_num.group(1)}. {m_num.group(2)}"), styles.list_item))
            i += 1
            continue

        m_bullet = re.match(r"^-+\s+(.*)$", stripped)
        if m_bullet:
            story.append(Paragraph(clean_inline(f"• {m_bullet.group(1)}"), styles.list_item))
            i += 1
            continue

        # Keep plain body text.
        story.append(Paragraph(clean_inline(stripped), styles.body))
        i += 1

    return story


def draw_footer(canvas, doc):
    if doc.page <= 1:
        return
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#6b7280"))
    canvas.drawRightString(A4[0] - 20 * mm, 12 * mm, f"Page {doc.page}")
    canvas.restoreState()


def generate_pdf(pdf_ready_md_text: str, output_path: Path):
    styles = build_styles()

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title="Color Smile Inventory Management System - User Guide and User Manual",
        author="Color Smile",
    )

    story = markdown_to_story(pdf_ready_md_text, styles)
    doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)


def main():
    source_text = SOURCE_MD.read_text(encoding="utf-8")
    pdf_ready_text = compose_pdf_ready_markdown(source_text)
    PDF_READY_MD.write_text(pdf_ready_text, encoding="utf-8")
    generate_pdf(pdf_ready_text, OUTPUT_PDF)
    print(f"Wrote: {PDF_READY_MD}")
    print(f"Wrote: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()

