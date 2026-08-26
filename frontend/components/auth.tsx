import Link from 'next/link';

export function Auth({title, sub, children}:{title:string, sub:string, children:React.ReactNode}) {
  return <main className="aurora grid min-h-screen place-items-center p-5 text-[#173c35]"><section className="glass w-full max-w-md rounded-[2rem] p-8"><Link href="/" className="text-sm font-black text-emerald-800">✦ StudyForge AI</Link><h1 className="mt-8 text-3xl font-black text-emerald-950">{title}</h1><p className="mb-7 mt-2 text-emerald-950/60">{sub}</p>{children}</section></main>;
}

export function Input({label,type,value,set}:{label:string,type:string,value:string,set:(v:string)=>void}) {
  return <label className="block text-sm font-semibold text-emerald-950">{label}<input required type={type} value={value} onChange={e=>set(e.target.value)} className="mt-2 w-full rounded-2xl border-2 border-emerald-900/10 bg-white/80 px-4 py-3 text-emerald-950 outline-none transition focus:border-emerald-500 focus:shadow-[0_4px_0_#bfe8d2]"/></label>;
}
