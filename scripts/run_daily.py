"""Collect once per topic; generate bounded drafts; publish the collection atomically.

GitHub Actions calls this script. No provider call is made in --collect-only mode.
An existing date/topic/language edition is reused unless --force is explicit.
"""
import argparse
import copy
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from daily_pills import TOPICS, make_pack, generate, route_baseline, collect_news, headline_index

def read_collection(path):
    if not path.exists():return []
    data=json.loads(path.read_text())
    if data.get('task')!='daily_pills_collection' or not isinstance(data.get('packets'),list):
        raise ValueError('Existing edition collection is invalid; it was not replaced.')
    return data['packets']

def atomic_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tmp.replace(path)

def run(root=ROOT, collect_only=False, force=False):
    root=Path(root);config=json.loads((root/'configs/daily.json').read_text())
    topics=config['topics'];languages=config['languages'];zone=config['timezone']
    if not topics or not languages or len(topics)!=len(set(topics)) or len(languages)!=len(set(languages)):
        raise ValueError('Choose unique topics and languages in configs/daily.json.')
    if any(t not in TOPICS for t in topics) or any(l not in ['en','te'] for l in languages):raise ValueError('Unsupported topic/language.')
    retained=config.get('retained_editions',30)
    if not isinstance(retained,int) or not 1<=retained<=30:raise ValueError('Retain between 1 and 30 editions.')
    today=datetime.now(timezone.utc).astimezone(ZoneInfo(zone)).date().isoformat()
    target=root/'editions/latest.json';old=read_collection(target)
    pending=[(t,l) for t in topics for l in languages if force or not any(p['date']==today and p['topic']==t and p['language']==l and p.get('generation_method')=='fireworks' for p in old)]
    if not pending and not collect_only:
        rows,warnings=collect_news()
        index=headline_index(rows)
        if index['items']:atomic_json(root/'editions/headlines.json',index)
        print(f"Checked live headlines: {len(index['items'])} available; {len(warnings)} source warnings.")
        print('All configured editions already exist for today. No provider calls.');return {'generated':0,'reused':len(topics)*len(languages)}
    key=os.environ.get('FIREWORKS_API_KEY','');model=os.environ.get('FIREWORKS_MODEL','')
    if not collect_only and (not key or not model.startswith('accounts/')):
        raise ValueError('Set the FIREWORKS_API_KEY repository secret and FIREWORKS_MODEL repository variable before generation. Existing editions were preserved.')
    baseline=json.loads((root/'dist/router_baseline.json').read_text())
    packs={};new=[]
    for topic in topics:
        if not collect_only and not any(t==topic for t,l in pending):continue
        recent=[p['concept'] for p in old if p['topic']==topic and p['date']!=today][-7:]
        pack=make_pack(topic,languages[0],zone,recent,lambda text:route_baseline(text,baseline),'TF-IDF + logistic regression',root)
        packs[topic]=pack
        if pack.get('headline_index',{}).get('items'):atomic_json(root/'editions/headlines.json',pack['headline_index'])
        atomic_json(root/'outputs/daily_sources'/f'{today}-{topic.lower()}.json',pack)
        print(f"{topic}: {len(pack['knowledge_sources'])} knowledge sources, {len(pack['news_sources'])} news sources ({pack['news_window']}).")
    if collect_only:return {'generated':0,'source_topics':len(packs)}
    for topic,language in pending:
        pack=copy.deepcopy(packs[topic]);pack['language']=language
        packet=generate(pack,key,model)
        packet['generation_method']='fireworks'
        new.append(packet)
        # Checkpoints are artifacts only, never the public latest collection on partial failure.
        atomic_json(root/'outputs/daily_checkpoints'/f"{packet['id']}.json",packet)
    keyed={p['id']:p for p in old}
    keyed.update({p['id']:p for p in new})
    packets=sorted(keyed.values(),key=lambda p:(p['date'],p['topic'],p['language']))[-retained:]
    collection={'schema_version':1,'task':'daily_pills_collection','updated_at':datetime.now(timezone.utc).isoformat(),'packets':packets}
    # Use the exact reader validation before making any edition current.
    import subprocess
    validator=root/'dist/daily-view.mjs'
    subprocess.run(['node','--input-type=module','-e',
        "import {validateDaily} from "+json.dumps(validator.as_uri())+";let s='';for await (const c of process.stdin)s+=c;JSON.parse(s).packets.forEach(validateDaily);"],
        input=json.dumps(collection),text=True,check=True,capture_output=True)
    atomic_json(target,collection)
    print(f'Published {len(new)} drafts. Facts and language still require human review.')
    return {'generated':len(new),'retained':len(packets)}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--collect-only',action='store_true')
    parser.add_argument('--force',action='store_true',help='Explicitly allow replacement/provider cost for existing editions.')
    args=parser.parse_args()
    try:run(collect_only=args.collect_only,force=args.force)
    except Exception as error:
        # Provider exceptions are already sanitized; never print credentials or provider bodies.
        print(f'Daily generation stopped: {error}',file=sys.stderr);sys.exit(1)
