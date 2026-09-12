"""Import a trusted user export after validating paths, data hashes and metrics."""
import csv
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from router import build_dataset, split_dataset, metrics

def main(archive):
    archive=Path(archive)
    destination=ROOT/'results/run_2026-09-12'
    with ZipFile(archive) as z:
        assert sum(i.file_size for i in z.infolist())<20_000_000, 'Unexpected export size'
        for i in z.infolist():
            p=PurePosixPath(i.filename)
            assert not p.is_absolute() and '..' not in p.parts and '\\' not in i.filename
            assert (i.external_attr>>16)&0o170000!=0o120000, 'Symlinks are not accepted'
        read=lambda name:json.loads(z.read(name))
        train=read('data/processed/train.json');validation=read('data/processed/validation.json')
        cases=read('data/source_cases.json')
        assert (train,validation)==split_dataset(build_dataset(read('data/topic_seeds.json')))
        for name,rows in [('base_validation',validation),('finetuned_validation',validation),('base_sources',cases),('finetuned_sources',cases)]:
            result=read('outputs/'+name+'.json')
            assert result['dataset_hash']==hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()
            assert len(result['predictions'])==len(rows)
            assert all(a['id']==b['id'] and a['expected']==b['label'] for a,b in zip(result['predictions'],rows))
            assert result['metrics']==metrics(rows,[p['label'] for p in result['predictions']])
        manifest={}
        for i in z.infolist():
            if i.is_dir():continue
            # Flatten outputs into the evidence directory; retain all other paths as a snapshot.
            relative=i.filename.removeprefix('outputs/') if i.filename.startswith('outputs/') else 'snapshot/'+i.filename
            path=destination/relative;path.parent.mkdir(parents=True,exist_ok=True)
            content=z.read(i);path.write_bytes(content)
            manifest[i.filename]={'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(content).hexdigest()}
        manifest={'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':manifest,
                  'verification':'Prediction metrics, dataset hashes, row IDs, labels and grouped splits recomputed successfully.'}
        (destination/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    with (ROOT/'data/knowledge_pill.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['id','group_id','text','label','split','provenance'])
        writer.writeheader()
        for split,rows in [('train',train),('validation',validation)]:
            for row in rows:writer.writerow({**{k:row[k] for k in ['id','group_id','text','label','provenance']},'split':split})
    print('Verified and imported 28 evidence files; exported 500 CSV rows with original split labels.')

if __name__=='__main__':main(sys.argv[1])
