'use client';

import {useEffect, useState} from 'react';
import {Award, Flame, Leaf, Pencil, Shield, Sparkles, Trophy} from 'lucide-react';
import {Shell} from '@/components/shell';
import {api} from '@/lib/api';

export default function Profile(){
  const [me,setMe]=useState<any>(); const [progress,setProgress]=useState<any>(); const [editing,setEditing]=useState(false); const [name,setName]=useState('');
  useEffect(()=>{api('/auth/me').then((user)=>{setMe(user);setName(user.name)});api('/progress').then(setProgress)},[]);
  const xp=progress?.xp||me?.xp||0; const level=Math.floor(xp/100)+1;
  return <Shell><main className="profile-page"><header className="profile-hero"><div className="avatar-orbit"><div>{(name||'E').slice(0,1).toUpperCase()}</div><span>✦</span></div><div><p className="eyebrow">// PLAYER PROFILE / STUDYFORGE</p><h1>{name||'Explorer'}</h1><p>Your learning world, your pace, your rules.</p></div><button onClick={()=>setEditing(!editing)} className="profile-edit"><Pencil size={15}/>{editing?'Close':'Edit profile'}</button></header>
    {editing&&<section className="profile-edit-panel"><label>Display name<input value={name} onChange={e=>setName(e.target.value)}/></label><button onClick={()=>{setMe({...me,name});setEditing(false)}} className="cute-button">Save locally</button></section>}
    <div className="profile-stats"><div><Flame/><strong>{me?.streak||1}</strong><span>day flame</span></div><div><Sparkles/><strong>{xp}</strong><span>forge XP</span></div><div><Shield/><strong>Level {level}</strong><span>current rank</span></div></div>
    <section className="profile-layout"><div className="profile-panel"><div className="panel-heading"><span><Trophy size={18}/> Badges earned</span><small>{progress?.badges?.length||0} unlocked</small></div><div className="badge-grid"><div className="badge unlocked"><Award/><b>First Spark</b><small>Started your journey</small></div><div className={'badge '+(xp>=100?'unlocked':'locked')}><Leaf/><b>Green Thumb</b><small>Reach 100 XP</small></div><div className="badge locked"><Trophy/><b>Boss Breaker</b><small>Complete 5 quizzes</small></div></div></div><div className="profile-panel identity-panel"><div className="panel-heading"><span>Learning identity</span><small>from onboarding</small></div><p className="identity-label">Preferred vibe</p><strong>{me?.learning_style||'Visual'}</strong><p className="identity-label">Current mission</p><strong>{me?.goals?.[0]||'Build consistency'}</strong><div className="profile-quote">“Small sessions. Huge confidence.”</div></div></section>
  </main></Shell>
}
