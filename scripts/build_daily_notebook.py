"""Build a small CPU-only source-to-pill notebook for the daily product flow."""
import ast,json,textwrap
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];cells=[]
def md(s):cells.append({'cell_type':'markdown','metadata':{},'source':textwrap.dedent(s).strip().splitlines(True)})
def code(s):
 s=textwrap.dedent(s).strip()+'\n';ast.parse(s)
 cells.append({'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':s.splitlines(True)})
md('''# Knowledge Pill: generate your two daily pills

The Week 5 training notebook is complete. This separate notebook creates the product's **knowledge pill** and **AI news pill**, aiming for **5–10 minutes each including the activity**. It needs no GPU and does not retrain Qwen.

The measured simple classifier routes source descriptions here; the completed Qwen + LoRA experiment remains in the training notebook. An existing Fireworks model writes the lessons from supplied sources.

This notebook offers manual generation. The repository also includes a GitHub Actions schedule, activated after Fireworks setup. The hosted app loads saved repository editions or imports this JSON. API calls spend your Fireworks credits. The first real provider run still needs verification; dated demonstration editions are explicitly labelled.

Before switching notebooks, save your training results ZIP, adapter ZIP and executed training notebook. Keep them together for the GitHub + Loom submission.
''')
md('''## 1. Prepare the included generator
Run this in a standard Python 3 runtime. All helper code and baseline weights are included.
''')
assets={p:(ROOT/p).read_text() for p in ['daily_pills.py','data/source_cases.json','dist/router_baseline.json']}
code('''
import sys,os,json,subprocess
from pathlib import Path
subprocess.run([sys.executable,'-m','pip','install','-q','beautifulsoup4>=4.12,<5'],check=True)
ROOT=Path('/content/knowledge-pill-daily');ROOT.mkdir(exist_ok=True);os.chdir(ROOT)
'''+ 'ASSETS=json.loads('+repr(json.dumps(assets,ensure_ascii=False))+')\n'+'''
for relative,content in ASSETS.items():
 path=ROOT/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content)
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from daily_pills import make_pack,generate,route_baseline
from IPython.display import display,Markdown
print('Ready. No GPU required.')
''')
md('''## 2. Choose your interest, language and Fireworks model
Start with English, review the result, then repeat with Telugu.
Copy an inference-ready **model or deployment path** from your Fireworks account into MODEL. Model availability changes; this notebook does not create a paid GPU deployment or guess which models your cohort account enables.

In Colab's left sidebar, open the **key icon / Secrets**. Add `FIREWORKS_API_KEY`, paste your Fireworks API key into its value and enable notebook access. Do not put the key in a code cell or chat.
''')
code('''
TOPIC='RAG'  # RAG / Agents / Fine-tuning
LANGUAGE='en'  # en / te
TIMEZONE='America/New_York'
MODEL=''  # Copy your available Fireworks model/deployment path here.
RECENT_CONCEPTS=[]  # Optional: concept names from previously completed pills.
assert TOPIC in ['RAG','Agents','Fine-tuning'] and LANGUAGE in ['en','te']
print('Selected:',TOPIC,LANGUAGE,TIMEZONE)
''')
md('''## 3. Collect and inspect sources — no writer charge yet
The generator reads official feeds from Hugging Face, OpenAI, Google DeepMind and Google Research. It excludes future-dated entries and prefers items published today in your timezone. If none exist, it labels a roundup from the last seven days as **recent**, with actual dates. Collection is bounded, not exhaustive research.

It fetches two paper abstracts for the knowledge lesson, and article text where available for news. If only a feed excerpt is available, that limitation remains visible. Check the sources before the next step.
''')
code('''
browser_model=json.loads((ROOT/'dist/router_baseline.json').read_text())
pack=make_pack(TOPIC,LANGUAGE,TIMEZONE,RECENT_CONCEPTS,
    classify=lambda text:route_baseline(text,browser_model),router_engine=browser_model['engine'],root=ROOT)
(ROOT/'source_pack.json').write_text(json.dumps(pack,ensure_ascii=False,indent=2))
print('Local date:',pack['date'],'Concept:',pack['concept'],'News window:',pack['news_window'])
for source in pack['knowledge_sources']+pack['news_sources']:
 print(source['title'],'|',source['published_at'] or 'Foundation paper','|',source['evidence_type'])
 print(source['url'])
if pack['source_warnings']:print('Sources unavailable:',pack['source_warnings'])
''')
md('''## 4. Generate both drafts
This cell makes **one paid Fireworks API request** using your configured account. There is no automatic retry. It checks output structure, cited source IDs, length and basic Telugu-script presence. Those checks do not prove factual accuracy or fluent translation.

If a model is unavailable, choose an inference-ready model in your account; do not create a dedicated deployment just to bypass the error. If a response fails validation, inspect the error before spending another request.
''')
code('''
from google.colab import userdata
assert MODEL.startswith('accounts/'), 'Set MODEL in step 2 to your available Fireworks model/deployment path, then rerun step 2.'
api_key=userdata.get('FIREWORKS_API_KEY')
try:
 packet=generate(pack,api_key,MODEL)
finally:
 api_key=None
(ROOT/'daily_pills.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2))
print('Both drafts generated. Usage:',packet['usage'])
print('Knowledge:',packet['knowledge']['title'])
print('News:',packet['news']['title'],'|',packet['news_window'])
for name in ['story','connection','explanation','limits']:
 display(Markdown('**'+name+'**'))
 print(packet['knowledge'][name])
for item in packet['news']['items']:
 display(Markdown('**'+item['headline']+'**'))
 print(item['what_happened']);print(item['why_it_matters'])
''')
md('''## 5. Download, import and review
Download the JSON, then open [Knowledge Pill](https://knowledge-pill.drkreddy.chatgpt.site) → **Daily pills** → **Import today's pills**.
Read the knowledge story, check the factual explanation against its sources, check dates in the news roundup, and answer one recall question. Mark reviewed only after checking content. For Telugu, have a fluent reader check the translation.

The app saves imported content and progress only on that device. Export your library periodically; browser storage can be cleared. A JSON packet is an import format, not a verified seal of accuracy.

Retain the source pack and generated JSON for submission evidence. For a learning-quality claim, ask a few intended users to explain the concept later; the classification benchmark alone does not show improved memory.
''')
code('''
from google.colab import files
files.download(str(ROOT/'daily_pills.json'))
print('Import daily_pills.json in the app. Run again with LANGUAGE=te after reviewing English.')
''')
for i,c in enumerate(cells):c['id']=f'daily-pill-{i:02d}'
notebook={'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}},'cells':cells}
p=ROOT/'notebooks/Knowledge_Pill_Daily.ipynb';p.write_text(json.dumps(notebook,ensure_ascii=False,indent=1)+'\n')
print('Created daily generation notebook:',sum(c['cell_type']=='code' for c in cells),'code cells.')
