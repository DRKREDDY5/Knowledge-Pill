import json
import subprocess
import sys
import unittest
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import daily_pills as daily

class DailyChecks(unittest.TestCase):
 def test_source_dates_and_host_boundaries(self):
  now=datetime(2026,9,12,14,tzinfo=timezone.utc)
  rows=[('past','Fri, 11 Sep 2026 10:00:00 GMT','https://openai.com/news/past'),
        ('future','Mon, 14 Sep 2026 10:00:00 GMT','https://openai.com/news/future'),
        ('wrong-host','Sat, 12 Sep 2026 10:00:00 GMT','https://example.com/fake')]
  raw='<rss><channel>'+''.join(f'<item><title>{t}</title><link>{u}</link><pubDate>{d}</pubDate><description>Example description for source-date validation.</description></item>' for t,d,u in rows)+'</channel></rss>'
  parsed=daily.parse_feed(raw,'OpenAI','openai.com',now)
  self.assertEqual([r['title'] for r in parsed],['past'])
  selected,window=daily.choose_news(parsed,'RAG','2026-09-12','America/New_York',now=now)
  self.assertEqual(window,'recent');self.assertEqual(len(selected),1)
  selected,window=daily.choose_news(parsed,'RAG','2026-09-11','America/New_York',now=now)
  self.assertEqual(window,'today')

 def test_packet_validation_in_python_and_browser(self):
  sources=[{'id':'paper-1','title':'Fixture paper','url':'https://arxiv.org/abs/2005.11401','publisher':'arXiv','published_at':None,'evidence_type':'paper_abstract'},
    {'id':'news-1','title':'Fixture update','url':'https://openai.com/news/fixture','publisher':'OpenAI','published_at':'2026-09-12T12:00:00+00:00','evidence_type':'article_excerpt'}]
  pack={'language':'en','knowledge_sources':[sources[0]],'news_sources':[sources[1]]}
  draft={'knowledge':{**{k:'Test fixture only. '+('word '*35) for k in daily.KNOWLEDGE_FIELDS},'source_ids':['paper-1']},
    'news':{'title':'Fixture','overview':'Example '*80,'items':[{**{k:'Example '*45 for k in daily.NEWS_FIELDS},'source_ids':['news-1']}], 'exercise':'Example exercise','question':'Example question','answer':'Example answer'}}
  daily.validate_draft(draft,pack)
  packet={**draft,'schema_version':1,'task':'daily_pills','status':'draft','id':'fixture','topic':'RAG','language':'en','concept':'Example concept','writer_model':'test-fixture','router_engine':'test-fixture','date':'2026-09-12','timezone':'America/New_York','created_at':'2026-09-12T14:00:00+00:00','news_window':'today','sources':sources}
  js="""
import assert from 'node:assert/strict';import fs from 'node:fs';
import {validateDaily} from './dist/daily-view.mjs';
const p=JSON.parse(fs.readFileSync(0,'utf8'));assert.equal(validateDaily(p),p);
const changed=structuredClone(p);changed.news.items[0].source_ids=['invented'];assert.throws(()=>validateDaily(changed));
const future=structuredClone(p);future.sources[1].published_at='2026-09-14T12:00:00Z';assert.throws(()=>validateDaily(future));
const old=structuredClone(p);old.sources[1].published_at='2026-09-11T12:00:00Z';assert.throws(()=>validateDaily(old));
old.news_window='recent';assert.equal(validateDaily(old),old);
const bad=structuredClone(p);bad.sources[0].url='javascript:alert(1)';assert.throws(()=>validateDaily(bad));
"""
  r=subprocess.run(['node','--input-type=module','-e',js],input=json.dumps(packet),text=True,capture_output=True,cwd=ROOT)
  self.assertEqual(r.returncode,0,r.stderr)
  draft['news']['items'][0]['source_ids']=['invented']
  with self.assertRaises(ValueError):daily.validate_draft(draft,pack)

 def test_missing_provider_configuration_stops_before_request(self):
  with self.assertRaises(ValueError):daily.generate({},'', 'accounts/example/models/example')
  with self.assertRaises(ValueError):daily.generate({},'test-fixture-not-a-key','')

if __name__=='__main__':unittest.main()
