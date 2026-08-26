import './globals.css'; import type { Metadata } from 'next'; import {MiraWidget} from '@/components/mira-widget';
export const metadata: Metadata = { title:'StudyForge AI', description:'Turn study material into momentum.' };
export default function Layout({children}:{children:React.ReactNode}) { return <html lang="en"><body>{children}<MiraWidget/></body></html>; }
