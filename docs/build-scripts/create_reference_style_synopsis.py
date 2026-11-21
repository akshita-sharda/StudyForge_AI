from copy import deepcopy
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


ROOT = Path(__file__).parent
TEMPLATE = Path(r"C:\Users\akshita sharda\Downloads\arpit synopsis.docx")
OUT = ROOT / "StudyForge_AI_Synopsis.docx"
LOGO = ROOT / "reference_media" / "image1.jpeg"


def retain_template_cover(document):
    introduction = next(paragraph._p for paragraph in document.paragraphs if paragraph.text == "INTRODUCTION")
    body = document._element.body
    remove = False
    for element in list(body):
        if element is introduction:
            remove = True
        if remove and element.tag != qn("w:sectPr"):
            body.remove(element)


def replace_cover_text(paragraph, value):
    paragraph.runs[0].text = value
    for run in paragraph.runs[1:]:
        run.text = ""


def page_break(document):
    document.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def add_text(document, text, *, style="Normal", center=False, bold=False, size=None, after=5):
    paragraph = document.add_paragraph(style=style)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.space_after = Pt(after)
    run = paragraph.add_run(text)
    run.bold = bold
    if size:
        run.font.size = Pt(size)
    return paragraph


def section(document, title):
    page_break(document)
    paragraph = document.add_paragraph(style="Style2")
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run(title).bold = True


def label_paragraph(document, label, body):
    paragraph = document.add_paragraph(style="Normal")
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.space_after = Pt(6)
    paragraph.add_run("• ")
    paragraph.add_run(label).bold = True
    paragraph.add_run(body)


def bullet(document, text):
    paragraph = document.add_paragraph(style="List Paragraph")
    paragraph.paragraph_format.space_after = Pt(3)
    for separator in (": ", " - "):
        if separator in text:
            label, body = text.split(separator, 1)
            paragraph.add_run(label + separator.strip()).bold = True
            paragraph.add_run(" " + body)
            return
    paragraph.add_run(text)


def add_page_field(paragraph):
    run = paragraph.add_run("Page ")
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = "PAGE"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instruction, end])


