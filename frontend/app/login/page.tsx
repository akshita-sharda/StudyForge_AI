'use client';
import {useState} from 'react';
import Link from 'next/link';
import {useRouter} from 'next/navigation';
import {api} from '@/lib/api';
import {Auth, Input} from '@/components/auth';

export default function Login(){
  const [email,setEmail]=useState('');
  const [password,setPassword]=useState('');
  const [keepSignedIn,setKeepSignedIn]=useState(false);
  const [error,setError]=useState('');
  const router=useRouter();
  async function submit(e:React.FormEvent){
    e.preventDefault();
    try {
      const r=await api('/auth/login',{method:'POST',body:JSON.stringify({email,password})});
      localStorage.removeItem('sf_token');
      sessionStorage.removeItem('sf_token');
      (keepSignedIn ? localStorage : sessionStorage).setItem('sf_token',r.access_token);
      router.push('/dashboard');
    } catch(e) { setError(e instanceof Error?e.message:'Try again'); }
  }
  return <Auth title="Welcome back" sub="Your next breakthrough is waiting."><form onSubmit={submit} className="space-y-4"><Input label="Email" type="email" value={email} set={setEmail}/><Input label="Password" type="password" value={password} set={setPassword}/><label className="keep-signed-in"><input type="checkbox" checked={keepSignedIn} onChange={e=>setKeepSignedIn(e.target.checked)}/><span>Keep me signed in on this device</span></label>{error&&<p className="text-sm text-rose-600">{error}</p>}<button className="cute-button w-full py-3">Continue →</button><p className="text-center text-sm text-emerald-950/60">New here? <Link href="/signup" className="font-bold text-emerald-700">Create account</Link></p></form></Auth>;
}
