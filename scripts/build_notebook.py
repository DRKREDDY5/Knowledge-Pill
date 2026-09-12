"""Build the self-contained, numbered Colab notebook from the project sources."""
import ast
import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
cells = []
def md(text):
    cells.append({'cell_type':'markdown','metadata':{},'source':textwrap.dedent(text).strip().splitlines(True)})
def code(text):
    text=textwrap.dedent(text).strip()+'\n';ast.parse(text)
    cells.append({'cell_type':'code','metadata':{},'source':text.splitlines(True),'execution_count':None,'outputs':[]})

md('''
# Knowledge Pill: a simple AI topic router
**Week 5 · Rushikeshava · Qwen3-1.7B-Base + LoRA**

An AI learner wants relevant reading without sorting every article manually. Our one model task is:
**English article title + short description → RAG / Agents / Fine-tuning / Other.**
The app matches that topic to a short, sourced foundation lesson in English or Telugu.

This is a classification experiment, following the support-ticket handout. It does not train a news writer.
The app includes three authored foundation lessons and two daily-pill views. The separate Knowledge_Pill_Daily notebook
generates the knowledge and news drafts for import. A GitHub Actions workflow can also generate daily editions after provider setup; the app loads saved editions automatically.

**Start:** Runtime → Change runtime type → T4 GPU (or another available CUDA GPU), then run the numbered steps in order.
All data and helper code are included. You do **not** need to upload a ZIP or supply an API key.
Planning estimate: allow roughly 1–2 hours for setup and a first GPU run, plus time to inspect results and record the submission.
The first user Colab run completed: training took about 8 minutes 41 seconds, with five smoke tests passing.
Setup and download times vary. The run's reported comparison is documented with its limits in the project source.

The 500 authored rows come from **100 scenarios with five formatting variations each**. We split scenarios first:
400 training rows / 100 validation rows, with no shared scenarios. The validation set is small and synthetic.
A separate 16-paper diagnostic set uses our summaries and labels; it is not an independent, expert-reviewed benchmark.
''')
md('''## 1. Check the GPU
Run this cell first. It should print a GPU name. If it says no GPU, stop and change the runtime.
''')
code('''
import sys, os, subprocess, shutil, json, gc
from pathlib import Path
import torch
assert sys.version_info >= (3,11), 'Use a Colab runtime with Python 3.11 or newer.'
assert torch.cuda.is_available(), 'No GPU: Runtime → Change runtime type → T4 GPU, then rerun.'
ROOT=Path('/content/knowledge-pill-simple'); ROOT.mkdir(parents=True,exist_ok=True)
os.chdir(ROOT)
print('GPU:',torch.cuda.get_device_name(0))
print('GPU memory GB:',round(torch.cuda.get_device_properties(0).total_memory/1e9,1))
print('Free disk GB:',round(shutil.disk_usage(ROOT).free/1e9,1))
assert shutil.disk_usage(ROOT).free > 18e9, 'Free at least 18 GB before continuing.'
''')
md('''## 2. Install the training tools
We use the LLaMA Factory training engine from the handout, through its command line in Colab.
The Board interface is not required by this notebook. If your instructor requires a Board screenshot for a custom project,
open `llamafactory-cli webui` on a supported environment and enter the settings in `configs/train.yaml`.

The Factory code and important dependencies are pinned. We preserve Colab's existing PyTorch packages.
If Colab explicitly requests a runtime restart after installation, restart, rerun step 1, then continue at step 3.
''')
constraints=(ROOT/'configs/training-constraints.txt').read_text()
code('''
import importlib.metadata
FACTORY_COMMIT='100e9a42c6c09f8f7849b70d60f3da445fb2024b'
factory=ROOT/'LLaMA-Factory'
if not factory.exists():
    subprocess.run(['git','init',str(factory)],check=True)
    subprocess.run(['git','-C',str(factory),'remote','add','origin','https://github.com/hiyouga/LLaMA-Factory.git'],check=True)
subprocess.run(['git','-C',str(factory),'fetch','--depth','1','origin',FACTORY_COMMIT],check=True)
subprocess.run(['git','-C',str(factory),'checkout','--detach',FACTORY_COMMIT],check=True)
''' + 'constraints='+repr(constraints)+'\n' + '''
for package in ['torch','torchvision','torchaudio']:
    try: constraints += package+'=='+importlib.metadata.version(package)+'\\n'
    except importlib.metadata.PackageNotFoundError: pass
(ROOT/'runtime-constraints.txt').write_text(constraints)
subprocess.run([sys.executable,'-m','pip','install','-q','-c','runtime-constraints.txt',
    '-e',str(factory),'scikit-learn==1.8.0','matplotlib','pandas'],check=True)
print('Installation complete. Continue to step 3, unless Colab requests a restart.')
''')
md('''## 3. Unpack the included project data and code
The following code writes the helper module, 100 labelled scenarios, 16 paper summaries and two configurations.
You can expand the cell to inspect everything. No private data or credentials are included.
''')
assets={p:(ROOT/p).read_text() for p in ['router.py','data/topic_seeds.json','data/source_cases.json','configs/train.yaml','configs/merge.yaml','configs/training-constraints.txt']}
assets_string=json.dumps(assets,ensure_ascii=False,indent=2)
code('ASSETS = json.loads('+repr(assets_string)+')\n'+'''
for relative, content in ASSETS.items():
    target=ROOT/relative; target.parent.mkdir(parents=True,exist_ok=True); target.write_text(content)
(ROOT/'outputs').mkdir(exist_ok=True)
(ROOT/'outputs/environment.txt').write_text(subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True))
(ROOT/'outputs/factory_revision.txt').write_text('100e9a42c6c09f8f7849b70d60f3da445fb2024b')
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
import router
from router import LABELS, BASE_MODEL, TopicRouter, dump, prepare, lexical_baseline
import pandas as pd
from IPython.display import display
train, validation, data_report=prepare(ROOT)
source_cases=json.loads((ROOT/'data/source_cases.json').read_text())
display(pd.DataFrame({'Training':data_report['train_per_class'],'Validation':data_report['validation_per_class']}))
display(pd.DataFrame(train)[['text','label']].head(4))
print('400 training rows; 100 validation rows; 16 separate source cases. Labels:',LABELS)
print('The 100 validation rows represent 20 scenario groups.')
''')
md('''## 4. Check the prompt and record the exact base model
Both base and fine-tuned models choose among the same four single-letter answers, using the same prompt.
This avoids confusing improved formatting with improved classification. The base weights' revision is recorded.
Nothing is silently cut off to fit the context window.

Step 2 installs Factory in editable mode. The code below also registers its source directory
in this already-running notebook so the import works without restarting the runtime.
''')
code('''
import sys, importlib
factory_src=ROOT/'LLaMA-Factory'/'src'
assert (factory_src/'llamafactory'/'__init__.py').is_file(), 'LLaMA Factory source is missing. Rerun step 2.'
if str(factory_src) not in sys.path:
    sys.path.insert(0,str(factory_src))
importlib.invalidate_caches()

from huggingface_hub import HfApi
from transformers import AutoTokenizer
from llamafactory.data import get_template_and_fix_tokenizer
from llamafactory.hparams import DataArguments
import yaml
revision_file=ROOT/'outputs/base_model_revision.txt'
revision=revision_file.read_text().strip() if revision_file.exists() else HfApi().model_info(BASE_MODEL).sha
revision_file.write_text(revision)
tokenizer=AutoTokenizer.from_pretrained(BASE_MODEL,revision=revision,trust_remote_code=False)
template=get_template_and_fix_tokenizer(tokenizer,DataArguments(template='qwen3_nothink'))
sample=train[0]
messages=[{'role':'user','content':router.user_text(sample['text'])},{'role':'assistant','content':'A'}]
factory_prompt,_=template.encode_oneturn(tokenizer,messages,router.SYSTEM)
assert factory_prompt==tokenizer.encode(router.prompt(sample['text']),add_special_tokens=False), 'Training/inference prompt mismatch.'
lengths=[len(tokenizer.encode(router.prompt(r['text']),add_special_tokens=False))+8 for r in train+validation+source_cases]
assert max(lengths)<=512, 'An example is too long; shorten it explicitly before training.'
for name in ['train','merge']:
    path=ROOT/f'configs/{name}.yaml';config=yaml.safe_load(path.read_text());config['model_revision']=revision
    path.write_text(yaml.safe_dump(config,sort_keys=False))
print('Exact prompt match. Longest example with answer reserve:',max(lengths),'tokens.')
print('Base revision:',revision)
''')
md('''## 5. Run a simple baseline
TF-IDF counts useful words and word pairs; logistic regression chooses a topic.
This cheap model is a serious alternative. A strong result is a reason to question whether the product needs Qwen.
Do not remove or weaken this baseline to make fine-tuning look better.
''')
code('''
lexical,browser_model=lexical_baseline(train,validation,source_cases)
dump('outputs/lexical_baseline.json',lexical)
dump('outputs/router_baseline.json',browser_model)
display(pd.DataFrame([
    {'Set':'Authored validation',**{k:lexical['validation'][k] for k in ['n','accuracy','macro_f1']}},
    {'Set':'16 source cases',**{k:lexical['source_cases'][k] for k in ['n','accuracy','macro_f1']}}
]))
''')
md('''## 6. Evaluate Qwen before training
Download/load the base model and measure both sets. These actual predictions will be compared with the merged model.
We use validation for checkpoint selection too, so this is a development comparison, not a final unbiased test.
''')
code('''
base=TopicRouter(revision=revision)
base_validation=base.evaluate(validation);base_sources=base.evaluate(source_cases)
dump('outputs/base_validation.json',base_validation);dump('outputs/base_sources.json',base_sources)
print('Base validation accuracy:',base_validation['metrics']['accuracy'])
print('Base source-case accuracy:',base_sources['metrics']['accuracy'])
del base;gc.collect();torch.cuda.empty_cache()
''')
md('''## 7. Train with LoRA
The base weights stay frozen. We train rank-8 adapters for three epochs with batch size 1 and gradient accumulation 8.
That is about 150 optimizer updates on 400 rows. `eval_loss` selects the best saved epoch.
The dataset is registered in `data/processed/dataset_info.json` in ShareGPT format.

Leave this cell running until it finishes. If it fails, keep the error output and stop; later steps need its adapter.
An out-of-memory error may require restarting the runtime, rerunning steps 1 and 3–4, then this step.
Earlier baseline files survive a runtime restart but not a deleted/disconnected VM.
''')
code('''
command=['llamafactory-cli','train',str(ROOT/'configs/train.yaml')]
with (ROOT/'outputs/training.log').open('w') as log:
    process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
    for line in process.stdout:
        print(line,end='');log.write(line);log.flush()
    if process.wait()!=0: raise RuntimeError('Training failed. Inspect outputs/training.log and the error above.')
assert (ROOT/'outputs/adapter/adapter_config.json').is_file(), 'Training did not save an adapter.'
print('Adapter saved. Continue to the loss curve.')
''')
md('''## 8. Inspect and save the loss curve
A lower training loss is not sufficient evidence of better routing. Look at validation loss and the classification results too.
''')
code('''
import matplotlib.pyplot as plt
history=json.loads((ROOT/'outputs/adapter/trainer_state.json').read_text())['log_history']
training_points=[x for x in history if 'loss' in x];eval_points=[x for x in history if 'eval_loss' in x]
assert training_points and eval_points, 'Missing training or validation loss history.'
fig,ax=plt.subplots(figsize=(7,4))
ax.plot([x['step'] for x in training_points],[x['loss'] for x in training_points],label='Training')
ax.plot([x['step'] for x in eval_points],[x['eval_loss'] for x in eval_points],'o-',label='Validation')
ax.set(xlabel='Optimizer step',ylabel='Loss',title='Knowledge Pill: LoRA training');ax.legend();fig.tight_layout()
fig.savefig('outputs/loss_curve.png',dpi=160);plt.show()
''')
md('''## 9. Merge the adapter and run five smoke tests
Merging combines the learned adapter with the base weights. `classify(text)` then returns one of the four topic labels.
Smoke tests are quick demonstrations; report failures honestly and use the larger comparison for evaluation.
''')
code('''
subprocess.run(['llamafactory-cli','export',str(ROOT/'configs/merge.yaml')],check=True)
merged=TopicRouter(str(ROOT/'models/knowledge-pill-merged'))
def classify(text):
    return merged.classify(text)['label']
smoke=[
    ('An assistant retrieves passages from company documentation and cites them in its answers.','RAG'),
    ('A coding assistant plans a fix, runs terminal tools and revises its patch from test results.','Agents'),
    ('Train low-rank adapters while freezing a pretrained model to specialize it for topic labels.','Fine-tuning'),
    ('A vision model segments objects in photographs.','Other'),
    ('This newsletter covers retrieval, autonomous tools and model adaptation equally.','Other')
]
smoke_results=[{'text':text,'expected':label,'predicted':classify(text)} for text,label in smoke]
dump('outputs/smoke_results.json',smoke_results);display(pd.DataFrame(smoke_results))
print('Passed:',sum(x['expected']==x['predicted'] for x in smoke_results),'/ 5')
''')
md('''## 10. Compare the same examples before and after
Save accuracy, precision, recall, F1, support, confusion matrices and individual errors.
Macro F1 gives each category equal weight. The 16 source cases are a small diagnostic with project-authored labels;
the base model may also have encountered these historical papers during pretraining.
Do not tune on these cases and then call them an untouched test set.
''')
code('''
base_validation=json.loads((ROOT/'outputs/base_validation.json').read_text())
base_sources=json.loads((ROOT/'outputs/base_sources.json').read_text())
lexical=json.loads((ROOT/'outputs/lexical_baseline.json').read_text())
ft_validation=merged.evaluate(validation);ft_sources=merged.evaluate(source_cases)
assert base_validation['dataset_hash']==ft_validation['dataset_hash']
assert base_sources['dataset_hash']==ft_sources['dataset_hash']
dump('outputs/finetuned_validation.json',ft_validation);dump('outputs/finetuned_sources.json',ft_sources)
comparison={'schema_version':2,'task':'topic_router','status':'measured','same_evaluation_set':True,
    'dataset_hash':ft_validation['dataset_hash'],'labels':LABELS,'base_revision':revision,
    'baseline':base_validation['metrics'],'finetuned':ft_validation['metrics'],'lexical':lexical['validation'],
    'source_cases':{'baseline':base_sources['metrics'],'finetuned':ft_sources['metrics'],'lexical':lexical['source_cases']},
    'limitations':'Authored development validation: 20 scenario groups. Source diagnostic: 16 author-labelled paper summaries.'}
dump('outputs/comparison.json',comparison)
for title,result_set in [('Validation',comparison),('Source cases',comparison['source_cases'])]:
    print(title)
    display(pd.DataFrame([{'Model':key,**{m:result_set[key][m] for m in ['n','accuracy','macro_f1']}}
        for key in ['lexical','baseline','finetuned']]))
display(pd.DataFrame(ft_validation['metrics']['classification_report']).T)
fig,axes=plt.subplots(1,2,figsize=(10,4))
for ax,(name,result) in zip(axes,[('Qwen base',base_validation),('Qwen + LoRA',ft_validation)]):
    matrix=result['metrics']['confusion_matrix'];ax.imshow(matrix,cmap='Blues')
    ax.set(xticks=range(4),yticks=range(4),xticklabels=LABELS,yticklabels=LABELS,title=name,xlabel='Predicted',ylabel='Actual')
    ax.tick_params(axis='x',rotation=25)
    for i in range(4):
        for j in range(4):ax.text(j,i,str(matrix[i][j]),ha='center',va='center',color='white' if matrix[i][j]>12 else 'black')
fig.tight_layout();fig.savefig('outputs/confusion_matrices.png',dpi=160);plt.show()
errors=[{'set':name,**p} for name,result in [('validation',ft_validation),('source_cases',ft_sources)]
        for p in result['predictions'] if p['expected']!=p['label']]
dump('outputs/errors.json',errors);display(pd.DataFrame(errors))
print('Import outputs/comparison.json in the app Experiment page. Imported reports are user-supplied, not independently verified.')
''')
md('''## 11. Use your model to route reading material
This step tries the Hugging Face editorial RSS feed for articles published in the last 30 days.
It routes feed descriptions, not full papers. If the feed is empty or unreachable it explicitly uses our historical paper examples.
The app can import `routed_articles.json`, filter by interest, and open the matching foundation lesson.
The foundation lesson explains the topic; it is not a generated summary of the imported article.
''')
code('''
from datetime import datetime,timezone
try:
    candidates=router.fetch_recent(12)
except Exception as error:
    print('Recent feed unavailable:',str(error));candidates=[]
source_mode='recent_editorial_feed' if candidates else 'historical_paper_examples'
if not candidates:
    print('Using historical examples, not current news.')
    candidates=[{k:r[k] for k in ['id','text','title','source_url']} for r in source_cases]
articles=[];skipped=[]
for item in candidates:
    try: articles.append({**item,'label':classify(item['text'])})
    except ValueError as error: skipped.append({'id':item['id'],'reason':str(error)})
assert articles, 'No descriptions fit the router. Shorten candidate descriptions explicitly and retry.'
packet={'schema_version':2,'task':'topic_router','engine':'Qwen3-1.7B + LoRA (merged)',
    'source_mode':source_mode,'created_at':datetime.now(timezone.utc).isoformat(),'articles':articles,'skipped':skipped}
dump('outputs/routed_articles.json',packet);display(pd.DataFrame(articles)[['title','label','source_url']])
if skipped: print('Skipped descriptions:',skipped)
''')
md('''## 12. Download the evidence and prepare your submission
Download `Knowledge_Pill_Results.zip`, then separately save the **executed notebook** using File → Download → Download .ipynb.
Also keep the small trained adapter; do not push multi-gigabyte model weights to an ordinary GitHub repository.
The merged model remains under `models/knowledge-pill-merged` while this Colab VM exists and can be reproduced from the adapter.

For the custom-project track, put the project source, data, configurations, executed notebook and measured results in your GitHub repository.
Record a short Loom: problem → four-label decision → why LoRA is an experiment → real comparison → wrong example → working app import.
The app's optional source ZIP is for submission, not a prerequisite to run this notebook.

Write your conclusion from the actual numbers: did LoRA beat the base, and did either beat the simple classifier?
If gains are absent, say so. A reasonable product decision may be to retain the cheap baseline.
Don't claim broad multilingual classification: input is English; the three lesson translations are authored Telugu drafts.

Handout: [official project](https://github.com/The-Gen-Academy/5A-Fine-Tune-a-Support-Ticket-Router).
Custom submission: GitHub + Loom via [the form](https://forms.gle/7Hpa2Pkd8ZaWUomm6).
Deadline in the supplied handout: **September 13, 2026, 11:59 PM Pacific**.
''')
code('''
import zipfile
with zipfile.ZipFile(ROOT/'Knowledge_Pill_Results.zip','w',zipfile.ZIP_DEFLATED) as z:
    for directory in ['outputs','configs','data']:
        for path in (ROOT/directory).rglob('*'):
            if not path.is_file(): continue
            if 'adapter' in path.relative_to(ROOT).parts: continue
            z.write(path,path.relative_to(ROOT))
    z.write(ROOT/'router.py','router.py')
with zipfile.ZipFile(ROOT/'Knowledge_Pill_Adapter.zip','w',zipfile.ZIP_DEFLATED) as z:
    for name in ['adapter_config.json','adapter_model.safetensors','README.md']:
        path=ROOT/'outputs/adapter'/name
        if path.exists():z.write(path,name)
    z.write(ROOT/'outputs/base_model_revision.txt','base_model_revision.txt')
from google.colab import files
files.download(str(ROOT/'Knowledge_Pill_Results.zip'))
print('Results ready. Also save the executed notebook and download the adapter in the next cell.')
''')
code("files.download(str(ROOT/'Knowledge_Pill_Adapter.zip'))")

notebook={'nbformat':4,'nbformat_minor':5,'metadata':{'accelerator':'GPU','kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}},'cells':cells}
for i,cell in enumerate(cells):cell['id']=f'knowledge-pill-{i:02d}'
path=ROOT/'notebooks/Knowledge_Pill_Simple.ipynb';path.parent.mkdir(exist_ok=True)
path.write_text(json.dumps(notebook,ensure_ascii=False,indent=1)+'\n')
print('Built:',path.name,'with',sum(c['cell_type']=='code' for c in cells),'code cells.')
