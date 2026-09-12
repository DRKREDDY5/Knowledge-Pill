import json
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from io import BytesIO,StringIO
from unittest.mock import patch
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

 def writer_fixture(self):
  packet=json.loads((ROOT/'examples/2026-09-12-rag-en.json').read_text())
  knowledge_ids=set(packet['knowledge']['source_ids'])
  pack={**packet,'knowledge_sources':[s for s in packet['sources'] if s['id'] in knowledge_ids],
    'news_sources':[s for s in packet['sources'] if s['id'] not in knowledge_ids]}
  return pack,{k:packet[k] for k in ['knowledge','news']}

 def test_writer_complete_structured_response_and_safe_logs(self):
  pack,draft=self.writer_fixture();log=StringIO()
  result={'choices':[{'finish_reason':'stop','message':{'content':json.dumps(draft),'reasoning_content':'PRIVATE_REASONING'}}],
    'usage':{'completion_tokens':3500,'prompt_tokens':2000,'total_tokens':5500,'unexpected':'PRIVATE_METADATA'}}
  with patch.object(daily.urllib.request,'urlopen',return_value=BytesIO(json.dumps(result).encode())) as request,redirect_stdout(log):
   packet=daily.generate(pack,'PRIVATE_TEST_KEY','accounts/fireworks/models/glm-5p3-flash')
  payload=json.loads(request.call_args.args[0].data)
  self.assertEqual(packet['generation_method'],'fireworks')
  self.assertEqual(packet['knowledge'],draft['knowledge'])
  self.assertGreaterEqual(payload['max_tokens'],16000)
  self.assertEqual(payload['response_format']['type'],'json_schema')
  schema=payload['response_format']['json_schema']['schema']
  self.assertEqual(schema['properties']['news']['properties']['items']['maxItems'],len(pack['news_sources']))
  self.assertIn('3500',log.getvalue())
  self.assertNotIn('PRIVATE_',log.getvalue())

 def test_truncated_writer_response_is_rejected_without_retry(self):
  pack,_=self.writer_fixture();log=StringIO()
  result={'choices':[{'finish_reason':'length','message':{'content':'{"knowledge":','reasoning_content':'PRIVATE_REASONING'}}],
    'usage':{'completion_tokens':16000}}
  with patch.object(daily.urllib.request,'urlopen',return_value=BytesIO(json.dumps(result).encode())) as request,redirect_stdout(log):
   with self.assertRaisesRegex(ValueError,'cut off for en.*no draft was accepted'):
    daily.generate(pack,'PRIVATE_TEST_KEY','accounts/fireworks/models/glm-5p3-flash')
  self.assertEqual(request.call_count,1)
  self.assertNotIn('PRIVATE_',log.getvalue())

 def test_no_news_schema_requires_empty_items(self):
  items=daily.draft_schema({'news_sources':[]})['properties']['news']['properties']['items']
  self.assertEqual((items['minItems'],items['maxItems']),(0,0))

if __name__=='__main__':unittest.main()
