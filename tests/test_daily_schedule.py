import json
import os
import sys
import tempfile
import unittest
from datetime import datetime,timezone
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import run_daily

class ScheduleChecks(unittest.TestCase):
    def setup_root(self,root):
        (root/'configs').mkdir();(root/'dist').mkdir();(root/'editions').mkdir()
        (root/'configs/daily.json').write_text(json.dumps({'topics':['RAG'],'languages':['en','te'],'timezone':'America/New_York','retained_editions':30}))
        (root/'dist/router_baseline.json').write_text('{}')
        day=datetime.now(timezone.utc).astimezone(ZoneInfo('America/New_York')).date().isoformat()
        packets=[{'id':l,'date':day,'topic':'RAG','language':l,'concept':'Example','generation_method':'fireworks'} for l in ['en','te']]
        path=root/'editions/latest.json';path.write_text(json.dumps({'task':'daily_pills_collection','packets':packets}))
        return path

    def test_same_day_reuses_existing_editions_without_provider(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.setup_root(root)
            with patch.object(run_daily,'collect_news',return_value=([],[])),patch.object(run_daily,'generate') as generate,patch.dict(os.environ,{},clear=True):
                self.assertEqual(run_daily.run(root)['generated'],0)
                generate.assert_not_called()

    def test_missing_key_preserves_last_successful_collection(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);path=self.setup_root(root);before=path.read_bytes()
            with patch.dict(os.environ,{},clear=True),self.assertRaises(ValueError):run_daily.run(root,force=True)
            self.assertEqual(path.read_bytes(),before)

    def test_partial_language_failure_never_replaces_collection(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);path=self.setup_root(root);before=path.read_bytes()
            pack={'knowledge_sources':[{},{}],'news_sources':[],'news_window':'none','language':'en'}
            with patch.dict(os.environ,{'FIREWORKS_API_KEY':'test-only','FIREWORKS_MODEL':'accounts/test/models/mock'}),patch.object(run_daily,'make_pack',return_value=pack),patch.object(run_daily,'generate',side_effect=[{'id':'draft-en'},ValueError('Invalid Telugu draft')]):
                with self.assertRaises(ValueError):run_daily.run(root,force=True)
            self.assertEqual(path.read_bytes(),before)

    def test_full_generation_validates_and_replaces_once(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);path=self.setup_root(root)
            old=json.loads(path.read_text())['packets']
            pack={'knowledge_sources':[{},{}],'news_sources':[],'news_window':'none','language':'en'}
            with patch.dict(os.environ,{'FIREWORKS_API_KEY':'test-only','FIREWORKS_MODEL':'accounts/test/models/mock'}),patch.object(run_daily,'make_pack',return_value=pack),patch.object(run_daily,'generate',side_effect=old),patch('subprocess.run') as check:
                self.assertEqual(run_daily.run(root,force=True)['generated'],2)
                check.assert_called_once()
            self.assertEqual(len(json.loads(path.read_text())['packets']),2)

if __name__=='__main__':unittest.main()
