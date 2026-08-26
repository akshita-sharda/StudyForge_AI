'use client';
import Link from 'next/link';
import {LayoutDashboard, MessageSquare, FileText, Sparkles, CalendarDays, Leaf, UserRound} from 'lucide-react';

const links=[['Dashboard','/dashboard',LayoutDashboard],['Library','/library',FileText],['AI Workspace','/workspace',MessageSquare],['Quiz Forge','/quiz',Sparkles],['Study Plan','/plan',CalendarDays],['Player Profile','/profile',UserRound]] as const;

export function Nav(){return <aside className="hidden w-64 shrink-0 border-r border-emerald-950/10 bg-[#173c35] p-5 text-white lg:block"><Link href="/dashboard" className="mb-10 flex items-center gap-2 text-xl font-black"><span className="rounded-2xl bg-[#bfe8d2] p-2 text-[#173c35]"><Leaf size={19}/></span>StudyForge</Link><nav className="space-y-2">{links.map(([name,href,Icon])=><Link key={href} href={href} className="flex items-center gap-3 rounded-2xl px-3 py-3 text-sm font-semibold text-emerald-100/70 transition hover:translate-x-1 hover:bg-white/10 hover:text-white"><Icon size={18}/>{name}</Link>)}</nav><div className="mt-12 rounded-3xl bg-[#2f8065] p-4 text-sm shadow-[0_6px_0_#102d27]"><p className="font-bold">Your study garden 🌱</p><p className="mt-1 text-xs text-emerald-50/75">Water one small habit today.</p></div></aside>}