def create():
    doc = Document(TEMPLATE)
    cover = doc.paragraphs
    replace_cover_text(cover[3], "STUDYFORGE_AI")
    replace_cover_text(cover[7], "COMPUTER ENGINEERING")
    replace_cover_text(cover[8], "Batch (2023 - 2027)")
    replace_cover_text(cover[19], "Akshita (2334136)")
    replace_cover_text(cover[20], "Aasveer Singh (2334128)")
    replace_cover_text(cover[21], "Aryan Rampal (2334150)")
    replace_cover_text(cover[22], "Manik Jasrotia (2334191)")
    retain_template_cover(doc)
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.font.size = Pt(12)
    normal.paragraph_format.line_spacing = 1.35
    doc.styles["Style2"].font.name = "Times New Roman"
    doc.styles["Style2"].font.size = Pt(14)

    page_break(doc)
    index_heading = doc.add_paragraph(style="Style2")
    index_heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    index_heading.add_run("INDEX").bold = True
    index_rows = [
        ("1.", "INTRODUCTION", "3"),
        ("2.", "PROBLEM STATEMENT", "4"),
        ("3.", "OBJECTIVES", "5"),
        ("4.", "PROPOSED SYSTEM / METHODOLOGY", "6"),
        ("5.", "SYSTEM DESIGN", "7"),
        ("6.", "TECHNOLOGIES USED", "8"),
        ("7.", "HARDWARE & SOFTWARE REQUIREMENTS", "9"),
        ("8.", "EXPECTED OUTCOME / DELIVERABLES", "10"),
        ("9.", "WORK PLAN / TIMELINE", "11"),
        ("10.", "REFERENCES", "12"),
    ]
    index_table = doc.add_table(rows=1, cols=3)
    index_table.style = "Table Grid"
    index_table.rows[0].cells[0].text = "S. No."
    index_table.rows[0].cells[1].text = "Contents"
    index_table.rows[0].cells[2].text = "Page No."
    for number, title, page in index_rows:
        cells = index_table.add_row().cells
        cells[0].text, cells[1].text, cells[2].text = number, title, page

    section(doc, "INTRODUCTION")
    label_paragraph(doc, "Overview of the Project: ", "StudyForge AI is a full-stack, AI-assisted study workspace that transforms uploaded PDF learning material into cited answers, quiz practice, flashcards, study plans, and visible learning momentum. It combines a Next.js web application with a FastAPI backend, secure authentication, relational persistence, PDF extraction, and Docker-based deployment.")
    label_paragraph(doc, "Brief Context and Background: ", "Students often store notes, search for explanations, practise questions, and manage deadlines using separate tools. This breaks the learning workflow and makes it difficult to connect the original study material with the final answer or assessment. StudyForge AI unifies these activities in one personal workspace.")
    label_paragraph(doc, "Motivation for Choosing the Project: ", "The project is motivated by the need for trustworthy and organised AI support for students. Rather than providing unsupported generic responses, the platform extracts page-wise content from uploaded PDFs and retrieves relevant source chunks for a cited learning experience.")
    label_paragraph(doc, "Existing Solutions & Project Differentiation: ", "ChatPDF and PDF.ai allow document chat but generally do not provide a combined study-plan and progress workflow. Notion and Trello manage tasks but do not understand learning material. General AI chatbots may answer doubts but lack persistent document citations. StudyForge AI differentiates itself by combining PDF-grounded answers, quizzes, flashcards, task management, XP/streak tracking, and a responsive academic interface.")

    section(doc, "PROBLEM STATEMENT")
    label_paragraph(doc, "Problem Definition: ", "To design and develop a secure AI-assisted study platform that converts student-uploaded PDF notes into traceable answers, self-assessment material, and personalised study tasks while maintaining a persistent record of learning progress.")
    label_paragraph(doc, "Importance: ", "Students need more than file storage or a generic chatbot: they need to know what to study, practise against their own material, verify the source of answers, and track unfinished work. Solving this problem improves focus, reduces time spent searching through notes, and makes revision more structured.")

    section(doc, "OBJECTIVES")
    label_paragraph(doc, "Primary Objectives:", "")
    for value in ["Build secure JWT-based registration, login, and protected learning workflows.", "Enable PDF upload and extract page-wise text using PyMuPDF.", "Provide cited, retrieval-based answers using the most relevant extracted source chunks.", "Generate and submit quizzes, record scores, and maintain XP/streak progress.", "Create, update, and complete study-plan tasks from one dashboard."]:
        bullet(doc, value)
    label_paragraph(doc, "Secondary Objectives:", "")
    for value in ["Deliver a responsive modern interface using Next.js 15, React 19, TypeScript, and Tailwind CSS.", "Support a configurable OpenAI-compatible LLM integration while retaining deterministic mock-AI mode for safe demonstrations.", "Package the system with Docker Compose and PostgreSQL/pgvector for scalable deployment."]:
        bullet(doc, value)

    section(doc, "PROPOSED SYSTEM / METHODOLOGY")
    label_paragraph(doc, "Proposed Approach: ", "StudyForge AI uses a modular API-first architecture. The Next.js frontend handles student interaction, while FastAPI provides secure REST APIs for authentication, PDF library management, chat, quiz generation, progress, and study plans. SQLAlchemy maps Python models to SQLite during local development and PostgreSQL with pgvector in Docker deployment.")
    label_paragraph(doc, "Detailed Workflow:", "")
    for value in ["Authentication: A student signs up or logs in; JWT tokens protect account-specific pages and APIs.", "PDF Ingestion: The student uploads a subject PDF. PyMuPDF extracts the text page by page, and the backend stores document metadata and source chunks.", "Grounded Retrieval: For a question, the service compares query terms with stored chunks and selects the most relevant evidence.", "Learning Activities: The workspace returns cited answers; quiz and flashcard features help students practise from the same material.", "Progress Tracking: Quiz submissions update score data, XP and streaks; study-plan tasks store due dates, estimated minutes, and completion state.", "Deployment: Docker Compose runs PostgreSQL/pgvector, FastAPI, and Next.js as isolated services."]:
        bullet(doc, value)

    section(doc, "SYSTEM DESIGN")
    label_paragraph(doc, "Database Schema (PostgreSQL / SQLite): ", "The implemented data model contains USERS, DOCUMENTS, CHUNKS, QUIZ_ATTEMPTS, and STUDY_TASKS. A user owns documents and tasks. Each document contains multiple page-wise chunks that are used for cited retrieval. Quiz attempts record student performance against a document.")
    add_text(doc, "ER Diagram:", bold=True, after=3)
    doc.add_picture(str(ROOT / "er_diagram.png"), width=Inches(6.25))
    add_text(doc, "Figure 1: Entity-Relationship Diagram for StudyForge AI", center=True, size=10, after=10)
    add_text(doc, "System Architecture Diagram (Conceptual):", bold=True, after=3)
    doc.add_picture(str(ROOT / "architecture.png"), width=Inches(6.25))
    add_text(doc, "Figure 2: High-level architecture of StudyForge AI", center=True, size=10, after=4)

    section(doc, "TECHNOLOGIES USED")
    label_paragraph(doc, "The project is built on a modern full-stack, cloud-ready technology stack:", "")
    for value in ["Frontend - Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, Framer Motion and Lucide React for a responsive, dark-first study interface.", "Backend - Python 3, FastAPI, Uvicorn, SQLAlchemy, Pydantic Settings, python-jose and passlib/bcrypt for high-performance APIs and secure authentication.", "PDF and AI Layer - PyMuPDF for page-wise extraction; an OpenAI-compatible SDK interface for production LLM workflows; safe deterministic mock-AI mode for the demonstration.", "Database - PostgreSQL with pgvector for containerised deployment and vector-search readiness; SQLite for lightweight local development.", "DevOps - Docker and Docker Compose for reproducible multi-service deployment; pytest and httpx for automated backend/API testing.", "Cloud-Native Direction - AWS, GCP, or Azure can host the API, database, object storage, monitoring, and future scalable services."]:
        bullet(doc, value)

    section(doc, "HARDWARE & SOFTWARE REQUIREMENTS")
    label_paragraph(doc, "Minimum Hardware Requirements:", "")
    for value in ["Processor: Intel Core i3 / AMD equivalent or higher.", "RAM: 4 GB minimum; 8 GB recommended for Docker, browser, and development tools.", "Storage: 2 GB free space for code, database, packages, and uploads.", "Internet: Required for dependencies, optional LLM API access, and cloud deployment."]:
        bullet(doc, value)
    label_paragraph(doc, "Software Requirements:", "")
    for value in ["OS: Windows 10/11, Linux, or macOS.", "Python 3.10+ with pip and virtual environment; Node.js 20+ with npm.", "VS Code, Git, Docker Desktop, Postman/Insomnia, and a modern browser.", "FastAPI, Uvicorn, SQLAlchemy, PostgreSQL/SQLite, Next.js, and Docker Compose."]:
        bullet(doc, value)

    section(doc, "EXPECTED OUTCOME / DELIVERABLES")
    label_paragraph(doc, "Expected Outcome: ", "A fully functional AI-assisted study workspace that students can access through a responsive web interface. Users can securely create an account, upload PDF notes, ask cited questions, practise with quizzes and flashcards, plan study tasks, and observe learning momentum through XP, streaks, and progress data.")
    label_paragraph(doc, "Key Deliverables:", "")
    for value in ["Complete Next.js frontend and FastAPI backend source code.", "JWT authentication, document library, PDF chunking, cited chat, quizzes, flashcards, study plans, and progress features.", "PostgreSQL/SQLite database schema with SQLAlchemy models.", "Docker Compose configuration for one-command local deployment.", "ER diagram, architecture diagram, test suite, project report, and live demonstration."]:
        bullet(doc, value)

    section(doc, "WORK PLAN / TIMELINE")
    table = doc.add_table(rows=1, cols=3)
    table.style = "Table Grid"
    table.rows[0].cells[0].text, table.rows[0].cells[1].text, table.rows[0].cells[2].text = "Phase", "Weeks", "Milestone"
    rows = [("Requirement Analysis", "1-2", "Study workflow, use cases, scope and feasibility"), ("Design", "3-4", "Architecture, ER diagram, API contracts and UI design"), ("Core Development", "5-7", "Authentication, database, upload and PDF extraction"), ("Learning Modules", "8-10", "Cited chat, quizzes, flashcards, tasks and progress"), ("AI and Integration", "11-12", "LLM service integration and protected client workflows"), ("Testing and Deployment", "13-16", "API testing, Docker deployment, report and final demo")]
    for phase, weeks, milestone in rows:
        cells = table.add_row().cells
        cells[0].text, cells[1].text, cells[2].text = phase, weeks, milestone

    section(doc, "REFERENCES")
    for reference in ["FastAPI Documentation. https://fastapi.tiangolo.com/", "Next.js Documentation. https://nextjs.org/docs", "SQLAlchemy Documentation. https://docs.sqlalchemy.org/", "PyMuPDF Documentation. https://pymupdf.readthedocs.io/", "PostgreSQL Documentation. https://www.postgresql.org/docs/", "OpenAI API Documentation. https://platform.openai.com/docs/", "Docker Documentation. https://docs.docker.com/"]:
        bullet(doc, reference)

    for section_item in doc.sections:
        footer = section_item.footer.paragraphs[0]
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer.runs.clear()
        add_page_field(footer)
        for run in footer.runs:
            run.font.name = "Times New Roman"
            run.font.size = Pt(10)

    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    create()
