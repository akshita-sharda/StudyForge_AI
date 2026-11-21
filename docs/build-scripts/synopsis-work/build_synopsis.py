from pathlib import Path
from shutil import copy2

from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"C:\Users\akshita sharda\OneDrive\Documents\studyforgeAI")
TEMPLATE = Path(r"C:\Users\akshita sharda\Downloads\arpit synopsis.docx")
OUTPUT = ROOT / "StudyForge_AI_Project_Synopsis_Draft.docx"
ASSETS = ROOT / "synopsis-work" / "assets"
ARCHITECTURE = ASSETS / "studyforge-architecture.png"
ER_DIAGRAM = ASSETS / "studyforge-er-diagram.png"


def font(size, bold=False):
    for candidate in ("arialbd.ttf" if bold else "arial.ttf", "calibrib.ttf" if bold else "calibri.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def center_text(draw, box, text, text_font, fill="#172554"):
    left, top, right, bottom = box
    bounds = draw.multiline_textbbox((0, 0), text, font=text_font, align="center", spacing=7)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    draw.multiline_text(
        ((left + right - width) / 2, (top + bottom - height) / 2),
        text,
        font=text_font,
        fill=fill,
        align="center",
        spacing=7,
    )


def rounded_box(draw, box, text, color, text_font, radius=22):
    draw.rounded_rectangle(box, radius=radius, fill=color, outline="#334155", width=4)
    center_text(draw, box, text, text_font)


def arrow(draw, start, end):
    draw.line([start, end], fill="#475569", width=5)
    x1, y1 = start
    x2, y2 = end
    if x2 >= x1:
        triangle = [(x2, y2), (x2 - 18, y2 - 10), (x2 - 18, y2 + 10)]
    else:
        triangle = [(x2, y2), (x2 + 18, y2 - 10), (x2 + 18, y2 + 10)]
    draw.polygon(triangle, fill="#475569")


def build_architecture():
    image = Image.new("RGB", (1800, 1000), "white")
    draw = ImageDraw.Draw(image)
    title_font = font(46, True)
    box_font = font(30, True)
    small_font = font(25, False)
    center_text(draw, (0, 35, 1800, 115), "StudyForge AI: Implemented System Architecture", title_font)
    client = (80, 360, 385, 575)
    api = (560, 340, 945, 600)
    auth = (1165, 180, 1615, 330)
    subjects = (1165, 405, 1615, 555)
    materials = (1165, 630, 1615, 780)
    database = (600, 760, 925, 920)
    rounded_box(draw, client, "API Client\nWeb / Mobile\nor Postman", "#dbeafe", box_font)
    rounded_box(draw, api, "FastAPI Application\nREST API + Validation", "#dcfce7", box_font)
    rounded_box(draw, auth, "Authentication Module\nSignup, Login, JWT", "#fef3c7", box_font)
    rounded_box(draw, subjects, "Subjects Module\nCreate, List, Delete", "#fef3c7", box_font)
    rounded_box(draw, materials, "Study Materials Module\nCreate and Retrieve", "#fef3c7", box_font)
    rounded_box(draw, database, "SQLAlchemy ORM\nSQLite Database", "#ede9fe", box_font)
    arrow(draw, (385, 468), (560, 468))
    arrow(draw, (945, 410), (1165, 255))
    arrow(draw, (945, 470), (1165, 480))
    arrow(draw, (945, 530), (1165, 705))
    arrow(draw, (752, 600), (752, 760))
    draw.multiline_text((610, 680), "Ownership checks protect\nsubjects and materials.", font=small_font, fill="#334155", align="center")
    image.save(ARCHITECTURE)


def entity(draw, box, heading, fields):
    left, top, right, bottom = box
    draw.rounded_rectangle(box, radius=15, fill="#f8fafc", outline="#1d4ed8", width=4)
    draw.rounded_rectangle((left, top, right, top + 55), radius=15, fill="#1e3a8a", outline="#1e3a8a")
    draw.rectangle((left, top + 32, right, top + 55), fill="#1e3a8a")
    center_text(draw, (left, top, right, top + 55), heading, font(25, True), "white")
    draw.multiline_text((left + 22, top + 78), fields, font=font(21), fill="#1f2937", spacing=8)


def build_er_diagram():
    image = Image.new("RGB", (1800, 940), "white")
    draw = ImageDraw.Draw(image)
    center_text(draw, (0, 25, 1800, 105), "StudyForge AI: Implemented Entity-Relationship Diagram", font(43, True))
    users = (80, 320, 545, 660)
    subjects = (690, 220, 1155, 620)
    materials = (1300, 320, 1765, 660)
    entity(draw, users, "USERS", "PK  id\nname\nemail (unique)\npassword_hash\ncreated_at")
    entity(draw, subjects, "SUBJECTS", "PK  id\nFK  owner_id -> users.id\nname\ncolor\ncreated_at")
    entity(draw, materials, "STUDY_MATERIALS", "PK  id\nFK  subject_id -> subjects.id\ntitle\ncontent\ncreated_at")
    arrow(draw, (545, 490), (690, 420))
    arrow(draw, (1155, 420), (1300, 490))
    center_text(draw, (530, 380, 680, 425), "1 : M", font(25, True), "#334155")
    center_text(draw, (1165, 380, 1290, 425), "1 : M", font(25, True), "#334155")
    draw.multiline_text((470, 760), "A user owns many subjects; each subject contains many study materials.\nAll subject and material endpoints verify ownership through the authenticated user.", font=font(27), fill="#334155", align="center", spacing=10)
    image.save(ER_DIAGRAM)


def set_text(paragraph, text, bold=None, size=None, alignment=None):
    paragraph.clear()
    run = paragraph.add_run(text)
    if bold is not None:
        run.bold = bold
    if size is not None:
        run.font.size = Pt(size)
    if alignment is not None:
        paragraph.alignment = alignment
    return paragraph


def delete_element(element):
    parent = element.getparent()
    parent.remove(element)


def set_cell_text(cell, text, header=False):
    paragraph = cell.paragraphs[0]
    set_text(paragraph, text, bold=header, size=9)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER if header else WD_ALIGN_PARAGRAPH.LEFT
    cell.vertical_alignment = 1


def set_table_widths(table, widths):
    grid = table._tbl.tblGrid.gridCol_lst
    for grid_col, width in zip(grid, widths):
        grid_col.set(qn("w:w"), str(width))
    for row in table.rows:
        for cell, width in zip(row.cells, widths):
            cell.width = width
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(width))
            tc_w.set(qn("w:type"), "dxa")


