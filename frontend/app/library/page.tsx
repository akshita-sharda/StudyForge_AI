'use client';

import {FormEvent, useEffect, useState} from 'react';
import {ArrowUpRight, FileText, FileUp, Leaf, Trash2, UploadCloud} from 'lucide-react';
import Link from 'next/link';
import {Shell} from '@/components/shell';
import {api} from '@/lib/api';

export default function Library(){
  const [docs,setDocs]=useState<any[]>([]); const [file,setFile]=useState<File>(); const [title,setTitle]=useState(''); const [subject,setSubject]=useState(''); const [busy,setBusy]=useState(false); const [error,setError]=useState('');
  const load=()=>api('/documents').then(setDocs).catch((e)=>setError(e.message)); useEffect(()=>{void load()},[]);
  async function upload(e:FormEvent){e.preventDefault();if(!file)return;setBusy(true);setError('');const form=new FormData();form.append('file',file);form.append('title',title);form.append('subject',subject);try{await api('/documents',{method:'POST',body:form});setTitle('');setSubject('');setFile(undefined);await load()}catch(e){setError(e instanceof Error?e.message:'Could not forge this PDF.')}finally{setBusy(false)}}
  return <Shell><main className="vault-page">
    <header className="vault-heading"><div><p className="eyebrow">// SOURCE VAULT / YOUR TERRAIN</p><h1>Feed the forge.</h1><p>Turn your PDFs into places you can return to, question, and master.</p></div><div className="vault-counter"><Leaf size={18}/><strong>{docs.length}</strong><span>sources planted</span></div></header>
    <form onSubmit={upload} className="upload-station"><div className="upload-icon"><UploadCloud size={27}/></div><div className="upload-copy"><p className="eyebrow">NEW SOURCE DROP</p><h2>Plant a new island</h2><p>PDF only. We&apos;ll extract the pages and build an evidence trail.</p></div><div className="upload-fields"><input required placeholder="Name this source" value={title} onChange={e=>setTitle(e.target.value)}/><input required placeholder="Subject / world" value={subject} onChange={e=>setSubject(e.target.value)}/><label className="file-drop"><FileUp size={17}/>{file?.name||'Choose PDF'}<input className="hidden" type="file" accept="application/pdf" onChange={e=>setFile(e.target.files?.[0])}/></label><button disabled={busy||!file} className="cute-button">{busy?'Forging…':'Plant source →'}</button></div></form>
    {error&&<div className="error-banner">{error}</div>}
    <div className="vault-grid">{docs.map((d,i)=><article key={d.id} className={'source-artifact artifact-'+(i%4)}><div className="artifact-top"><span className="artifact-number">0{i+1}</span><FileText size={20}/><button onClick={async()=>{await api('/documents/'+d.id,{method:'DELETE'});load()}} aria-label="Delete document"><Trash2 size={16}/></button></div><p className="eyebrow">{d.subject.toUpperCase()} · {d.status}</p><h2>{d.title}</h2><p className="artifact-file">{d.filename}</p><Link href={'/workspace?doc='+d.id}>Open observatory <ArrowUpRight size={15}/></Link></article>)}{!docs.length&&<div className="empty-vault"><span>✦</span><h2>The vault is quiet.</h2><p>Plant your first PDF above and your study world will begin to grow.</p></div>}</div>
  </main></Shell>
}
