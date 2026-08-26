import type { Config } from 'tailwindcss';
export default { content:['./app/**/*.{ts,tsx}','./components/**/*.{ts,tsx}'], theme:{extend:{colors:{ink:'#0a1023'},boxShadow:{glow:'0 10px 50px rgba(99,102,241,.25)'}}}, plugins:[] } satisfies Config;