def add_table(document, headers, rows, widths):
    table = document.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.autofit = False
    set_table_widths(table, widths)
    for cell, text in zip(table.rows[0].cells, headers):
        set_cell_text(cell, text, header=True)
        shading = OxmlElement("w:shd")
        shading.set(qn("w:fill"), "D9EAF7")
        cell._tc.get_or_add_tcPr().append(shading)
    for row in rows:
        cells = table.add_row().cells
        for cell, text in zip(cells, row):
            set_cell_text(cell, text)
    document.add_paragraph()


def add_heading(document, text):
    paragraph = document.add_paragraph(style="Style2")
    set_text(paragraph, text, bold=True, size=13)
    return paragraph


def add_labelled_paragraph(document, label, text):
    paragraph = document.add_paragraph(style="Normal")
    first = paragraph.add_run(label)
    first.bold = True
    paragraph.add_run(text)
    paragraph.paragraph_format.space_after = Pt(6)
    return paragraph


def add_bullet(document, text):
    paragraph = document.add_paragraph(style="List Paragraph")
    paragraph.style = "List Paragraph"
    paragraph.add_run(text)
    return paragraph


def add_figure(document, image_path, caption):
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run().add_picture(str(image_path), width=Inches(6.1))
    caption_p = document.add_paragraph()
    set_text(caption_p, caption, size=10, alignment=WD_ALIGN_PARAGRAPH.CENTER)
    caption_p.runs[0].italic = True


