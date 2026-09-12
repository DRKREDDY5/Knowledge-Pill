const KEY='knowledge-pill-daily-v1';
const escape=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const TOPICS=['RAG','Agents','Fine-tuning'];
const REMOTE='https://raw.githubusercontent.com/DRKREDDY5/Knowledge-Pill/main/editions/latest.json';
const text=(x,max=12000)=>typeof x==='string'&&x.trim()&&x.length<=max;
const dayIn=(date,zone)=>new Intl.DateTimeFormat('en-CA',{timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit'}).format(date);
export function validateDaily(p){
 if(p?.schema_version!==1||p.task!=='daily_pills'||p.status!=='draft'||!TOPICS.includes(p.topic)||!['en','te'].includes(p.language))throw Error('Import daily_pills.json from the daily generation notebook.');
 if(!text(p.id,100)||!text(p.concept,250)||!text(p.writer_model,300)||!text(p.router_engine,150)||!/^\d{4}-\d{2}-\d{2}$/.test(p.date)||!text(p.timezone,100))throw Error('Missing edition details.');
 const created=new Date(p.created_at);
 if(!Number.isFinite(created.getTime())||created.getTime()>Date.now()+300000||dayIn(created,p.timezone)!==p.date)throw Error('The edition date and timezone do not match, or the edition is future-dated.');
 if(!['today','recent','none'].includes(p.news_window)||!Array.isArray(p.sources)||p.sources.length<2||p.sources.length>8)throw Error('Invalid sources or news window.');
 const sources=new Map();
 for(const s of p.sources){
  if(!text(s.id,100)||sources.has(s.id)||!text(s.title,1000)||!text(s.publisher,150)||!text(s.url,2000))throw Error('Invalid or duplicate source.');
  let u;try{u=new URL(s.url);}catch{throw Error('Invalid source URL.');}
  if(u.protocol!=='https:'||u.username||u.password)throw Error('Source links must use HTTPS.');
  if(!['paper_abstract','article_excerpt','feed_excerpt'].includes(s.evidence_type))throw Error('Unknown source type.');
  if(s.published_at!==null&&!Number.isFinite(Date.parse(s.published_at)))throw Error('Invalid publication date.');
  sources.set(s.id,s);
 }
 const fields=(v,keys)=>{if(!v||keys.some(k=>!text(v[k])))throw Error('A pill is missing its explanation or activity.');};
 const refs=(ids,kind)=>{
  if(!Array.isArray(ids)||!ids.length||new Set(ids).size!==ids.length)throw Error('Missing or duplicate citations.');
  for(const id of ids){const s=sources.get(id);if(!s)throw Error('A citation does not match the sources.');
   if(kind==='knowledge'&&s.evidence_type!=='paper_abstract')throw Error('Knowledge citations must reference the supplied foundation papers.');
   if(kind==='news'){
    if(s.evidence_type==='paper_abstract')throw Error('News needs a dated news source.');
    const dt=new Date(s.published_at);const age=created-dt;
    if(s.published_at===null||age<0||age>7*86400000)throw Error('News is future-dated or outside the seven-day edition window.');
    if(p.news_window==='today'&&dayIn(dt,p.timezone)!==p.date)throw Error('Older news cannot be labelled as published today.');
   }
  }
 };
 fields(p.knowledge,['title','summary','story','connection','explanation','application','exercise','question','answer','limits']);refs(p.knowledge.source_ids,'knowledge');
 fields(p.news,['title','overview','exercise','question','answer']);
 if(!Array.isArray(p.news.items)||p.news.items.length>3||(p.news_window==='none')!==(p.news.items.length===0))throw Error('News items and availability do not match.');
 for(const item of p.news.items){fields(item,['headline','what_happened','why_it_matters','takeaway']);refs(item.source_ids,'news');}
 return p;
}
let library=[],progress={};
try{const saved=JSON.parse(localStorage.getItem(KEY)||'{}');library=(saved.packets||[]).map(validateDaily).slice(-30);progress=saved.progress&&typeof saved.progress==='object'?saved.progress:{};}catch{}
let active='knowledge',selectedId=null;
let syncState='idle',syncMessage='';
function persist(){localStorage.setItem(KEY,JSON.stringify({packets:library,progress}));}
export function validateCollection(raw){
 const list=raw?.task==='daily_pills_collection'?raw.packets:[raw];
 if(!Array.isArray(list)||!list.length||list.length>30)throw Error('Expected 1–30 saved editions.');
 const checked=list.map(validateDaily);
 if(new Set(checked.map(p=>p.id)).size!==checked.length)throw Error('Duplicate edition IDs.');
 return checked;
}
function savePackets(checked){
 const before=library,oldProgress=structuredClone(progress);
 for(const p of checked){
  const old=library.find(x=>x.id===p.id);
  if(old&&(old.date!==p.date||old.topic!==p.topic||old.language!==p.language))throw Error('Edition ID conflict.');
  if(old&&JSON.stringify(old)!==JSON.stringify(p)){
   delete progress[p.id];delete progress[p.id+':knowledge'];delete progress[p.id+':news'];
  }
 }
 library=[...library.filter(x=>!checked.some(p=>p.id===x.id)),...checked].sort((a,b)=>a.date.localeCompare(b.date)).slice(-30);
 try{persist();}catch{library=before;progress=oldProgress;throw Error('Device storage is full. Export saved pills before adding more.');}
}
async function syncEditions(rerender){
 if(syncState==='loading')return;
 syncState='loading';syncMessage='Checking for the latest saved editions…';rerender();
 try{
  let data;
  try{
   const response=await fetch(REMOTE,{cache:'no-store',signal:AbortSignal.timeout(12000)});
   if(!response.ok)throw Error('Remote collection is not available.');
   const body=await response.text();if(body.length>2000000)throw Error('Collection is too large.');
   data=JSON.parse(body);validateCollection(data);
  }catch{
   const response=await fetch('sample_editions.json',{signal:AbortSignal.timeout(5000)});
   if(!response.ok)throw Error('Could not load editions. Your saved pills are still available.');
   data=await response.json();
  }
  const checked=validateCollection(data);savePackets(checked);
  syncMessage=checked.every(p=>p.generation_method==='authored_demo')?'Loaded the dated demonstration editions.':'Loaded the latest saved editions. Each pill shows its original date.';
  syncState='done';
 }catch(error){syncState='error';syncMessage=error.message;}
 rerender();
}
function selected(topic,language){const match=library.filter(p=>p.topic===topic&&p.language===language).sort((a,b)=>b.date.localeCompare(a.date));return match.find(p=>p.id===selectedId)||match[0];}
const paragraphs=x=>String(x).split(/\n+/).filter(Boolean).map(p=>`<p>${escape(p)}</p>`).join('');
function sourceList(p,ids){return ids.map(id=>{const s=p.sources.find(s=>s.id===id);return `<div class="source-item"><a href="${escape(s.url)}" target="_blank" rel="noopener noreferrer">${escape(s.title)}</a><p class="notice">${escape(s.publisher)} · ${s.published_at?escape(new Date(s.published_at).toLocaleString('en',{timeZone:p.timezone})):'Foundation paper'} · ${escape(s.evidence_type.replaceAll('_',' '))}</p></div>`;}).join('');}
function recall(p,kind){const c=p[kind],key=p.id+':'+kind,r=progress[key];return `<section class="recall"><div class="number-label">RECALL / గుర్తు చేసుకోండి</div><h3>${escape(c.question)}</h3><textarea aria-label="Your recall answer" placeholder="Explain it in your own words. Your answer stays on this page."></textarea><details><summary>Reveal the key idea / సమాధానం చూడండి</summary>${paragraphs(c.answer)}<div class="actions"><button data-recall="remembered">I remembered it</button><button data-recall="again">Review tomorrow</button></div></details>${r?`<p class="notice">Next review: ${escape(new Date(r.due).toLocaleDateString())}. Your self-assessment.</p>`:''}</section>`;}
function pill(p){const te=p.language==='te',k=p.knowledge,n=p.news,c=active==='knowledge'?k:n;
 let content=active==='knowledge'?`<section><div class="number-label">01 / ${te?'ఒక చిన్న కథ':'A FAMILIAR STORY'}</div><span class="badge">${te?'ఊహించిన ఉదాహరణ':'Fictional example'}</span>${paragraphs(k.story)}</section><section><div class="number-label">02 / ${te?'కథకు భావనకు సంబంధం':'CONNECT THE IDEA'}</div>${paragraphs(k.connection)}${paragraphs(k.explanation)}<div class="analogy">${paragraphs(k.limits)}</div></section><section><div class="number-label">03 / ${te?'ఆచరణలో ఉపయోగం':'MAKE IT USEFUL'}</div>${paragraphs(k.application)}</section>`:
 `${paragraphs(n.overview)}${n.items.map((item,i)=>`<section class="panel"><div class="number-label">${i+1} / ${te?'ఏం జరిగింది?':'WHAT HAPPENED'}</div><h3>${escape(item.headline)}</h3>${paragraphs(item.what_happened)}<h3>${te?'ఇది ఎందుకు ముఖ్యం?':'Why it matters'}</h3>${paragraphs(item.why_it_matters)}<div class="analogy">${paragraphs(item.takeaway)}</div>${sourceList(p,item.source_ids)}</section>`).join('')}`;
 return `<article class="lesson" lang="${p.language}"><div class="lesson-top"><div class="badges"><span class="badge dark">${active==='knowledge'?'Knowledge Pill':'AI News Pill'}</span><span class="badge">${active==='news'&&p.news_window==='none'?'No updates available':'5–10 min · reading + activity'}</span><span class="badge">${escape(p.topic)}</span>${p.generation_method==='authored_demo'?'<span class="badge">Dated demonstration · not a Fireworks run</span>':''}</div><h2>${escape(c.title)}</h2>${active==='knowledge'?paragraphs(k.summary):`<p class="notice">${p.news_window==='today'?'Published on this edition’s date':p.news_window==='recent'?'Recent roundup · earlier in the last seven days':'No suitable recent updates found'} · ${escape(p.date)}</p>`}</div><div class="lesson-body">${content}<section class="exercise"><div class="number-label">${te?'రెండు నిమిషాలు ప్రయత్నించండి':'TRY IT / ABOUT TWO MINUTES'}</div>${paragraphs(c.exercise)}</section>${recall(p,active)}</div><details class="sources"><summary>${te?'ఆధారాలు, సమీక్ష':'Sources and review'}</summary>${active==='knowledge'?sourceList(p,k.source_ids):'<p>Source links and dates appear with each news item.</p>'}<p>${p.generation_method==='authored_demo'?'Assistant-authored demonstration.':'AI-generated draft.'} Check the facts, analogy and language before marking it reviewed. Source links alone do not establish correctness.</p><button id="daily-reviewed">${progress[p.id]?.reviewed?'Reviewed on this device':'I reviewed the sources and language'}</button><p class="notice">Writer: ${escape(p.writer_model)}. Topic router: ${escape(p.router_engine)}.</p></details></article>`;
}
export function renderDaily(topic,language){const p=selected(topic,language),matches=library.filter(x=>x.topic===topic&&x.language===language).sort((a,b)=>b.date.localeCompare(a.date));
 return `<div class="heading"><div><p class="eyebrow">TWO SMALL LEARNING SESSIONS</p><h1>Your daily pills</h1><p>One idea to understand. A few developments to keep up with.</p></div></div><div class="daily-tabs"><button data-pill-kind="knowledge" aria-pressed="${active==='knowledge'}"><strong>Learn a concept</strong><span>Story · explanation · practice</span></button><button data-pill-kind="news" aria-pressed="${active==='news'}"><strong>Today in AI</strong><span>Dated updates · why they matter</span></button></div><div class="panel"><label class="file-label">Import today’s pills<input type="file" id="daily-input" accept="application/json,.json"></label><p class="notice">5–10 minutes per pill, including its activity. Imported drafts and review progress are saved on this device.</p>${matches.length?`<label for="daily-edition">Saved edition</label><select id="daily-edition">${matches.map(x=>`<option value="${escape(x.id)}" ${p?.id===x.id?'selected':''}>${escape(x.date)} · ${escape(x.knowledge.title)}</option>`).join('')}</select><button class="small" id="daily-export">Export my saved pills</button>`:''}</div>${p?`${p.date!==dayIn(new Date(),p.timezone)?`<div class="alert">You are reading the saved edition from ${escape(p.date)}. This is not today’s news.</div>`:''}${pill(p)}`:`<div class="empty"><h2>${active==='knowledge'?'Your next idea starts here.':'Bring today’s AI into focus.'}</h2><p>No ${language==='te'?'Telugu':'English'} ${escape(topic)} edition has been imported yet. The generation notebook collects sources and writes both pills using your Fireworks account.</p><div class="actions"><a href="downloads/Knowledge_Pill_Daily.ipynb" download>Download the daily generation notebook</a><button id="daily-foundation">Read a foundation lesson</button></div><p class="notice">New editions load automatically when the repository has them. The daily schedule needs the project owner’s Fireworks setup; manual notebook imports also work.</p></div>`}`;
}
export function bindDaily(topic,language,rerender,toast,openFoundation){
 if(syncState==='idle')queueMicrotask(()=>syncEditions(rerender));
 const panel=document.querySelector('#daily-input')?.closest('.panel');
 if(panel){const status=document.createElement('p');status.className='notice';status.textContent=syncMessage||'Latest editions load automatically from the project repository.';panel.prepend(status);
  const refresh=document.createElement('button');refresh.className='small';refresh.textContent=syncState==='loading'?'Checking…':'Check for new editions';refresh.disabled=syncState==='loading';refresh.onclick=()=>syncEditions(rerender);panel.append(refresh);}
 document.querySelectorAll('[data-pill-kind]').forEach(b=>b.onclick=()=>{active=b.dataset.pillKind;rerender();});
 const input=document.querySelector('#daily-input');
 if(input)input.onchange=async e=>{const file=e.target.files[0];if(!file)return;try{
  if(file.size>2000000)throw Error('Use a JSON export smaller than 2 MB.');
  const checked=validateCollection(JSON.parse(await file.text()));savePackets(checked);
  selectedId=checked[checked.length-1].id;toast('Saved. Select the matching interest and language to read your edition.');rerender();
 }catch(error){toast(error.message);}};
 const edition=document.querySelector('#daily-edition');if(edition)edition.onchange=e=>{selectedId=e.target.value;rerender();};
 const foundation=document.querySelector('#daily-foundation');if(foundation)foundation.onclick=openFoundation;
 const exportButton=document.querySelector('#daily-export');if(exportButton)exportButton.onclick=()=>{
  const blob=new Blob([JSON.stringify({schema_version:1,task:'daily_pills_collection',packets:library},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='Knowledge_Pill_Saved_Editions.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
 };
 const p=selected(topic,language);if(!p)return;
 document.querySelectorAll('[data-recall]').forEach(b=>b.onclick=()=>{progress[p.id+':'+active]={due:new Date(Date.now()+(b.dataset.recall==='again'?1:3)*86400000).toISOString()};try{persist();rerender();}catch{toast('Could not save review progress on this device.');}});
 const reviewed=document.querySelector('#daily-reviewed');if(reviewed)reviewed.onclick=()=>{progress[p.id]={reviewed:new Date().toISOString()};try{persist();rerender();}catch{toast('Could not save review progress.');}};
}
