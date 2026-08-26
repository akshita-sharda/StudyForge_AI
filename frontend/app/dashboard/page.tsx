'use client';

import {useEffect, useState} from 'react';
import Link from 'next/link';
import {motion} from 'framer-motion';
import {ArrowUpRight, BookOpen, Compass, FileText, Flame, Leaf, MessageCircle, Sparkles, Trophy} from 'lucide-react';
import {api} from '@/lib/api';

type DocumentItem = {id:number; title:string; subject:string; status:string};

export default function Dashboard(){
  const [me,setMe]=useState<any>();
  const [progress,setProgress]=useState<any>();
  const [docs,setDocs]=useState<DocumentItem[]>([]);

  useEffect(()=>{
    api('/auth/me').then(setMe).catch(()=>location.href='/login');
    api('/progress').then(setProgress);
    api('/documents').then(setDocs);
  },[]);

  const firstDoc=docs[0];
  const level=Math.floor((progress?.xp||0)/100)+1;

  return <main className="map-page aurora min-h-screen overflow-hidden px-5 pb-12 text-[#173c35] md:px-10">
    <header className="map-header mx-auto flex max-w-7xl items-center justify-between py-6">
      <Link href="/dashboard" className="flex items-center gap-2 text-lg font-black"><span className="rounded-xl bg-[#173c35] p-2 text-[#bfe8d2]">✦</span>StudyForge</Link>
      <nav className="hidden items-center gap-6 text-sm font-bold text-emerald-950/55 md:flex"><Link href="/library" className="hover:text-emerald-700">Source library</Link><Link href="/workspace" className="hover:text-emerald-700">AI observatory</Link><Link href="/quiz" className="hover:text-emerald-700">Boss encounters</Link></nav>
      <div className="flex items-center gap-3"><span className="hidden rounded-full bg-white/70 px-3 py-2 text-xs font-bold text-emerald-800 sm:block">LEVEL {level}</span><Link href="/library" className="rounded-full bg-emerald-800 px-4 py-2 text-xs font-bold text-white shadow-[0_3px_0_#123d32]">+ SOURCE</Link></div>
    </header>

    <section className="mx-auto max-w-7xl">
      <div className="mb-7 flex flex-col justify-between gap-5 md:flex-row md:items-end">
        <div><p className="eyebrow">// YOUR LIVING KNOWLEDGE WORLD</p><h1 className="mt-2 text-4xl font-black tracking-tight md:text-6xl">Welcome back, {me?.name?.split(' ')[0]||'explorer'}.</h1><p className="mt-3 max-w-xl text-emerald-950/60">Every source you add becomes terrain. Every question lights a path.</p></div>
        <div className="flex items-center gap-2 text-sm font-bold text-emerald-800"><Flame size={18} className="text-[#f27f68]"/> {progress?.streak||1} day learning flame</div>
      </div>

      <div className="knowledge-map">
        <div className="map-toolbar"><span><Compass size={16}/> KNOWLEDGE MAP / SECTOR 01</span><span>{docs.length} SOURCE{docs.length===1?'':'S'} DISCOVERED</span></div>
        <div className="map-canvas">
          <div className="map-grid-lines"/>
          <div className="map-orbit orbit-one"/>
          <div className="map-orbit orbit-two"/>
          <div className="path-line path-one"/>
          <div className="path-line path-two"/>
          <div className="path-line path-three"/>

          <MapIsland className="island-source float-source" color="mint" icon={<FileText size={22}/>} eyebrow="SOURCE GROVE" title={docs.length ? docs[0].subject : 'Unplanted ground'} detail={docs.length ? docs.length+' document'+(docs.length===1?'':'s') : 'Plant your first PDF'} href="/library" pulse={docs.length===0}/>
          <MapIsland className="island-ai float-ai" color="lilac" icon={<MessageCircle size={22}/>} eyebrow="AI OBSERVATORY" title="Ask the evidence" detail="Grounded answers with page trails" href={firstDoc?'/workspace?doc='+firstDoc.id:'/workspace'} />
          <MapIsland className="island-quiz float-quiz" color="peach" icon={<Sparkles size={22}/>} eyebrow="RECALL REEF" title="Boss encounter" detail="Turn knowledge into confidence" href="/quiz" />
          <MapIsland className="island-summit float-summit" color="forest" icon={<Trophy size={22}/>} eyebrow="MASTERY SUMMIT" title={progress?.xp ? progress.xp+' XP earned' : 'Your summit awaits'} detail={progress?.recent_scores?.length ? 'Keep climbing your best score' : 'Complete a first encounter'} href="/quiz" />

          <motion.div className="map-spark spark-a" animate={{y:[0,-10,0],opacity:[.45,1,.45]}} transition={{duration:2.8,repeat:Infinity}}><Leaf size={18}/></motion.div>
          <motion.div className="map-spark spark-b" animate={{scale:[.8,1.2,.8],rotate:[0,20,0]}} transition={{duration:3.4,repeat:Infinity}}><Sparkles size={16}/></motion.div>
        </div>
        <div className="map-legend"><span><i className="legend-dot mint"/> active source</span><span><i className="legend-dot lilac"/> AI layer</span><span><i className="legend-dot peach"/> challenge</span><span><i className="legend-dot forest"/> mastery</span></div>
      </div>

      <div className="mt-6 grid gap-5 lg:grid-cols-[1.2fr_.8fr]">
        <motion.section initial={{opacity:0,y:15}} animate={{opacity:1,y:0}} className="quest-banner">
          <div><p className="eyebrow">// NEXT TRANSMISSION</p><h2>{docs.length ? 'Ask one brave question.' : 'Plant the first island.'}</h2><p>{docs.length ? 'Open the observatory and interrogate your notes.' : 'Upload a PDF and watch StudyForge turn it into a navigable world.'}</p></div>
          <Link href={docs.length?'/workspace?doc='+firstDoc.id:'/library'} className="cute-button inline-flex items-center gap-2">{docs.length?'Open observatory':'Open source vault'} <ArrowUpRight size={17}/></Link>
        </motion.section>
        <section className="quote-panel"><span className="quote-symbol">“</span><div><p>Consistency is not a personality trait. It is a world you keep returning to.</p><small>FIELD NOTE / STUDYFORGE</small></div></section>
      </div>
    </section>
  </main>;
}

function MapIsland({className,color,icon,eyebrow,title,detail,href,pulse}:{className:string;color:string;icon:React.ReactNode;eyebrow:string;title:string;detail:string;href:string;pulse?:boolean}){
  return <Link href={href} className={'map-island '+className+' island-'+color+(pulse?' island-pulse':'')}><span className="island-icon">{icon}</span><span className="island-eyebrow">{eyebrow}</span><strong>{title}</strong><small>{detail}</small><span className="island-arrow">↗</span></Link>;
}
