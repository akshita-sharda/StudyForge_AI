from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    Preformatted, KeepTogether
)

OUT = Path('output/pdf/StudyForge_AI_Complete_Explanation.pdf')
OUT.parent.mkdir(parents=True, exist_ok=True)

navy = colors.HexColor('#172554')
blue = colors.HexColor('#2563EB')
light_blue = colors.HexColor('#EFF6FF')
light_gray = colors.HexColor('#F3F4F6')
dark = colors.HexColor('#1F2937')

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='CoverTitle', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=27, leading=33, textColor=navy, alignment=TA_CENTER, spaceAfter=12))
styles.add(ParagraphStyle(name='CoverSub', parent=styles['Normal'], fontSize=13, leading=19, textColor=dark, alignment=TA_CENTER, spaceAfter=12))
styles.add(ParagraphStyle(name='H1x', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=17, leading=21, textColor=navy, spaceBefore=12, spaceAfter=8, keepWithNext=True))
styles.add(ParagraphStyle(name='H2x', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12.5, leading=16, textColor=blue, spaceBefore=9, spaceAfter=5, keepWithNext=True))
styles.add(ParagraphStyle(name='Bodyx', parent=styles['BodyText'], fontSize=9.5, leading=14, textColor=dark, spaceAfter=6))
styles.add(ParagraphStyle(name='Smallx', parent=styles['BodyText'], fontSize=8.2, leading=11, textColor=dark, spaceAfter=4))
styles.add(ParagraphStyle(name='Bulletx', parent=styles['BodyText'], fontSize=9.5, leading=14, leftIndent=13, firstLineIndent=-8, bulletIndent=3, spaceAfter=3, textColor=dark))
styles.add(ParagraphStyle(name='Codex', parent=styles['Code'], fontName='Courier', fontSize=7.5, leading=10, leftIndent=8, rightIndent=8, borderColor=colors.HexColor('#CBD5E1'), borderWidth=0.5, borderPadding=7, backColor=light_gray, spaceBefore=4, spaceAfter=8))
styles.add(ParagraphStyle(name='Footer', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#64748B'), alignment=TA_CENTER))

def P(text, style='Bodyx'):
    return Paragraph(text, styles[style])

def bullets(items):
    return [Paragraph('&bull; ' + x, styles['Bulletx']) for x in items]

def code(text):
    return Preformatted(text.strip('\n'), styles['Codex'])

def table(data, widths=None, header=True):
    converted = []
    for r, row in enumerate(data):
        converted.append([P(str(cell), 'Smallx') for cell in row])
    t = Table(converted, colWidths=widths, repeatRows=1 if header else 0, hAlign='LEFT')
    commands = [
        ('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]
    if header:
        commands += [('BACKGROUND', (0, 0), (-1, 0), navy), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white)]
    for r in range(1 if header else 0, len(data)):
        if r % 2 == 0:
            commands.append(('BACKGROUND', (0, r), (-1, r), light_blue))
    t.setStyle(TableStyle(commands))
    return t

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#E2E8F0'))
    canvas.line(18*mm, 14*mm, 192*mm, 14*mm)
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#64748B'))
    canvas.drawCentredString(105*mm, 8*mm, f'StudyForge AI - Complete Project Explanation   |   Page {doc.page}')
    canvas.restoreState()

story = []
story += [Spacer(1, 35*mm), P('StudyForge AI', 'CoverTitle'), P('Complete Theoretical Explanation', 'CoverSub'), P('Simple-language guide with special focus on the React frontend', 'CoverSub'), Spacer(1, 14*mm)]
story += [table([['Project purpose', 'An AI-powered learning platform for organizing study materials and practicing with summaries, flashcards, quizzes, and progress tracking.'], ['Main parts', 'React frontend + FastAPI backend + SQLite database + Gemini AI'], ['Current frontend status', 'Login and signup interface is implemented; dashboard features are planned next.']], [43*mm, 122*mm], header=False), PageBreak()]

story += [P('1. Project Overview', 'H1x'), P('StudyForge AI is a web application for students. A student creates an account, creates subjects, adds notes or uploads files, and asks Gemini AI to turn the material into useful learning tools. The student can then take quizzes and review progress.', 'Bodyx'), P('The frontend is the visible workspace. The backend is the hidden brain that validates requests, protects data, stores records, talks to Gemini, and calculates results.', 'Bodyx'), code('Student action\n    -> React frontend\n    -> FastAPI API\n    -> Security and validation\n    -> SQLite database or Gemini AI\n    -> JSON response\n    -> React updates the screen'), P('Main user journey', 'H2x')] + bullets(['Create an account and log in.', 'Create a subject such as Python or DBMS.', 'Add written notes or upload a PDF/TXT file.', 'Generate an AI summary, flashcards, or quiz.', 'Submit the quiz and receive a percentage score.', 'View recent attempts and overall progress.'])

story += [P('2. Technologies Used', 'H1x'), table([['Technology', 'Simple meaning', 'Role in the project'], ['Python', 'Programming language', 'Backend code'], ['FastAPI', 'Python web framework', 'Creates API endpoints'], ['Uvicorn', 'Web server', 'Runs FastAPI'], ['SQLite', 'Small local database', 'Stores project data'], ['SQLAlchemy', 'Database helper', 'Maps Python classes to tables'], ['Pydantic', 'Data checker', 'Validates requests and responses'], ['JWT', 'Login token format', 'Protects private routes'], ['Bcrypt', 'Password hashing method', 'Stores passwords safely'], ['Gemini AI', 'AI model', 'Creates learning content'], ['React', 'JavaScript UI library', 'Builds the frontend'], ['CORS', 'Browser permission mechanism', 'Allows frontend-backend communication'], ['pypdf', 'PDF reader', 'Extracts text from PDFs']], [32*mm, 54*mm, 79*mm])]

story += [P('3. Frontend Architecture - Main Focus', 'H1x'), P('The frontend is currently centered in <b>frontend/src/App.jsx</b>. It displays a login/signup card and sends authentication requests to the FastAPI server. A complete version would split this large screen into smaller reusable components.', 'Bodyx'), P('Recommended frontend structure', 'H2x'), code('frontend/\n  src/\n    App.jsx              # Main application and routing decision\n    components/          # Reusable UI pieces\n      Navbar.jsx\n      SubjectCard.jsx\n      MaterialCard.jsx\n      QuizQuestion.jsx\n    pages/               # Full screens\n      Login.jsx\n      Dashboard.jsx\n      Subjects.jsx\n      Materials.jsx\n      Quiz.jsx\n      Progress.jsx\n    services/api.js       # fetch helpers\n    styles/               # CSS files'), P('React component', 'H2x'), P('A component is a reusable part of the screen. The current <b>App</b> function is the main component. Future components could include LoginForm, SubjectCard, QuizQuestion, and ProgressDashboard. Each component should have one clear responsibility.', 'Bodyx'), P('JSX', 'H2x'), P('JSX allows HTML-like markup inside JavaScript. JavaScript expressions are written inside curly brackets, and React event names use camelCase such as <b>onClick</b>, <b>onChange</b>, and <b>onSubmit</b>.', 'Bodyx'), code("return (\n  <main>\n    <h1>StudyForge AI</h1>\n    <p>Learn smarter with AI-powered study tools.</p>\n  </main>\n);"), PageBreak()]

story += [P('4. React State and Events', 'H1x'), P('State is information that can change while the page is open. React redraws the affected interface whenever state changes.', 'Bodyx'), code("const [isSignup, setIsSignup] = useState(false);\nconst [form, setForm] = useState({\n  name: '',\n  email: '',\n  password: '',\n});\nconst [message, setMessage] = useState('');"), table([['State value', 'Purpose'], ['isSignup', 'Chooses login mode or signup mode'], ['form', 'Stores name, email, and password input'], ['message', 'Displays success and error messages']], [40*mm, 125*mm]), P('Controlled inputs', 'H2x'), P('The input value comes from React state. When the user types, <b>onChange</b> calls updateForm and changes that state. This gives React complete control of the form.', 'Bodyx'), code("<input\n  name=\"email\"\n  value={form.email}\n  onChange={updateForm}\n/>"), P('updateForm()', 'H2x'), code("function updateForm(event) {\n  setForm({\n    ...form,\n    [event.target.name]: event.target.value,\n  });\n}"), P('The spread operator copies the old form object. The computed property name updates only the input that changed. This prevents the name, email, and password values from overwriting one another.', 'Bodyx'), P('Conditional rendering', 'H2x'), code("{isSignup && (\n  <input name=\"name\" placeholder=\"Your name\" />\n)}"), P('The name input appears only when signup mode is active. The same idea can later show a dashboard for logged-in users and a login page for logged-out users.', 'Bodyx')]

story += [P('5. Frontend Authentication Flow', 'H1x'), P('The current frontend uses one form for both login and signup. The isSignup state decides which backend endpoint is used.', 'Bodyx'), code("const endpoint = isSignup ? '/auth/signup' : '/auth/login';"), P('handleSubmit()', 'H2x'), code("async function handleSubmit(event) {\n  event.preventDefault();\n\n  const response = await fetch(\n    `http://127.0.0.1:8000${endpoint}`,\n    {\n      method: 'POST',\n      headers: { 'Content-Type': 'application/json' },\n      body: JSON.stringify(form),\n    }\n  );\n\n  const data = await response.json();\n}"), P('Important ideas', 'H2x')] + bullets(['async means the function can wait for a server response.', 'await pauses this function until fetch finishes.', 'fetch sends the HTTP request.', 'JSON.stringify converts the JavaScript object into JSON text.', 'response.json converts the server response back into a JavaScript object.', 'response.ok tells whether the request succeeded.'])

story += [P('Saving the JWT token', 'H2x'), code("if (!isSignup) {\n  localStorage.setItem('token', data.access_token);\n  setMessage('Login successful!');\n}"), P('After login, the backend returns a JWT access token. The frontend stores it in localStorage. Future protected requests send it in the Authorization header:', 'Bodyx'), code("headers: {\n  Authorization: `Bearer ${localStorage.getItem('token')}`,\n}"), PageBreak()]

story += [P('6. Important Frontend Screens', 'H1x'), table([['Screen', 'Main responsibility'], ['Login / Signup', 'Create an account and receive a JWT after login'], ['Dashboard', 'Show welcome message, subject count, recent scores, and summary progress'], ['Subjects', 'Create, list, open, and delete subjects'], ['Materials', 'Write notes, upload files, and view saved material'], ['AI Tools', 'Request summaries, flashcards, and quizzes'], ['Quiz', 'Display questions, record answers, submit responses, show score'], ['Progress', 'Display average score, best score, quiz count, and recent attempts']], [42*mm, 123*mm]), P('Recommended frontend data flow', 'H2x'), code('1. Page loads.\n2. useEffect calls the API.\n3. API returns JSON.\n4. setState stores the result.\n5. React renders cards, lists, or charts.\n6. User performs an action.\n7. Another API request updates the database.\n8. State is refreshed so the screen shows the new data.'), P('Rendering lists with map()', 'H2x'), code("{subjects.map((subject) => (\n  <div key={subject.id}>\n    <h3>{subject.name}</h3>\n  </div>\n))}"), P('map repeats a UI structure for every subject. The key helps React identify each item efficiently.', 'Bodyx'), P('Loading and error states', 'H2x'), code("const [loading, setLoading] = useState(false);\n\nsetLoading(true);\n// call API\nsetLoading(false);"), P('AI requests may take time. A loading message such as "Generating quiz..." gives the user feedback. try/catch should display a friendly error if the server is unavailable.', 'Bodyx')]

story += [P('7. File Upload Frontend Concept', 'H1x'), P('The backend accepts PDF and TXT files. The frontend should use FormData because a file is binary data, not ordinary JSON.', 'Bodyx'), code("const formData = new FormData();\nformData.append('subject_id', subjectId);\nformData.append('title', title);\nformData.append('file', selectedFile);\n\nfetch('http://127.0.0.1:8000/uploads/material', {\n  method: 'POST',\n  headers: {\n    Authorization: `Bearer ${token}`,\n  },\n  body: formData,\n});"), P('When using FormData, do not manually set Content-Type. The browser adds the correct multipart boundary automatically.', 'Bodyx'), P('8. Quiz Frontend Concept', 'H1x'), P('The quiz screen receives questions from the backend and stores the selected answer for each question.', 'Bodyx'), code("const [answers, setAnswers] = useState({});\n\nsetAnswers({\n  ...answers,\n  [question.id]: selectedOption,\n});"), P('At submission, the frontend sends an object such as:', 'Bodyx'), code('{\n  "answers": {\n    "1": "A programming language",\n    "2": "Structured Query Language"\n  }\n}'), P('The backend compares these values with the correct answers and returns the score.', 'Bodyx')]

story += [P('9. Backend Files and Functions', 'H1x'), table([['File', 'Important functions / purpose'], ['main.py', 'Creates FastAPI app, loads environment variables, enables CORS, creates tables, and includes routers'], ['database.py', 'Creates SQLite engine, sessions, Base, and get_db()'], ['models.py', 'Defines User, Subject, StudyMaterial, Quiz, QuizQuestion, and QuizAttempt tables'], ['schemas.py', 'Defines input/output formats and validation rules'], ['Authentication.py', 'signup() hashes passwords; login() verifies passwords and creates token'], ['security.py', 'create_access_token() creates JWT; get_current_user() validates token'], ['subjects.py', 'Creates, lists, and deletes user-owned subjects'], ['materials.py', 'Checks ownership, creates notes, and lists notes'], ['uploads.py', 'Checks file type and size, extracts PDF/TXT text, saves material'], ['ai_service.py', 'Calls Gemini for summaries, flashcards, and quizzes'], ['ai_routes.py', 'Exposes AI endpoints and saves generated quizzes'], ['quizzes.py', 'Returns quizzes and scores submitted answers'], ['progress.py', 'Calculates quiz count, average, best score, and recent attempts']], [39*mm, 126*mm]), P('Models versus schemas', 'H2x'), table([['Models', 'Schemas'], ['Describe database tables', 'Describe API data'], ['Use SQLAlchemy Column objects', 'Use Pydantic fields'], ['Store data permanently', 'Validate data entering or leaving the API'], ['Example: User model', 'Example: UserCreate schema']], [84*mm, 81*mm])]

story += [P('10. Database and Security Theory', 'H1x'), P('The database relationship is:', 'Bodyx'), code('User -> Subject -> StudyMaterial -> Quiz -> QuizQuestion\nUser -> QuizAttempt'), P('Every protected query checks ownership. For example, a subject query filters by both subject ID and current user ID. This prevents Student A from viewing Student B data.', 'Bodyx'), P('Password security', 'H2x'), P('Passwords are never stored as plain text. Bcrypt converts a password into a one-way hash. During login, the entered password is compared with the hash.', 'Bodyx'), P('JWT security', 'H2x'), P('A JWT contains the user identity and an expiry time. The frontend sends it as Bearer authentication. The backend decodes it and finds the matching user.', 'Bodyx'), P('Important deployment note', 'H2x'), P('The default SECRET_KEY in security.py is only suitable for development. A real deployment must use a long private secret from an environment variable.', 'Bodyx')]

story += [P('11. API Endpoints', 'H1x'), table([['Method', 'Endpoint', 'Purpose'], ['GET', '/', 'Welcome message'], ['GET', '/health', 'Server health check'], ['POST', '/auth/signup', 'Create account'], ['POST', '/auth/login', 'Login and receive token'], ['POST', '/subjects/', 'Create subject'], ['GET', '/subjects/', 'List user subjects'], ['DELETE', '/subjects/{id}', 'Delete subject'], ['POST', '/materials/', 'Add notes'], ['GET', '/materials/subject/{id}', 'List notes'], ['POST', '/uploads/material', 'Upload PDF or TXT'], ['POST', '/ai/summary', 'Generate summary'], ['POST', '/ai/flashcards', 'Generate flashcards'], ['POST', '/ai/quiz', 'Generate and save quiz'], ['GET', '/quizzes/{id}', 'View quiz'], ['POST', '/quizzes/{id}/submit', 'Submit quiz'], ['GET', '/progress/overview', 'View progress']], [26*mm, 57*mm, 84*mm]), P('Common HTTP methods', 'H2x')] + bullets(['GET reads information.', 'POST creates or submits information.', 'DELETE removes information.', 'PUT or PATCH updates information.'])

story += [P('12. Complete Request Flow Example', 'H1x'), P('When a student generates a quiz, the complete flow is:', 'Bodyx'), code('1. Student selects a saved note in React.\n2. React sends POST /ai/quiz with the material ID.\n3. FastAPI reads the JWT token.\n4. get_current_user() identifies the student.\n5. get_owned_material() checks ownership.\n6. ai_service.generate_quiz() sends the note to Gemini.\n7. Gemini returns structured questions.\n8. The backend saves Quiz and QuizQuestion records.\n9. FastAPI returns JSON.\n10. React renders the quiz screen.'), P('13. Important JavaScript and Python Concepts', 'H1x'), table([['Concept', 'Meaning'], ['useState', 'Stores changing React data'], ['useEffect', 'Runs side effects such as loading API data'], ['fetch', 'Sends HTTP requests from the browser'], ['async/await', 'Waits for asynchronous work'], ['map()', 'Renders repeated UI elements'], ['event.preventDefault()', 'Stops normal browser form refresh'], ['JSON.stringify()', 'Converts JavaScript object to JSON'], ['Depends()', 'Provides FastAPI dependencies automatically'], ['db.commit()', 'Saves database changes'], ['db.refresh()', 'Refreshes a saved database object'], ['join()', 'Connects related database tables'], ['filter()', 'Selects matching records'], ['try/except', 'Handles errors safely']], [46*mm, 121*mm])]

story += [P('14. Final Presentation Summary', 'H1x'), P('StudyForge AI uses React for the interactive student interface. React state stores form values, login mode, messages, subjects, notes, quiz answers, and loading status. The frontend sends JSON or FormData requests using fetch and saves the JWT token after login.', 'Bodyx'), P('FastAPI receives those requests, validates them with Pydantic, checks the JWT token, verifies data ownership, stores data through SQLAlchemy in SQLite, calls Gemini when AI content is needed, and returns JSON responses. The frontend then updates its state and displays the result.', 'Bodyx'), P('The most important frontend improvement is to expand the current login/signup page into reusable pages and components for the dashboard, subjects, materials, AI tools, quizzes, and progress.', 'Bodyx'), P('One-sentence mental model', 'H2x'), code('React displays the learning interface, fetch connects it to FastAPI, JWT identifies the student, SQLAlchemy stores learning data, and Gemini creates AI study content.'), P('Useful commands', 'H2x'), code('py -3.10 -m pip install -r requirements.txt\npy -3.10 -m uvicorn main:app --reload\n\nAPI documentation:\nhttp://127.0.0.1:8000/docs')]

doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=16*mm, bottomMargin=20*mm, title='StudyForge AI Complete Explanation', author='OpenAI')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT.resolve())
