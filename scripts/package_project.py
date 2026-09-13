"""Validate and package the simple notebook and optional submission source bundle."""
import ast
import json
import shutil
import zipfile
from pathlib import Path

root=Path(__file__).resolve().parents[1]
downloads=root/'dist/downloads';downloads.mkdir(exist_ok=True)
notebook=root/'notebooks/Knowledge_Pill_Simple.ipynb'
for i,cell in enumerate(json.loads(notebook.read_text())['cells']):
    if cell['cell_type']=='code':ast.parse(''.join(cell['source']),filename=f'notebook-cell-{i}')
for directory in ['scripts','tests']:
    for source in (root/directory).glob('*.py'):ast.parse(source.read_text(),filename=str(source))
shutil.copyfile(notebook,downloads/notebook.name)
# Saved URLs continue to deliver the simplified notebook.
shutil.copyfile(notebook,downloads/'Knowledge_Pill_Training.ipynb')
shutil.copyfile(root/'notebooks/Knowledge_Pill_Daily.ipynb',downloads/'Knowledge_Pill_Daily.ipynb')
files=[root/name for name in ['README.md','router.py','daily_pills.py','requirements-data.txt','requirements-daily.txt','.gitignore']]
for directory in ['scripts','tests','configs','notebooks','docs','dist','results','examples','editions','.github']:
    files.extend(p for p in (root/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts and 'downloads' not in p.parts)
files.extend([root/'data/topic_seeds.json',root/'data/source_cases.json',root/'data/knowledge_pill.csv'])
archive=downloads/'Knowledge_Pill_Week5.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for file in sorted(set(files)):z.write(file,file.relative_to(root))
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert 'router.py' in z.namelist() and 'data/topic_seeds.json' in z.namelist()
    assert not any('data/raw' in x or 'knowledge_pill/' in x or 'SCIFACT' in x for x in z.namelist())
for name in ['index.html','app.js','topic-model.mjs','styles.css','lessons.json','router_baseline.json','source_cases.json','daily-view.mjs','sample_editions.json']:
    assert (root/'dist'/name).is_file()
print('Notebook parses. Source ZIP:',len(files),'files,',archive.stat().st_size,'bytes.')
