from pathlib import Path

from docx import Document
from docx.table import Table as DocxTable
from docx.text.paragraph import Paragraph
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph as RLParagraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.platypus.tableofcontents import TableOfContents


ROOT = Path(__file__).parent
SOURCE = ROOT / "StudyForge_AI_Synopsis.docx"
OUTPUT = ROOT / "StudyForge_AI_Synopsis.pdf"
ASSETS = ROOT / "pdf_assets"


def iter_blocks(document):
    for child in document.element.body.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, document)
        elif child.tag.endswith("}tbl"):
            yield DocxTable(child, document)


def contains_page_break(paragraph):
    return "w:type=\"page\"" in paragraph._p.xml


def extract_images():
    return [ROOT / "er_diagram.png", ROOT / "architecture.png"]


def page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Roman", 10)
    canvas.drawCentredString(A4[0] / 2, 0.42 * inch, f"Page {doc.page}")
    canvas.restoreState()


class SynopsisDoc(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, RLParagraph) and flowable.style.name == "H1":
            self.notify("TOCEntry", (0, flowable.getPlainText(), self.page))


def build_pdf():
    document = Document(SOURCE)
    images = extract_images()
    styles = getSampleStyleSheet()
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontName="Times-Roman", fontSize=12, leading=16, alignment=TA_JUSTIFY, spaceAfter=7)
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Times-Bold", fontSize=14, leading=18, alignment=TA_CENTER, spaceBefore=13, spaceAfter=8, keepWithNext=True)
    index_title = ParagraphStyle("IndexTitle", parent=h1)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Times-Bold", fontSize=12, leading=15, alignment=TA_LEFT, spaceBefore=9, spaceAfter=4, keepWithNext=True)
    h3 = ParagraphStyle("H3", parent=styles["Heading3"], fontName="Times-Italic", fontSize=12, leading=15, alignment=TA_LEFT, spaceBefore=8, spaceAfter=3, keepWithNext=True)
    caption = ParagraphStyle("Caption", parent=body, fontName="Times-Roman", fontSize=10, leading=12, alignment=TA_CENTER, spaceAfter=8)
    cover = ParagraphStyle("Cover", parent=body, alignment=TA_CENTER, spaceAfter=8)
    story = []
    cover_mode = True
    image_index = 0
    index_added = False
    cover_logo_added = False

    def paragraph_markup(paragraph):
        parts = []
        for run in paragraph.runs:
            value = run.text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            parts.append(f"<b>{value}</b>" if run.bold else value)
        return "".join(parts)

    def bullet_markup(text):
        value = text[1:].strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        for separator in (": ", " - "):
            if separator in value:
                label, body = value.split(separator, 1)
                return f"&bull; <b>{label}{separator.strip()}</b> {body}"
        return "&bull; " + value

    for block in iter_blocks(document):
        if isinstance(block, Paragraph):
            if contains_page_break(block):
                story.append(PageBreak())
                cover_mode = False
                continue
            text = block.text.strip()
            if not text:
                continue
            safe = paragraph_markup(block)
            style_name = block.style.name
            if cover_mode:
                font_size = 12
                if text == "STUDYFORGE AI": font_size = 22
                elif text == "PROJECT SYNOPSIS": font_size = 16
                elif text in {"DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING", "AGC AMRITSAR"}: font_size = 14
                bold = text in {"PROJECT SYNOPSIS", "STUDYFORGE AI", "Bachelor of Technology", "Submitted By", "Under the Guidance of", "DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING", "AGC AMRITSAR"}
                story.append(RLParagraph(f"<b>{safe}</b>" if bold else safe, ParagraphStyle("CoverLocal", parent=cover, fontSize=font_size, leading=font_size + 5, spaceAfter=13 if font_size >= 14 else 8)))
                if text.startswith("Batch") and not cover_logo_added:
                    story.append(Image(str(ROOT / "reference_media" / "image1.jpeg"), width=0.85 * inch, height=0.85 * inch, hAlign="CENTER"))
                    story.append(Spacer(1, 10))
                    cover_logo_added = True
            elif style_name in {"Heading 1", "Style2"}:
                story.append(RLParagraph(safe, h1))
            elif style_name == "Heading 2":
                story.append(RLParagraph(safe, h2))
                if text == "5.1 High-Level Architecture" and image_index < len(images):
                    story.append(Image(str(images[image_index]), width=6.45 * inch, height=3.37 * inch, kind="proportional"))
                    image_index += 1
            elif style_name == "Heading 3":
                story.append(RLParagraph(safe, h3))
            elif style_name == "Caption":
                story.append(RLParagraph(safe, caption))
                if "Figure 1" in text:
                    pass
                elif "Figure 2" in text and image_index < len(images):
                    # Figure 2 follows the ER heading and is inserted before its caption by the next rule.
                    pass
            else:
                if text.startswith("•") or block.style.name == "List Paragraph":
                    markup = safe if text.startswith("•") else bullet_markup("• " + text)
                    story.append(RLParagraph(markup, ParagraphStyle("Bullet", parent=body, leftIndent=18, firstLineIndent=-10, spaceAfter=3)))
                else:
                    story.append(RLParagraph(safe, body))
                if text == "ER Diagram:" and image_index < len(images):
                    story.append(Image(str(images[image_index]), width=6.45 * inch, height=3.65 * inch, kind="proportional"))
                    image_index += 1
                elif text == "System Architecture Diagram (Conceptual):" and image_index < len(images):
                    story.append(Image(str(images[image_index]), width=6.45 * inch, height=3.4 * inch, kind="proportional"))
                    image_index += 1
            if not cover_mode and text == "5.2 ER Diagram and Database Schema" and image_index < len(images):
                story.append(Image(str(images[image_index]), width=6.45 * inch, height=3.7 * inch, kind="proportional"))
                image_index += 1
        else:
            data = [[RLParagraph(cell.text.replace("&", "&amp;"), ParagraphStyle("Cell", parent=body, fontSize=9.2, leading=11)) for cell in row.cells] for row in block.rows]
            widths = [6.5 * inch / len(data[0])] * len(data[0])
            table = Table(data, colWidths=widths, repeatRows=1, hAlign="CENTER")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"), ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#7F8C8D")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.extend([table, Spacer(1, 7)])
    pdf = SynopsisDoc(str(OUTPUT), pagesize=A4, rightMargin=0.8 * inch, leftMargin=0.8 * inch, topMargin=0.75 * inch, bottomMargin=0.7 * inch)
    pdf.multiBuild(story, onFirstPage=page_number, onLaterPages=page_number)
    return OUTPUT


if __name__ == "__main__":
    print(build_pdf())