def build_document():
    build_architecture()
    build_er_diagram()
    copy2(TEMPLATE, OUTPUT)
    document = Document(OUTPUT)

    cover_replacements = {
        1: "Synopsis",
        2: "On",
        3: "STUDYFORGE AI",
        4: "Subject Name: Major Project Lab (AGCS-21704)",
        5: "Bachelor Of Technology",
        6: "In",
        7: "COMPUTER ENGINEERING",
        8: "Academic Session (2026 - 2027)",
        18: "Submitted By",
        19: "[Student Name (Roll Number)]",
        20: "",
        21: "",
        22: "",
    }
    for index, text in cover_replacements.items():
        set_text(document.paragraphs[index], text, bold=index in {1, 2, 3, 5, 6, 7, 18})

    for paragraph in list(document.paragraphs[25:]):
        delete_element(paragraph._element)
    for table in list(document.tables):
        delete_element(table._element)

    page_break = document.add_paragraph()
    page_break.add_run().add_break()

    add_heading(document, "INTRODUCTION")
    add_labelled_paragraph(document, "Overview of the Project: ", "StudyForge AI is a learning-organisation backend that lets authenticated students create personal subjects and store study materials within them. The application exposes REST APIs through FastAPI and persists data through SQLAlchemy and SQLite.")
    add_labelled_paragraph(document, "Brief Context and Background: ", "Students often keep notes, subject information and revision material in disconnected places. A lightweight, secure application layer is useful for collecting these resources under a single subject-based structure that can later support richer academic workflows.")
    add_labelled_paragraph(document, "Motivation for Choosing the Project: ", "The project focuses on building a clean, maintainable foundation for a student study platform. It combines user security, ownership-aware data access and modular API design so that learning features can be extended safely.")
    add_labelled_paragraph(document, "Existing Solutions and Project Differentiation: ", "Generic note and task tools may not enforce subject-level ownership or provide a reusable backend domain model. StudyForge AI provides a focused API with JWT-authenticated access, password hashing, subject separation and material retrieval scoped to the signed-in student.")

    add_heading(document, "PROBLEM STATEMENT")
    add_labelled_paragraph(document, "Problem Definition: ", "To design and develop a secure, modular backend for a study-management platform in which each student can register, authenticate, organise subjects and store study materials while ensuring that records remain accessible only to their owner.")
    add_labelled_paragraph(document, "Importance: ", "A reliable study platform begins with trustworthy identity, data separation and persistent storage. Solving these concerns early makes later additions such as planning, analytics and AI-assisted learning easier to build without compromising privacy or maintainability.")

    add_heading(document, "OBJECTIVES")
    add_labelled_paragraph(document, "Primary Objectives:", "")
    for bullet in [
        "Develop a FastAPI-based REST API with health-check endpoints and automatic OpenAPI documentation.",
        "Implement signup and login using bcrypt password hashing and JWT bearer tokens.",
        "Allow authenticated users to create, list and delete their own subjects.",
        "Allow authenticated users to create and retrieve study materials within subjects they own.",
        "Use SQLAlchemy models and SQLite persistence for a lightweight local deployment.",
    ]:
        add_bullet(document, bullet)
    add_labelled_paragraph(document, "Planned Extension Objectives:", "The modular backend can later be extended with PDF processing, quizzes, personalised study plans, progress tracking and AI-assisted academic guidance.")

    add_heading(document, "PROPOSED SYSTEM / METHODOLOGY")
    add_labelled_paragraph(document, "Proposed Approach: ", "The current system follows an API-first layered approach. A client sends requests to the FastAPI application. Route handlers validate request bodies with Pydantic schemas, authenticate protected actions through JWTs, apply ownership checks, and store or retrieve records through SQLAlchemy.")
    add_labelled_paragraph(document, "Detailed Workflow:", "")
    for bullet in [
        "Account creation: A student submits name, email and password. The password is hashed with bcrypt before the user record is saved.",
        "Login: The API verifies the stored hash and returns a time-limited JWT bearer token.",
        "Subject management: The authenticated user creates, lists or deletes subjects. Queries are filtered by the authenticated user's ID.",
        "Material management: A material is created only after the system verifies that the requested subject belongs to the current user.",
        "Persistence: Users, subjects and study materials are stored in a SQLite database through SQLAlchemy models.",
    ]:
        add_bullet(document, bullet)
    add_labelled_paragraph(document, "Development Method: ", "The implementation is modular: authentication, subject management, material management, schemas, models and database configuration are kept in separate files. This separation supports independent testing and future feature growth.")

    add_heading(document, "SYSTEM DESIGN")
    add_labelled_paragraph(document, "System Architecture: ", "The implemented architecture is centred on a FastAPI service. Authentication, subjects and study materials are separate routers, while SQLAlchemy provides the persistence layer and SQLite stores the application data.")
    add_figure(document, ARCHITECTURE, "Figure 1: Implemented high-level architecture of StudyForge AI.")
    add_labelled_paragraph(document, "Database Schema: ", "The implemented database has three core entities. A user owns one or more subjects, and each subject contains one or more study-material records. Foreign-key fields represent these relationships.")
    add_figure(document, ER_DIAGRAM, "Figure 2: Implemented entity-relationship diagram.")

    add_heading(document, "TECHNOLOGIES USED")
    add_labelled_paragraph(document, "The current implementation uses the following technologies and libraries:", "")
    add_table(document, ["Technology / Library", "Role in StudyForge AI"], [
        ["Python 3", "Primary programming language for backend application logic."],
        ["FastAPI", "REST API routing, dependency injection, validation integration and OpenAPI documentation."],
        ["Uvicorn", "ASGI server for running the FastAPI application."],
        ["SQLAlchemy", "ORM, declarative models, sessions and database queries."],
        ["SQLite", "Lightweight relational database for local data persistence."],
        ["Pydantic + email-validator", "Validation for request and response schemas, including email addresses."],
        ["passlib with bcrypt", "Secure password hashing and verification."],
        ["python-jose", "Creation and validation of JWT bearer tokens."],
    ], [3000, 6360])

    add_heading(document, "HARDWARE & SOFTWARE REQUIREMENTS")
    add_labelled_paragraph(document, "Minimum Hardware Requirements: ", "Processor: Intel Core i3 / AMD equivalent or higher; RAM: 4 GB minimum; Storage: approximately 500 MB for source code, virtual environment and SQLite database.")
    add_labelled_paragraph(document, "Software Requirements: ", "Windows 10/11, Linux or macOS; Python 3.10+; pip and a virtual environment; VS Code or PyCharm; and a REST API client such as Postman or the FastAPI Swagger UI. Internet access is required only for initial package installation.")

    add_heading(document, "EXPECTED OUTCOME / DELIVERABLES")
    add_labelled_paragraph(document, "Expected Outcome: ", "A functioning StudyForge AI backend that starts locally, responds to health checks, creates the required database tables, allows secure signup/login and supports owner-protected subject and study-material workflows.")
    add_labelled_paragraph(document, "Key Deliverables:", "")
    for bullet in [
        "FastAPI backend source code organised into authentication, subjects, materials, schemas, models, database and security modules.",
        "SQLite database schema for users, subjects and study materials.",
        "JWT-based authentication and bcrypt password hashing.",
        "Documented REST endpoints available through Swagger/OpenAPI.",
        "Project synopsis, technical documentation and demonstration of core API workflows.",
    ]:
        add_bullet(document, bullet)

    add_heading(document, "WORK PLAN / TIMELINE")
    add_table(document, ["Phase", "Timeline", "Key Milestones"], [
        ["Phase 1: Analysis", "Weeks 1-2", "Gather requirements and define student, subject and material workflows."],
        ["Phase 2: System Design", "Weeks 3-4", "Prepare API contracts, database entities and ownership rules."],
        ["Phase 3: Authentication", "Weeks 5-6", "Implement signup, login, password hashing and JWT security."],
        ["Phase 4: Study Modules", "Weeks 7-9", "Implement subject and study-material endpoints with ownership checks."],
        ["Phase 5: Persistence & Testing", "Weeks 10-11", "Configure SQLite/SQLAlchemy and validate API flows."],
        ["Phase 6: Future Extension", "Weeks 12-14", "Plan optional AI, quiz, study-plan and progress-tracking modules."],
        ["Phase 7: Final Delivery", "Weeks 15-16", "Prepare synopsis, demonstration and final project documentation."],
    ], [2100, 1600, 5660])

    add_heading(document, "REFERENCES")
    for reference in [
        "FastAPI Documentation. https://fastapi.tiangolo.com/",
        "SQLAlchemy Documentation. https://docs.sqlalchemy.org/",
        "SQLite Documentation. https://www.sqlite.org/docs.html",
        "Pydantic Documentation. https://docs.pydantic.dev/",
        "python-jose Documentation. https://python-jose.readthedocs.io/",
        "Sommerville, I. Software Engineering, 10th Edition, Pearson, 2015.",
    ]:
        document.add_paragraph(reference, style="Normal")

    document.save(OUTPUT)


if __name__ == "__main__":
    build_document()
