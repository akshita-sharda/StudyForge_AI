'use client';

import {useEffect, useState} from 'react';
import {motion} from 'framer-motion';
import {Check, ChevronRight, Flame, LockKeyhole, RotateCcw, Sparkles, Trophy, X} from 'lucide-react';
import {Shell} from '@/components/shell';
import {api} from '@/lib/api';

type Question = {question:string; options:string[]; correct_index:number; explanation?:string};

export default function Quiz(){
  const [docs,setDocs]=useState<any[]>([]);
  const [doc,setDoc]=useState('');
  const [questions,setQuestions]=useState<Question[]>([]);
  const [answers,setAnswers]=useState<number[]>([]);
  const [result,setResult]=useState<any>();
  const [error,setError]=useState('');
  const [loading,setLoading]=useState(false);
  const [submitting,setSubmitting]=useState(false);

  useEffect(()=>{ api('/documents').then(setDocs).catch((e)=>setError(e.message)); },[]);

  async function generate(){
    setError(''); setLoading(true); setResult(undefined);
    try {
      const response=await api('/quizzes/generate',{method:'POST',body:JSON.stringify({document_id:Number(doc),count:5})});
      setQuestions(response.questions || []); setAnswers([]);
      if (!response.questions?.length) setError('This source needs a little more text before it can become a quest.');
    } catch(e) { setError(e instanceof Error ? e.message : 'The quest generator is offline.'); }
    finally { setLoading(false); }
  }

  async function submit(){
    if (answers.length !== questions.length || answers.some((answer)=>answer === undefined)) { setError('Choose an answer for every encounter first.'); return; }
    setError(''); setSubmitting(true);
    try { setResult(await api('/quizzes/submit',{method:'POST',body:JSON.stringify({document_id:Number(doc),questions,answers:answers.map(correct_index=>({correct_index}))})})); }
    catch(e) { setError(e instanceof Error ? e.message : 'Could not save this attempt.'); }
    finally { setSubmitting(false); }
  }

  function choose(questionIndex:number, optionIndex:number){ setAnswers((current)=>{const next=[...current]; next[questionIndex]=optionIndex; return next;}); }

  return <Shell><main className="quiz-world aurora min-h-screen -m-6 p-6 md:-m-10 md:p-10">
    <div className="mx-auto max-w-5xl">
      <header className="mb-8 flex flex-col justify-between gap-5 md:flex-row md:items-end">
        <div><p className="eyebrow">// RECALL REEF / BOSS ENCOUNTER</p><h1 className="mt-2 text-4xl font-black tracking-tight md:text-6xl">Make your notes<br/><span className="gradient-text">fight back.</span></h1><p className="mt-3 max-w-xl text-emerald-950/60">A quiz should feel like a small adventure—not a worksheet.</p></div>
        <div className="quiz-streak"><Flame size={18}/> Keep the signal alive</div>
      </header>

      {!questions.length && <section className="quest-launch glass rounded-[2rem] p-7 md:p-10">
        <div className="mb-7 flex items-center gap-4"><div className="quest-orb"><Sparkles size={25}/></div><div><p className="eyebrow">CHOOSE YOUR TERRAIN</p><h2 className="text-2xl font-black">Which source are we entering?</h2></div></div>
        <select value={doc} onChange={e=>setDoc(e.target.value)} className="w-full rounded-2xl border-2 border-emerald-950/10 bg-white/75 p-4 font-bold outline-none focus:border-emerald-600"><option value="">Select a ready document</option>{docs.map(d=><option key={d.id} value={d.id}>{d.title} · {d.subject}</option>)}</select>
        <button disabled={!doc||loading} onClick={generate} className="cute-button mt-5 inline-flex items-center gap-2 disabled:cursor-not-allowed disabled:opacity-45">{loading?'Forging encounters…':'Enter the reef'} <ChevronRight size={18}/></button>
        <p className="mt-5 flex items-center gap-2 text-xs text-emerald-950/50"><LockKeyhole size={14}/> Every answer is checked against your uploaded source.</p>
      </section>}

      {!!questions.length && !result && <section className="space-y-5">
        <div className="quiz-progress"><span>{answers.filter((a)=>a!==undefined).length} / {questions.length} encounters answered</span><div><i style={{width:`${(answers.filter((a)=>a!==undefined).length/questions.length)*100}%`}}/></div></div>
        {questions.map((q,i)=><motion.article initial={{opacity:0,y:12}} animate={{opacity:1,y:0}} transition={{delay:i*.06}} key={i} className="encounter-card">
          <div className="flex items-start justify-between gap-4"><div><p className="eyebrow">ENCOUNTER {String(i+1).padStart(2,'0')}</p><h2>{q.question}</h2></div><span className="encounter-number">{i+1}</span></div>
          <div className="mt-6 grid gap-3">{q.options.map((option,j)=><button onClick={()=>choose(i,j)} key={j} className={`answer-choice ${answers[i]===j?'selected':''}`}><span className="answer-letter">{String.fromCharCode(65+j)}</span><span>{option}</span>{answers[i]===j&&<Check size={18}/>}</button>)}</div>
        </motion.article>)}
        {error&&<ErrorBanner text={error}/>}<button onClick={submit} disabled={submitting} className="cute-button inline-flex items-center gap-2 disabled:opacity-50">{submitting?'Saving your run…':'Finish encounter'} <Trophy size={18}/></button>
      </section>}

      {result && <motion.section initial={{opacity:0,scale:.97}} animate={{opacity:1,scale:1}} className="result-card"><div className="result-badge"><Trophy size={26}/></div><p className="eyebrow">ENCOUNTER COMPLETE</p><h2>{result.score === result.total ? 'Perfect signal.' : result.score >= result.total/2 ? 'You found the trail.' : 'The map is still growing.'}</h2><div className="result-score">{result.score}<small>/{result.total}</small></div><p>+{result.xp_earned} XP added to your summit.</p><button onClick={()=>{setQuestions([]);setAnswers([]);setResult(undefined);}} className="cute-button mt-6 inline-flex items-center gap-2"><RotateCcw size={17}/> Run another encounter</button></motion.section>}
      {error&&!questions.length&&<ErrorBanner text={error}/>} 
    </div>
  </main></Shell>;
}

function ErrorBanner({text}:{text:string}){return <div className="error-banner"><X size={17}/><span>{text}</span></div>}
