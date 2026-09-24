import { validateDaily, validateCollection } from './daily-view.mjs';
export const REMOTE = 'https://raw.githubusercontent.com/DRKREDDY5/Knowledge-Pill/main/editions/latest.json';
export const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function safeURL(value) { try { const u = new URL(value); return u.protocol === 'https:' && !u.username && !u.password ? u.href : null; } catch { return null; } }
export function mergeEditions(existing, incoming) {
  const checked = validateCollection({task:'daily_pills_collection',packets:incoming});
  const byId = new Map();
  for (const p of existing) { try { validateDaily(p); byId.set(p.id,p); } catch {} }
  for (const p of checked) {
    const old = byId.get(p.id);
    if (old && (old.date !== p.date || old.topic !== p.topic || old.language !== p.language)) throw Error('An edition has conflicting identity details. Your saved pills are safe.');
    if (!old || Date.parse(p.created_at) >= Date.parse(old.created_at)) byId.set(p.id,p);
  }
  return [...byId.values()].sort((a,b)=>a.date.localeCompare(b.date)||a.created_at.localeCompare(b.created_at)).slice(-30);
}
export async function refreshEditions(existing, fetcher = fetch) {
  const response = await fetcher(REMOTE,{cache:'no-store',signal:AbortSignal.timeout(15000)});
  if (!response.ok) throw Error('The edition service is unavailable. Your saved pills are still here.');
  const body = await response.text();
  if (body.length > 2000000) throw Error('The edition download was too large. Your saved pills were kept.');
  const packets = validateCollection(JSON.parse(body));
  return mergeEditions(existing,packets);
}
export function localDay(timezone='America/New_York', date=new Date()) { return new Intl.DateTimeFormat('en-CA',{timeZone:timezone,year:'numeric',month:'2-digit',day:'2-digit'}).format(date); }
export function latestFor(packets,language,topic) { return packets.filter(p=>p.language===language&&(!topic||topic==='All topics'||p.topic===topic)).sort((a,b)=>b.date.localeCompare(a.date)||b.created_at.localeCompare(a.created_at))[0]||null; }
export function readStorage(storage,key,fallback) { try { const v=JSON.parse(storage.getItem(key)); return v && typeof v==='object' && !Array.isArray(v) ? v : fallback; } catch { return fallback; } }
export function scheduleReview(previous,remembered,now=Date.now()) { const interval=remembered?Math.min((previous?.interval||1)*3,30):1; return {reviewed_at:new Date(now).toISOString(),due:new Date(now+interval*86400000).toISOString(),interval,remembered:!!remembered}; }

const record = v => v && typeof v === 'object' && !Array.isArray(v);
export function cleanLearningState(raw={}) {
  const out={language:raw.language==='te'?'te':'en',bookmarks:[],reviews:{},notes:{}};
  if(Array.isArray(raw.bookmarks))out.bookmarks=[...new Set(raw.bookmarks.filter(x=>typeof x==='string'&&x.length<=150))];
  if(record(raw.reviews))for(const [id,r] of Object.entries(raw.reviews))if(record(r)&&Number.isFinite(Date.parse(r.due))&&id!=='__proto__'&&id!=='constructor')out.reviews[id]={due:r.due,reviewed_at:Number.isFinite(Date.parse(r.reviewed_at))?r.reviewed_at:null,interval:Number.isFinite(r.interval)?Math.max(1,Math.min(30,r.interval)):1,remembered:!!r.remembered};
  if(record(raw.notes))for(const [id,n] of Object.entries(raw.notes))if(typeof n==='string'&&n.length<=30000&&id.length<=250&&id!=='__proto__'&&id!=='constructor')out.notes[id]=n;
  return out;
}
export function importLibrary(data,existing,state,knownIds) {
  const backup=data?.task==='knowledge_pill_backup';
  const incoming=backup?data.packets:validateCollection(data);
  if(!Array.isArray(incoming))throw Error('The backup has no edition collection.');
  const packets=incoming.length?mergeEditions(existing,incoming):existing;
  if(!backup)return {packets,state:cleanLearningState(state)};
  const next=data.state;
  if(data.schema_version!==2||!record(next)||!Array.isArray(next.bookmarks)||next.bookmarks.some(x=>typeof x!=='string'||x.length>150))throw Error('Unsupported backup or invalid bookmarks.');
  if(!record(next.reviews||{})||!record(next.notes||{}))throw Error('Invalid notes or reviews.');
  if(Object.keys(next.reviews||{}).length>500||Object.keys(next.notes||{}).length>1000)throw Error('The backup is too large.');
  for(const r of Object.values(next.reviews||{}))if(!record(r)||!Number.isFinite(Date.parse(r.due)))throw Error('Invalid review date.');
  for(const [id,n]of Object.entries(next.notes||{}))if(typeof n!=='string'||n.length>30000||id.length>250)throw Error('Invalid practice note.');
  const allowed=new Set([...knownIds,...packets.flatMap(p=>[p.id+':knowledge',p.id+':news'])]);
  const clean=cleanLearningState(next),current=cleanLearningState(state);
  return {packets,state:{...current,bookmarks:[...new Set([...current.bookmarks,...clean.bookmarks.filter(id=>allowed.has(id))])],reviews:{...current.reviews,...Object.fromEntries(Object.entries(clean.reviews).filter(([id])=>allowed.has(id)))},notes:{...current.notes,...clean.notes}}};
}

export function validateHeadlines(raw) {
  if(raw?.task!=='ai_headlines'||raw.schema_version!==1||!Array.isArray(raw.items)||raw.items.length>12||!Number.isFinite(Date.parse(raw.checked_at))||Date.parse(raw.checked_at)>Date.now()+300000)throw Error('Invalid headline index.');
  const ids=new Set();
  for(const item of raw.items){const age=Date.parse(raw.checked_at)-Date.parse(item.published_at);if(typeof item.id!=='string'||ids.has(item.id)||typeof item.title!=='string'||item.title.length>1000||typeof item.publisher!=='string'||!safeURL(item.url)||!Number.isFinite(age)||age<0||age>14*86400000)throw Error('Invalid headline date or source.');ids.add(item.id);}
  return raw;
}
export async function refreshHeadlines(fetcher=fetch){const r=await fetcher(REMOTE.replace('latest.json','headlines.json'),{cache:'no-store',signal:AbortSignal.timeout(15000)});if(!r.ok)throw Error('Headlines unavailable.');const text=await r.text();if(text.length>60000)throw Error('Headline index too large.');return validateHeadlines(JSON.parse(text));}
