import { useEffect, useState } from "react";

const API = "http://127.0.0.1:8000";
const token = () => localStorage.getItem("token");
const quotes = [
  "Small steps become big victories.",
  "You do not need to know everything. You only need to begin.",
  "Every question you answer makes your future self stronger.",
  "Progress is a power-up. Keep going.",
];

function App() {
  const [screen, setScreen] = useState(localStorage.getItem("token") ? "dashboard" : "login");
  const [signup, setSignup] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [subjects, setSubjects] = useState([]);
  const [newSubject, setNewSubject] = useState("");
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [materials, setMaterials] = useState([]);
  const [materialTitle, setMaterialTitle] = useState("");
  const [materialContent, setMaterialContent] = useState("");
  const [summary, setSummary] = useState("");
  const [quote] = useState(() => quotes[Math.floor(Math.random() * quotes.length)]);
  const [quiz, setQuiz] = useState(null);
  const [quizAnswers, setQuizAnswers] = useState({});
  const [quizResult, setQuizResult] = useState(null);
  const [flashcards, setFlashcards] = useState([]);
  const [flashcardIndex, setFlashcardIndex] = useState(0);
  const [flashcardRevealed, setFlashcardRevealed] = useState(false);
  const [questMessage, setQuestMessage] = useState("");
  const [progress, setProgress] = useState({
    quizzes_taken: 0,
    average_score: 0,
    best_score: 0,
    total_correct_answers: 0,
    total_questions: 0,
    recent_attempts: [],
  });

  useEffect(() => {
    if (screen === "dashboard") {
      loadSubjects();
      loadProgress();
    }
  }, [screen]);

  async function submitAuth(event) {
    event.preventDefault();
    const endpoint = signup ? "/auth/signup" : "/auth/login";
    const body = signup ? { name, email, password } : { email, password };
    try {
      const response = await fetch(API + endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await response.json();
      if (!response.ok) {
        setMessage(data.detail || "Something went wrong.");
        return;
      }
      if (signup) {
        setMessage("Player created! Now log in.");
        setSignup(false);
      } else {
        localStorage.setItem("token", data.access_token);
        setScreen("dashboard");
      }
    } catch {
      setMessage("Backend offline. Start FastAPI first.");
    }
  }

  async function loadSubjects() {
    const response = await fetch(API + "/subjects/", { headers: { Authorization: "Bearer " + token() } });
    if (response.ok) setSubjects(await response.json());
  }

  async function loadProgress() {
    const response = await fetch(API + "/progress/overview", {
      headers: { Authorization: "Bearer " + token() },
    });
    if (response.ok) setProgress(await response.json());
  }

  async function createSubject(event) {
    event.preventDefault();
    if (!newSubject.trim()) return;
    const response = await fetch(API + "/subjects/", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: "Bearer " + token() },
      body: JSON.stringify({ name: newSubject, color: "#786bc9" }),
    });
    if (response.ok) {
      setNewSubject("");
      loadSubjects();
    }
  }

  async function openSubject(subject) {
    setSelectedSubject(subject);
    setSummary("");
    setScreen("subject");
    const response = await fetch(API + "/materials/subject/" + subject.id, {
      headers: { Authorization: "Bearer " + token() },
    });
    if (response.ok) setMaterials(await response.json());
  }

  async function addMaterial(event) {
    event.preventDefault();
    if (!materialTitle.trim() || !materialContent.trim()) return;
    const response = await fetch(API + "/materials/", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: "Bearer " + token() },
      body: JSON.stringify({ title: materialTitle, content: materialContent, subject_id: selectedSubject.id }),
    });
    if (response.ok) {
      setMaterialTitle("");
      setMaterialContent("");
      openSubject(selectedSubject);
    }
  }

  async function generateSummary(materialId) {
    setSummary("AI is studying this material...");
    const response = await fetch(API + "/ai/summary", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: "Bearer " + token() },
      body: JSON.stringify({ material_id: materialId }),
    });
    const data = await response.json();
    setSummary(response.ok ? data.summary : data.detail || "Could not generate summary.");
  }

  async function generateQuiz(materialId) {
    setQuizResult(null);
    setQuizAnswers({});
    setMessage("Generating your Boss Quiz...");
    const response = await fetch(API + "/ai/quiz", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: "Bearer " + token() },
      body: JSON.stringify({ material_id: materialId, count: 5 }),
    });
    const data = await response.json();
    if (!response.ok) {
      setMessage(data.detail || "Could not generate quiz.");
      return;
    }
    const quizResponse = await fetch(API + "/quizzes/" + data.quiz_id, {
      headers: { Authorization: "Bearer " + token() },
    });
    const quizDetails = await quizResponse.json();
    setQuiz({ quiz_id: data.quiz_id, questions: quizDetails.questions });
    setScreen("quiz");
    setMessage("");
  }

  async function getFirstMaterial() {
    if (!subjects.length) {
      setQuestMessage("Create a study world first to unlock quests.");
      return null;
    }
    const response = await fetch(API + "/materials/subject/" + subjects[0].id, {
      headers: { Authorization: "Bearer " + token() },
    });
    const list = await response.json();
    if (!list.length) {
      setQuestMessage("Add a note to your first study world first.");
      openSubject(subjects[0]);
      return null;
    }
    return list[0];
  }

  async function startFlashcards() {
    const material = await getFirstMaterial();
    if (!material) return;
    const response = await fetch(API + "/ai/flashcards", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: "Bearer " + token() },
      body: JSON.stringify({ material_id: material.id, count: 5 }),
    });
    const data = await response.json();
    if (!response.ok) {
      setQuestMessage(data.detail || "Could not generate flashcards.");
      return;
    }
    setFlashcards(data.flashcards);
    setFlashcardIndex(0);
    setFlashcardRevealed(false);
    setScreen("flashcards");
  }

  async function startBossQuiz() {
    const material = await getFirstMaterial();
    if (material) generateQuiz(material.id);
  }

  async function submitQuiz(event) {
    event.preventDefault();
    const response = await fetch(API + "/quizzes/" + quiz.quiz_id + "/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: "Bearer " + token() },
      body: JSON.stringify({ answers: quizAnswers }),
    });
    const data = await response.json();
    if (response.ok) setQuizResult(data);
  }

  function logout() {
    localStorage.removeItem("token");
    setScreen("login");
    setSubjects([]);
  }

  if (screen === "quiz" && quiz) {
    return (
      <main className="dashboard-page">
        <header className="dash-header">
          <button className="back-button" onClick={() => setScreen("subject")}>← MATERIAL</button>
          <div className="brand-row"><span className="brand-mark">◆</span><span>STUDYFORGE</span></div>
          <span className="player-chip">BOSS QUIZ</span>
        </header>
        <section className="dashboard-content quiz-content">
          <p className="eyebrow">// FINAL CHALLENGE</p>
          <h1 className="subject-title">Boss <span>Quiz</span></h1>
          <p className="subtitle">Choose carefully. Every answer earns knowledge.</p>
          {quizResult ? (
            <section className="result-card">
              <span className="result-star">✦</span>
              <p className="eyebrow">// QUEST COMPLETE</p>
              <h2>{quizResult.score >= 70 ? "World cleared!" : "Keep training!"}</h2>
              <strong>{quizResult.score}%</strong>
              <p>{quizResult.correct_answers} of {quizResult.total_questions} answers correct</p>
              <button className="primary-button" onClick={() => setScreen("subject")}>RETURN TO WORLD →</button>
            </section>
          ) : (
            <form className="quiz-form" onSubmit={submitQuiz}>
              {quiz.questions.map((question, index) => (
                <fieldset className="question-card" key={index}>
                  <legend><span>Q{index + 1}</span>{question.question}</legend>
                  <div className="options">
                    {question.options.map((option) => (
                      <label className="option" key={option}>
                        <input
                          type="radio"
                          name={"question-" + index}
                          value={option}
                          onChange={() => setQuizAnswers({ ...quizAnswers, [question.id || index]: option })}
                          required
                        />
                        <span>{option}</span>
                      </label>
                    ))}
                  </div>
                </fieldset>
              ))}
              <button className="primary-button submit-quiz" type="submit">SUBMIT BOSS QUIZ →</button>
            </form>
          )}
        </section>
      </main>
    );
  }

  if (screen === "flashcards" && flashcards.length) {
    const card = flashcards[flashcardIndex];
    const isLast = flashcardIndex === flashcards.length - 1;
    return (
      <main className="dashboard-page">
        <header className="dash-header">
          <button className="back-button" onClick={() => setScreen("dashboard")}>← HUB</button>
          <div className="brand-row"><span className="brand-mark">◆</span><span>STUDYFORGE</span></div>
          <span className="player-chip">FLASHCARD RUN</span>
        </header>
        <section className="dashboard-content flashcard-content">
          <p className="eyebrow">// MEMORY TRAINING</p>
          <h1 className="subject-title">Flashcard <span>Run</span></h1>
          <p className="subtitle">Card {flashcardIndex + 1} of {flashcards.length}</p>
          <button className={"flashcard " + (flashcardRevealed ? "revealed" : "")} onClick={() => setFlashcardRevealed(!flashcardRevealed)}>
            <span className="card-label">{flashcardRevealed ? "ANSWER" : "QUESTION"}</span>
            <strong>{flashcardRevealed ? card.answer : card.question}</strong>
            <small>{flashcardRevealed ? "Tap to see the question" : "Tap to reveal the answer"}</small>
          </button>
          <div className="flashcard-controls">
            <button className="secondary-button" disabled={flashcardIndex === 0} onClick={() => { setFlashcardIndex(flashcardIndex - 1); setFlashcardRevealed(false); }}>← PREVIOUS</button>
            <button className="primary-button" onClick={() => { if (isLast) setScreen("dashboard"); else { setFlashcardIndex(flashcardIndex + 1); setFlashcardRevealed(false); } }}>{isLast ? "FINISH RUN →" : "NEXT CARD →"}</button>
          </div>
        </section>
      </main>
    );
  }

  if (screen === "progress") {
    return (
      <main className="dashboard-page">
        <header className="dash-header">
          <button className="back-button" onClick={() => setScreen("dashboard")}>← HUB</button>
          <div className="brand-row"><span className="brand-mark">◆</span><span>STUDYFORGE</span></div>
          <span className="player-chip">PLAYER STATS</span>
        </header>
        <section className="dashboard-content">
          <p className="eyebrow">// PLAYER RECORD</p>
          <h1 className="subject-title">Your <span>progress.</span></h1>
          <p className="subtitle">Every attempt is proof that you are getting stronger.</p>
          <div className="progress-stat-grid">
            <div className="progress-big-card purple"><small>QUIZZES TAKEN</small><strong>{progress.quizzes_taken}</strong><span>quests completed</span></div>
            <div className="progress-big-card pink"><small>AVERAGE SCORE</small><strong>{progress.average_score}%</strong><span>your current power</span></div>
            <div className="progress-big-card blue"><small>BEST SCORE</small><strong>{progress.best_score}%</strong><span>personal record</span></div>
          </div>
          <section className="progress-panel">
            <div className="section-heading"><div><p className="eyebrow">// TRAINING LOG</p><h2>Recent attempts</h2></div><span className="mission-count">{progress.total_correct_answers} / {progress.total_questions} CORRECT</span></div>
            {progress.recent_attempts.length ? progress.recent_attempts.map((attempt, index) => (
              <div className="attempt-row" key={index}><span className="attempt-icon">✦</span><div><b>{attempt.quiz_title}</b><small>{new Date(attempt.submitted_at).toLocaleDateString()}</small></div><strong>{attempt.score}%</strong></div>
            )) : <div className="empty-world">Complete your first Boss Quiz to unlock your training history.</div>}
          </section>
          <section className="level-panel"><div><p className="eyebrow">// NEXT LEVEL</p><h2>ROOKIE → SCHOLAR</h2><p>Complete more quests to power up your rank.</p></div><div className="level-track"><span style={{ width: Math.min(progress.quizzes_taken * 20, 100) + "%" }} /></div></section>
        </section>
      </main>
    );
  }

  if (screen === "subject" && selectedSubject) {
    return (
      <main className="dashboard-page">
        <header className="dash-header">
          <button className="back-button" onClick={() => setScreen("dashboard")}>← WORLDS</button>
          <div className="brand-row"><span className="brand-mark">◆</span><span>STUDYFORGE</span></div>
          <button className="logout-button" onClick={logout}>LOG OUT</button>
        </header>
        <section className="dashboard-content subject-content">
          <p className="eyebrow">// STUDY WORLD</p>
          <h1 className="subject-title">{selectedSubject.name}</h1>
          <p className="subtitle">Collect knowledge. Complete quests. Master this world.</p>

          <div className="subject-actions">
            <div className="action-badge">✦ {materials.length} MATERIALS</div>
            <button className="primary-button" onClick={() => document.getElementById("add-note").scrollIntoView({ behavior: "smooth" })}>+ ADD NOTE</button>
          </div>

          <div className="material-layout">
            <section>
              <div className="section-heading"><div><p className="eyebrow">// KNOWLEDGE LOOT</p><h2>Your materials</h2></div></div>
              <div className="material-list">
                {materials.map((material) => (
                  <article className="material-card" key={material.id}>
                    <div><span className="material-icon">▣</span><h3>{material.title}</h3><p>{material.content.slice(0, 130)}{material.content.length > 130 ? "..." : ""}</p></div>
                    <div className="material-buttons">
                      <button className="summary-button" onClick={() => generateSummary(material.id)}>AI SUMMARY →</button>
                      <button className="quiz-button" onClick={() => generateQuiz(material.id)}>BOSS QUIZ →</button>
                    </div>
                  </article>
                ))}
                {materials.length === 0 && <div className="empty-world">No notes yet. Add your first piece of knowledge below.</div>}
              </div>
            </section>

            <form id="add-note" className="note-card" onSubmit={addMaterial}>
              <p className="eyebrow">// NEW KNOWLEDGE</p>
              <h2>Add a study note</h2>
              <input placeholder="Note title" value={materialTitle} onChange={(event) => setMaterialTitle(event.target.value)} required />
              <textarea placeholder="Paste or write your study material here..." value={materialContent} onChange={(event) => setMaterialContent(event.target.value)} required />
              <button className="primary-button" type="submit">SAVE TO WORLD →</button>
            </form>
          </div>

          {summary && <section className="summary-panel"><p className="eyebrow">// AI INTEL</p><h2>Study summary</h2><div>{summary}</div></section>}
        </section>
      </main>
    );
  }

  if (screen === "dashboard") {
    return (
      <main className="dashboard-page">
        <header className="dash-header">
          <div className="brand-row"><span className="brand-mark">◆</span><span>STUDYFORGE</span></div>
          <div className="player-chip">PLAYER 01 <span>LVL 01</span></div>
          <button className="logout-button" onClick={logout}>LOG OUT</button>
        </header>
        <section className="dashboard-content">
          <div className="welcome-row animate-in"><div><p className="eyebrow">// PLAYER HUB</p><h1>Ready for your<br /><span>next quest?</span></h1><p className="dashboard-intro">Your knowledge journey starts with one curious thought.</p></div><div className="streak-card floating"><span className="flame">✦</span><strong>0 DAY</strong><small>study streak</small></div></div>
          <div className="stat-grid"><button className="stat-card stat-button" onClick={() => setScreen("progress")}><small>XP EARNED</small><strong>{progress.total_correct_answers * 10}</strong><span>view player stats →</span></button><button className="stat-card pink stat-button" onClick={() => setScreen("progress")}><small>QUESTS DONE</small><strong>{progress.quizzes_taken}</strong><span>view training log →</span></button><button className="stat-card blue stat-button" onClick={() => setScreen("progress")}><small>SKILL RANK</small><strong>{progress.quizzes_taken >= 5 ? "SCHOLAR" : "ROOKIE"}</strong><span>keep exploring</span></button></div>
          <section className="quote-card animate-in"><span className="quote-mark">“</span><div><p>{quote}</p><small>— YOUR FUTURE SELF</small></div><span className="quote-sparkle">✦</span></section>
          <section className="quest-section"><div className="section-heading"><div><p className="eyebrow">// TODAY'S MISSIONS</p><h2>Choose your quest</h2></div><span className="mission-count">0 / 3 COMPLETE</span></div><div className="quest-grid"><button className="quest-card purple" onClick={() => subjects.length ? openSubject(subjects[0]) : setQuestMessage("Create a study world first to unlock quests.")}><span className="quest-icon">✎</span><span><b>READ & DISCOVER</b><small>Explore a study material</small></span><strong>+20 XP</strong></button><button className="quest-card pink" onClick={startFlashcards}><span className="quest-icon">✦</span><span><b>FLASHCARD RUN</b><small>Review your memory deck</small></span><strong>+30 XP</strong></button><button className="quest-card blue" onClick={startBossQuiz}><span className="quest-icon">◆</span><span><b>BOSS QUIZ</b><small>Test what you know</small></span><strong>+50 XP</strong></button></div>{questMessage && <p className="quest-message">{questMessage}</p>}</section>
          <section className="journey-section"><div className="section-heading"><div><p className="eyebrow">// YOUR POWER-UP PLAN</p><h2>Three steps to mastery</h2></div></div><div className="journey-grid"><div className="journey-step active"><span>01</span><b>COLLECT</b><p>Save notes and ideas in your study worlds.</p></div><div className="journey-line" /><div className="journey-step"><span>02</span><b>TRAIN</b><p>Turn knowledge into summaries and flashcards.</p></div><div className="journey-line" /><div className="journey-step"><span>03</span><b>CONQUER</b><p>Beat quizzes and watch your progress grow.</p></div></div></section>
          <section className="world-section"><div className="section-heading"><div><p className="eyebrow">// YOUR WORLDS</p><h2>Study subjects</h2></div><span className="mission-count">{subjects.length} WORLDS</span></div><form className="add-world" onSubmit={createSubject}><input placeholder="Name a new study world..." value={newSubject} onChange={(event) => setNewSubject(event.target.value)} /><button type="submit">+ ADD WORLD</button></form><div className="world-grid">{subjects.map((subject) => <button className="world-card" key={subject.id} style={{ "--world-color": subject.color }} onClick={() => openSubject(subject)}><span className="world-symbol">◆</span><b>{subject.name}</b><small>ENTER WORLD →</small></button>)}{subjects.length === 0 && <div className="empty-world">Your first world is waiting to be created above.</div>}</div></section>
        </section>
      </main>
    );
  }

  return (
    <main className="game-page"><div className="scanlines" /><section className="login-shell"><div className="brand-row"><span className="brand-mark">◆</span><span>STUDYFORGE</span><span className="status">● ONLINE</span></div><div className="hero-copy"><p className="eyebrow">// LEARNING ADVENTURE SYSTEM</p><h1>Level up<br /><span>your mind.</span></h1><p className="subtitle">Turn notes into quests, quizzes, and victories.</p></div><div className="login-card"><div className="card-top"><span>{signup ? "NEW PLAYER" : "PLAYER LOGIN"}</span><span>✦ 001</span></div><h2>{signup ? "Create your player" : "Welcome back, player"}</h2><p className="card-help">{signup ? "Start your study adventure." : "Ready for your next quest?"}</p><form onSubmit={submitAuth}>{signup && <input placeholder="Player name" value={name} onChange={(event) => setName(event.target.value)} required />}<input type="email" placeholder="Email address" value={email} onChange={(event) => setEmail(event.target.value)} required /><input type="password" placeholder="Password" value={password} onChange={(event) => setPassword(event.target.value)} required /><button className="primary-button" type="submit">{signup ? "START ADVENTURE  →" : "ENTER THE FORGE  →"}</button></form>{message && <p className="message">{message}</p>}<button className="switch-button" onClick={() => setSignup(!signup)}>{signup ? "← I already have a player account" : "Create a new player account →"}</button></div><div className="feature-row"><span>✦ AI POWERED</span><span>✦ DAILY QUESTS</span><span>✦ XP & STREAKS</span></div></section></main>
  );
}

export default App;
