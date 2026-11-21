from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).parent
OUT = ROOT / "StudyForge_AI_Project_Synopsis.docx"


def set_cell_shading(cell, fill):
    cell_properties = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    cell_properties.append(shading)


def set_cell_margins(cell, top=90, start=110, bottom=90, end=110):
    cell_properties = cell._tc.get_or_add_tcPr()
    margins = cell_properties.first_child_found_in("w:tcMar")
    if margins is None:
        margins = OxmlElement("w:tcMar")
        cell_properties.append(margins)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        element = margins.find(qn(f"w:{side}"))
        if element is None:
            element = OxmlElement(f"w:{side}")
            margins.append(element)
        element.set(qn("w:w"), str(value))
        element.set(qn("w:type"), "dxa")


def border_cell(cell, color="7F8C8D", size="6"):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right"):
        tag = qn(f"w:{edge}")
        element = borders.find(tag)
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:color"), color)


def add_field(paragraph, field):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = field
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    separate.append(text)
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, end])


def make_architecture(path):
    image = Image.new("RGB", (1800, 940), "white")
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.truetype("C:/Windows/Fonts/timesbd.ttf", 40)
    text_font = ImageFont.truetype("C:/Windows/Fonts/timesbd.ttf", 24)
    draw.text((900, 35), "StudyForge AI: High-Level Architecture", anchor="ma", fill="#1F2937", font=title_font)
    boxes = [
        (70, 400, 360, 580, "Student\nNext.js Web UI", "#DCEBFA"), (540, 400, 900, 580, "FastAPI Backend\nREST APIs", "#D9F2E6"),
        (1040, 200, 1390, 350, "Authentication\n& User Module", "#FFF0C2"), (1040, 400, 1390, 550, "Document, Quiz &\nStudy-plan Service", "#FFF0C2"),
        (1040, 610, 1390, 760, "Grounded AI\nAssistance Service", "#FFF0C2"), (1480, 400, 1750, 580, "PostgreSQL + pgvector\n(SQLAlchemy ORM)", "#E8DDF5"),
    ]
    for left, top, right, bottom, label, color in boxes:
        draw.rounded_rectangle((left, top, right, bottom), radius=22, fill=color, outline="#34495E", width=4)
        draw.multiline_text(((left + right) // 2, (top + bottom) // 2), label, anchor="mm", align="center", spacing=8, fill="#1F2937", font=text_font)
    arrows = [((430, 490), (540, 490)), ((900, 490), (1040, 275)), ((900, 490), (1040, 475)), ((900, 490), (1040, 685)), ((1390, 275), (1480, 490)), ((1390, 475), (1480, 490)), ((1390, 685), (1480, 490))]
    for start, end in arrows:
        draw.line((start, end), fill="#34495E", width=5)
        draw.ellipse((end[0]-10, end[1]-10, end[0]+10, end[1]+10), fill="#34495E")
    image.save(path)


def make_er(path):
    image = Image.new("RGB", (1800, 1060), "white")
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.truetype("C:/Windows/Fonts/timesbd.ttf", 40)
    header_font = ImageFont.truetype("C:/Windows/Fonts/timesbd.ttf", 23)
    body_font = ImageFont.truetype("C:/Windows/Fonts/times.ttf", 20)
    draw.text((900, 30), "Implemented Entity-Relationship Diagram", anchor="ma", fill="#1F2937", font=title_font)
    entities = [
        (90, 470, 500, 750, "USERS", ["PK  id", "email (unique)", "password_hash", "xp, streak", "learning_style, goals"]),
        (700, 470, 1110, 750, "DOCUMENTS", ["PK  id", "FK  user_id", "title, subject", "filename, status", "created_at"]),
        (1310, 470, 1710, 750, "CHUNKS", ["PK  id", "FK  document_id", "page", "content"]),
        (700, 130, 1110, 380, "STUDY_TASKS", ["PK  id", "FK  user_id", "title, due_date", "minutes, completed"]),
    ]
    for left, top, right, bottom, title, attributes in entities:
        draw.rounded_rectangle((left, top, right, bottom), radius=16, fill="#F9FBFD", outline="#1F4E79", width=4)
        draw.rectangle((left, top, right, top + 52), fill="#1F4E79")
        draw.text(((left+right)//2, top+26), title, anchor="mm", fill="white", font=header_font)
        draw.multiline_text((left+25, top+78), "\n".join(attributes), fill="#1F2937", font=body_font, spacing=10)
    for start, end, label in [((500, 610), (700, 610), "1 : M"), ((1110, 610), (1310, 610), "1 : M"), ((300, 470), (800, 380), "1 : M")]:
        draw.line((start, end), fill="#34495E", width=5)
        draw.ellipse((end[0]-10, end[1]-10, end[0]+10, end[1]+10), fill="#34495E")
        draw.text(((start[0]+end[0])//2, (start[1]+end[1])//2-25), label, anchor="mm", fill="#34495E", font=header_font)
    image.save(path)


def create_document():
    arch_image = ROOT / "architecture.png"
    er_image = ROOT / "er_diagram.png"
    make_architecture(arch_image)
    make_er(er_image)

    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.85)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.9)
    section.right_margin = Inches(0.9)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.font.size = Pt(12)
    normal.paragraph_format.line_spacing = 1.35
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for name, size, alignment, bold, italic, before, after in [
        ("Title", 20, WD_ALIGN_PARAGRAPH.CENTER, True, False, 0, 12),
        ("Heading 1", 14, WD_ALIGN_PARAGRAPH.CENTER, True, False, 14, 8),
        ("Heading 2", 12, WD_ALIGN_PARAGRAPH.LEFT, True, False, 10, 4),
        ("Heading 3", 12, WD_ALIGN_PARAGRAPH.LEFT, False, True, 8, 3),
    ]:
        style = styles[name]
        style.font.name = "Times New Roman"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        style.font.size = Pt(size)
        style.font.bold = bold
        style.font.italic = italic
        style.paragraph_format.alignment = alignment
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True
    caption = styles["Caption"]
    caption.font.name = "Times New Roman"
    caption.font.size = Pt(10)
    caption.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def para(text="", style=None, align=None, bold=False, size=None, space_after=None):
        p = doc.add_paragraph(style=style)
        if align is not None:
            p.alignment = align
        run = p.add_run(text)
        run.bold = bold
        if size:
            run.font.size = Pt(size)
        if space_after is not None:
            p.paragraph_format.space_after = Pt(space_after)
        return p

    def heading(text, level=1):
        return doc.add_heading(text, level=level)

    def bullet(text):
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.first_line_indent = Inches(-0.18)
        p.paragraph_format.space_after = Pt(3)
        p.add_run(text)
        return p

    def table(headers, rows, widths=None):
        tbl = doc.add_table(rows=1, cols=len(headers))
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.style = "Table Grid"
        tbl.autofit = False
        for index, value in enumerate(headers):
            cell = tbl.rows[0].cells[index]
            cell.text = value
            set_cell_shading(cell, "1F4E79")
            set_cell_margins(cell)
            border_cell(cell, "1F4E79")
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            for run in cell.paragraphs[0].runs:
                run.font.name = "Times New Roman"; run.font.size = Pt(11); run.font.bold = True; run.font.color.rgb = RGBColor(255,255,255)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            if widths: cell.width = Inches(widths[index])
        for row_values in rows:
            cells = tbl.add_row().cells
            for index, value in enumerate(row_values):
                cell = cells[index]
                cell.text = value
                set_cell_margins(cell)
                border_cell(cell)
                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.space_after = Pt(0)
                    paragraph.paragraph_format.line_spacing = 1.12
                    for run in paragraph.runs:
                        run.font.name = "Times New Roman"; run.font.size = Pt(10.5)
                if widths: cell.width = Inches(widths[index])
        doc.add_paragraph().paragraph_format.space_after = Pt(2)
        return tbl

    # Cover page
    para("PROJECT SYNOPSIS", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=16, space_after=24)
    para("STUDYFORGE AI", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=22, space_after=8)
    para("An Intelligent Study Planning and Learning Support Platform", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=14, space_after=40)
    para("Submitted in partial fulfillment of the requirements for the award of the degree of", align=WD_ALIGN_PARAGRAPH.CENTER, size=12, space_after=8)
    para("Bachelor of Technology", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=15, space_after=28)
    para("Submitted By", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_after=5)
    para("[Student Name]  |  Roll No.: [Roll Number]", align=WD_ALIGN_PARAGRAPH.CENTER, size=12, space_after=28)
    para("Under the Guidance of", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_after=5)
    para("[Faculty Guide Name]", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=12, space_after=3)
    para("[Designation]", align=WD_ALIGN_PARAGRAPH.CENTER, size=12, space_after=44)
    para("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=14, space_after=6)
    para("AGC AMRITSAR", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, size=14, space_after=8)
    para("Academic Session: 2026–27", align=WD_ALIGN_PARAGRAPH.CENTER, size=12)
    doc.add_page_break()

    heading("1. INTRODUCTION")
    heading("1.1 Overview", 2)
    para("StudyForge AI is a full-stack, AI-assisted study workspace that converts uploaded PDF learning material into cited answers, quiz practice, study plans, and visible progress momentum. The system combines a Next.js client application with a FastAPI backend, PostgreSQL-compatible persistence, document extraction, secure authentication, and containerised deployment. It gives students one coherent workspace for their notes, questions, quizzes, flashcards, and planned study tasks.")
    heading("1.2 Background and Motivation", 2)
    para("Students frequently divide their attention between multiple subjects, deadlines, examinations, and learning resources. Generic task applications help record reminders but do not understand academic context, while large online learning platforms often focus on content delivery rather than a student's personal workflow. This project addresses the need for a lightweight, student-centred workspace that brings study planning, progress monitoring, and intelligent guidance together in one interface.")
    para("The motivation for StudyForge AI is to reduce the friction between uploading course notes and beginning an effective, focused study session. By maintaining structured records of documents, page-wise text chunks, quiz performance, tasks, XP, and learning preferences, the platform provides contextual and measurable support while preserving source traceability.")
    heading("1.3 Existing Solutions and Differentiation", 2)
    bullet("Notion and Trello support flexible note-taking and task boards, but they do not provide an academic-domain data model or built-in AI study workflow.")
    bullet("Google Classroom and Moodle distribute course content and assignments, but are mainly institution-led rather than personalised study planners.")
    bullet("General-purpose AI chatbots can answer questions, but often lack source-grounding, PDF citations, quiz-history storage, and structured study-task progress.")
    para("StudyForge AI combines a structured learning database with a modern API-first architecture. Its key distinction is grounded learning support: it extracts uploaded PDFs page by page, retrieves the most relevant chunks, and presents answers with source citations. It also combines this with quiz submission, XP/streak tracking, task completion, and an elegant responsive user interface.")

    heading("2. PROBLEM STATEMENT")
    para("Students need a unified and reliable system to transform scattered PDF notes into useful learning activities, manage subject-wise tasks, monitor progress, and obtain timely, source-grounded answers. Existing tools are often fragmented: one tool stores files, another tracks tasks, and another provides AI answers without evidence. This fragmentation makes it difficult to sustain a consistent study routine, verify answers, or identify unfinished priorities.")
    para("The problem is important because poor planning and lack of visibility into progress can cause missed deadlines, ineffective revision, and unnecessary academic stress. StudyForge AI aims to solve this problem by providing a secure, extensible backend that centralises student information and supports an intelligent learning workflow.")

    heading("3. OBJECTIVES")
    heading("3.1 Primary Objectives", 2)
    bullet("Develop a RESTful backend for StudyForge AI using FastAPI with documented, health-checkable API endpoints.")
    bullet("Implement JWT-based signup/login and protected routes with securely hashed passwords.")
    bullet("Accept PDF uploads, extract page-wise text using PyMuPDF, and store searchable source chunks with document metadata.")
    bullet("Generate grounded answers, quizzes, flashcards, study-plan tasks, and measurable XP/streak progress from a student's learning material.")
    heading("3.2 Secondary Objectives", 2)
    bullet("Deliver a polished, responsive Next.js application for library, workspace, quiz, flashcard, dashboard, and planning workflows.")
    bullet("Support a production LLM provider through an environment-controlled OpenAI-compatible API integration, while retaining a safe deterministic mock-AI mode for demonstrations.")
    bullet("Deploy repeatably with Docker Compose, PostgreSQL, and pgvector; retain a SQLite option for lightweight local development.")

    heading("4. PROPOSED SYSTEM AND METHODOLOGY")
    heading("4.1 Proposed Approach", 2)
    para("The proposed system follows an API-first, layered architecture. A student interacts with a responsive Next.js interface. Requests are sent to the FastAPI application, where route handlers validate input, enforce JWT authentication, and invoke the appropriate business logic. SQLAlchemy acts as the object-relational mapper between Python models and PostgreSQL/SQLite. Docker Compose provisions the database, backend, and frontend as separate services for repeatable execution.")
    para("When a PDF is uploaded, the backend uses PyMuPDF to extract text one page at a time and divides it into manageable chunks. A retrieval routine scores chunks against the user's question and supplies the most relevant text as cited evidence. The current demonstration configuration uses deterministic mock quiz content and extractive cited chat; the service layer is intentionally prepared for a production LLM provider for schema-validated quizzes, flashcards, study plans, and explanations.")
    heading("4.2 Workflow", 2)
    table(["Step", "System Activity", "Outcome"], [
        ("1", "User signs up or logs in through protected client pages.", "JWT-authenticated learner session."),
        ("2", "Student uploads a subject PDF to the personal library.", "Document metadata and page-wise chunks are stored."),
        ("3", "Student asks a question or opens the workspace.", "Relevant chunks are retrieved and cited in the answer."),
        ("4", "Student generates and submits a quiz or reviews flashcards.", "Score, XP, and learning feedback are recorded."),
        ("5", "Student creates and completes study-plan tasks.", "Updated progress, task state, and dashboard metrics."),
        ("6", "Dashboard presents pending work and momentum.", "Clear, personalised next actions for the learner.")
    ], [0.55, 3.75, 2.75])
    heading("4.3 Methodology", 2)
    bullet("Requirement analysis: identify student workflows, data fields, privacy needs, and the minimum viable feature set.")
    bullet("Backend modelling: define SQLAlchemy entities for users, documents, chunks, quiz attempts, and study tasks, with database session management.")
    bullet("API development: implement versioned FastAPI endpoints with Pydantic schemas, dependency injection, JWT security, and automatic OpenAPI documentation.")
    bullet("Grounded intelligence layer: retrieve uploaded source chunks before answering; use an environment-controlled LLM provider only for approved generative workflows.")
    bullet("Testing and deployment: validate APIs using pytest and FastAPI TestClient; package the service with Docker and deploy to a managed cloud environment when ready.")
    para("The methodology is iterative. Each module is first designed, implemented in isolation, tested through its API contract, and then integrated into the common data model. This reduces coupling and keeps the platform maintainable as functionality grows.")

    heading("5. SYSTEM DESIGN")
    heading("5.1 High-Level Architecture", 2)
    doc.add_picture(str(arch_image), width=Inches(6.6))
    para("Figure 1: High-level architecture of StudyForge AI.", style="Caption")
    para("The client layer is implemented as a responsive Next.js web application. FastAPI is the central service layer and exposes REST endpoints. Authentication, document processing, retrieval, quizzes, planning, and progress modules remain logically separated while sharing the same domain model. SQLAlchemy manages persistence to SQLite for local development and PostgreSQL with pgvector in Docker-based deployments.")
    heading("5.2 ER Diagram and Database Schema", 2)
    doc.add_picture(str(er_image), width=Inches(6.6))
    para("Figure 2: Proposed entity-relationship diagram.", style="Caption")
    para("The implemented database includes USERS, DOCUMENTS, CHUNKS, QUIZ_ATTEMPTS, and STUDY_TASKS. The user record stores secure identity and learning-preference information, documents belong to users, and a document contains many page-wise chunks. Quiz attempts store score and total marks, while study tasks store due date, estimated duration, and completion state.")
    table(["Entity", "Key Fields", "Purpose"], [
        ("USERS", "id, email, password_hash, xp, streak, learning_style", "Stores secure learner identity and preferences."),
        ("DOCUMENTS", "id, user_id, title, subject, filename, status", "Stores uploaded PDF metadata."),
        ("CHUNKS", "id, document_id, page, content", "Stores extracted source text for cited retrieval."),
        ("QUIZ_ATTEMPTS", "id, user_id, document_id, score, total", "Stores assessment performance."),
        ("STUDY_TASKS", "id, user_id, title, due_date, minutes, completed", "Represents actionable study work.")
    ], [1.25, 3.0, 2.8])
    heading("5.3 Data Flow Description", 2)
    para("At Level 0, the Student supplies account details, PDF files, questions, quiz responses, and task data to StudyForge AI, and receives cited answers, assessment feedback, plans, and progress metrics. At Level 1, the backend routes account data to Authentication, files to Document Processing, questions to Grounded Retrieval, and learning actions to the Quiz/Planning modules. Each module reads or writes controlled records through the data-access layer. The resulting response is returned to the Next.js client in JSON format.")

    heading("6. TECHNOLOGIES AND LIBRARIES USED")
    para("StudyForge AI is intentionally built with current, industry-relevant technologies. The present codebase already uses the following core stack, while the proposed stack supports future delivery of the full intelligent platform.")
    table(["Technology / Library", "Role in StudyForge AI", "Status"], [
        ("Python 3", "Primary backend programming language; provides readable, maintainable application logic.", "Used"),
        ("FastAPI", "High-performance REST API framework; provides routing, validation integration, automatic Swagger/OpenAPI documentation, and async-ready architecture.", "Used"),
        ("Uvicorn", "ASGI server used to run the FastAPI application during development and deployment.", "Used"),
        ("SQLAlchemy", "ORM for declarative data models, database engine configuration, sessions, and portable queries.", "Used"),
        ("PostgreSQL + pgvector", "Containerised relational database and vector-extension-ready persistence; SQLite remains supported for local development.", "Used"),
        ("Pydantic Settings", "Configuration and API schema support for validated environment-driven application settings.", "Used"),
        ("JWT + python-jose + passlib/bcrypt", "Token-based authentication and secure password hashing for protected account workflows.", "Used"),
        ("PyMuPDF (fitz)", "Page-wise PDF text extraction and chunking of learner-uploaded source material.", "Used"),
        ("OpenAI SDK / compatible LLM API", "Production-ready integration point for generative study plans, quizzes, flashcards, and explanations; mock-AI mode is enabled for safe demos.", "Used / configurable"),
        ("Next.js 15 + React 19", "App Router-based responsive frontend for landing, library, workspace, quiz, flashcards, dashboard, and planning flows.", "Used"),
        ("TypeScript + Tailwind CSS", "Type-safe frontend implementation and responsive dark-first interface styling.", "Used"),
        ("Framer Motion + Lucide React", "User-interface motion and accessible iconography.", "Used"),
        ("Docker Compose", "Runs frontend, FastAPI backend, PostgreSQL, volumes, and service networking reproducibly.", "Used"),
        ("pytest + httpx", "Automated backend/API tests for reliable iterative development.", "Used"),
        ("AWS / GCP / Azure", "Future cloud-hosting options for managed database, object storage, monitoring, and scalable deployment.", "Planned")
    ], [1.45, 4.65, 0.95])
    para("FastAPI and SQLAlchemy separate API concerns from storage concerns, while Next.js provides a modern type-safe client experience. PyMuPDF plus the source-chunk retrieval workflow makes the AI experience evidence-aware rather than purely conversational. PostgreSQL/pgvector and Docker Compose create a cloud-native path for growth, and the modular service layer enables future managed deployment on AWS, GCP, or Azure.")

    heading("7. HARDWARE AND SOFTWARE REQUIREMENTS")
    heading("7.1 Minimum Hardware Requirements", 2)
    bullet("Processor: Intel Core i3 / AMD equivalent or higher.")
    bullet("RAM: 4 GB minimum; 8 GB recommended for development tools and local testing.")
    bullet("Storage: 2 GB free space for source code, virtual environment, database, and development utilities.")
    bullet("Internet: Required for package installation, Git repositories, cloud deployment, and LLM API access.")
    heading("7.2 Software Requirements", 2)
    bullet("Operating System: Windows 10/11, Linux, or macOS.")
    bullet("Python 3.10+ with pip and a virtual environment.")
    bullet("VS Code or PyCharm; Git for source control; Postman/Insomnia for API testing.")
    bullet("FastAPI, Uvicorn, SQLAlchemy, and SQLite; Docker Desktop and a modern browser for optional deployment and frontend work.")

    heading("8. EXPECTED OUTCOME AND DELIVERABLES")
    para("The expected outcome is a functioning backend service for StudyForge AI that can run locally, confirm service health, initialise the database, and manage a secure user model. The completed project will demonstrate a complete learner workflow in which a student creates an account, builds study plans, adds tasks, monitors completion, and receives AI-generated academic support where the integration is enabled.")
    bullet("Next.js frontend and FastAPI backend with documented OpenAPI/Swagger endpoints.")
    bullet("JWT authentication, PostgreSQL/SQLite persistence, and SQLAlchemy models for users, PDFs, chunks, attempts, and tasks.")
    bullet("PDF library, cited workspace chat, quiz generation/submission, flashcards, study-plan tasks, and XP/streak progress modules.")
    bullet("Database schema/ER diagram, API test collection, project report, and demonstration video or live demo.")
    bullet("Optional Docker configuration and cloud deployment guide for reproducible execution.")

    heading("9. WORK PLAN AND TIMELINE")
    table(["Phase", "Weeks", "Activities and Milestone"], [
        ("I. Analysis", "1–2", "Collect requirements, review similar systems, finalise use cases and scope."),
        ("II. Design", "3–4", "Prepare database schema, API contracts, architecture, and wireframes."),
        ("III. Core Backend", "5–7", "Implement FastAPI, SQLAlchemy, JWT authentication, document uploads, and tests."),
        ("IV. Learning Modules", "8–10", "Build PDF chunking, cited retrieval, quizzes, tasks, progress, and dashboard APIs."),
        ("V. AI Integration", "11–12", "Add guarded LLM workflows for generated quizzes, flashcards, planning, and explanations."),
        ("VI. UI and Integration", "13–14", "Build and connect the Next.js client; conduct end-to-end integration testing."),
        ("VII. Deployment & Review", "15–16", "Dockerise, perform final testing, prepare report, synopsis, and demonstration."),
    ], [1.55, 0.75, 4.75])
    para("Key milestones are: approved design by Week 4, operational authenticated document backend by Week 7, complete cited learning workflow by Week 10, AI-assisted prototype by Week 12, and final containerised demonstration by Week 16.")

    heading("10. REFERENCES")
    refs = [
        "FastAPI Documentation. https://fastapi.tiangolo.com/ (accessed July 2026).",
        "SQLAlchemy Documentation. https://docs.sqlalchemy.org/ (accessed July 2026).",
        "SQLite Documentation. https://www.sqlite.org/docs.html (accessed July 2026).",
        "Uvicorn Documentation. https://www.uvicorn.org/ (accessed July 2026).",
        "OpenAI API Documentation. https://platform.openai.com/docs/ (for proposed LLM integration; accessed July 2026).",
        "Sommerville, I. Software Engineering, 10th Edition, Pearson, 2015."
    ]
    for reference in refs:
        p = doc.add_paragraph(style="List Number")
        p.paragraph_format.space_after = Pt(3)
        p.add_run(reference)

    # footer page numbers
    for section in doc.sections:
        footer = section.footer.paragraphs[0]
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer.add_run("StudyForge AI Project Synopsis | Page ")
        add_field(footer, "PAGE")
        for run in footer.runs:
            run.font.name = "Times New Roman"; run.font.size = Pt(10)
    doc.save(OUT)
    return OUT


if __name__ == "__main__":
    print(create_document())
