'use client';

import {FormEvent, useEffect, useState} from 'react';
import Link from 'next/link';
import {usePathname} from 'next/navigation';
import {ArrowUpRight, Brain, Send, Sparkles, X} from 'lucide-react';
import {api, token} from '@/lib/api';

type Message={role:'user'|'ai';text:string};

export function MiraIcon({small=false}:{small?:boolean}){
  return <span className={'mira-icon '+(small?'small':'')} aria-hidden="true"><Brain size={small?16:21}/><Sparkles className="mira-icon-spark" size={small?8:10}/></span>;
}

export function MiraWidget(){
  const pathname=usePathname();
  const [open,setOpen]=useState(false); const [docs,setDocs]=useState<any[]>([]); const [me,setMe]=useState<any>(); const [doc,setDoc]=useState<number>(); const [question,setQuestion]=useState(''); const [messages,setMessages]=useState<Message[]>([]); const [busy,setBusy]=useState(false); const [error,setError]=useState('');
  useEffect(()=>{if(open&&token()&&!docs.length){Promise.all([api('/documents'),api('/auth/me')]).then(([items,user])=>{setDocs(items);setMe(user);setDoc(items[0]?.id)}).catch(()=>setError('Open the full observatory after signing in.'))}},[open,docs.length]);
  const name=me?.name?.split(' ')[0]||'Scholar'; const goal=me?.goals?.[0]||'make steady progress';
  async function send(e:FormEvent){e.preventDefault();if(!question.trim()||busy)return;if(!token()){setError('Sign in first so Mira can learn with you.');return}if(!doc){setError('Plant a PDF first so Mira has something to teach from.');return}const text=question.trim();setMessages((current)=>[...current,{role:'user',text}]);setQuestion('');setBusy(true);setError('');try{const response=await Promise.all([api('/chat',{method:'POST',body:JSON.stringify({document_id:doc,question:text,history:messages.slice(-8)})}),new Promise(resolve=>setTimeout(resolve,900))]).then(([answer])=>answer as any);setMessages((current)=>[...current,{role:'ai',text:response.answer}])}catch(err){setError(err instanceof Error?err.message:'Mira is taking a short pause.')}finally{setBusy(false)}}
  return <div className={'mira-widget '+(pathname==='/workspace'?'observatory-mira':'')}><button className={'mira-fab '+(open?'active':'')} onClick={()=>setOpen(!open)} aria-label={open?'Close Mira':'Open Mira'}>{open?<X size={22}/>:<MiraIcon/>}<span className="mira-fab-ping"/></button>{open&&<section className="mira-popover" aria-label="Mira assistant"><header><MiraIcon small/><div><b>Mira</b><span>Personal coach for {name}</span></div><button onClick={()=>setOpen(false)} aria-label="Close Mira"><X size={16}/></button></header><div className="mira-mini-body">{!messages.length?<><div className="mira-greeting"><p>Hi {name}, I&apos;m Mira 🌱</p><span>I remember that you&apos;re working to {goal.toLowerCase()}. What should we tackle?</span></div><div className="mira-prompts"><button onClick={()=>setQuestion('What should I study next?')}>Choose my next move</button><button onClick={()=>setQuestion('Give me a memory trick.')}>Memory trick</button><button onClick={()=>setQuestion('Quiz me one question at a time.')}>Quiz me</button></div></>:messages.slice(-4).map((message,index)=><div className={'mira-mini-message '+message.role} key={index}>{message.text}</div>)}{busy&&<div className="mira-mini-message ai">Mira is thinking…</div>}{error&&<small className="mira-error">{error}</small>}</div><form onSubmit={send} className="mira-mini-input"><input value={question} onChange={e=>setQuestion(e.target.value)} placeholder={`Ask Mira, ${name}…`}/><button aria-label="Send"><Send size={15}/></button></form><Link href="/workspace" className="mira-full-link">Open full observatory <ArrowUpRight size={14}/></Link></section>}</div>;
}
