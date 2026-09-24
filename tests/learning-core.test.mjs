import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {mergeEditions,refreshEditions,importLibrary,cleanLearningState,scheduleReview,latestFor,validateHeadlines} from '../dist/learning-core.mjs';
const packets=JSON.parse(fs.readFileSync(new URL('../dist/editions.json',import.meta.url))).packets;
const fixture=()=>structuredClone(packets[0]);
test('refresh merges without erasing saved editions and rejects malformed updates',async()=>{
 const p=fixture();p.id='saved-only';const existing=[p];
 const fetcher=async()=>({ok:true,text:async()=>JSON.stringify({task:'daily_pills_collection',packets})});
 const updated=await refreshEditions(existing,fetcher);assert(updated.some(x=>x.id==='saved-only'));assert.equal(existing.length,1);
 await assert.rejects(refreshEditions(existing,async()=>({ok:false})));assert.equal(existing[0].id,'saved-only');
 await assert.rejects(refreshEditions(existing,async()=>({ok:true,text:async()=>'{}'})));
});
test('edition identity conflicts and duplicate packet IDs cannot replace saved work',()=>{
 const p=fixture(),conflict=fixture();conflict.language=p.language==='en'?'te':'en';
 assert.throws(()=>mergeEditions([p],[conflict]));assert.throws(()=>mergeEditions([],[p,p]));assert.equal(p.language,packets[0].language);
});
test('backups validate fully before any state changes',()=>{
 const state={language:'en',bookmarks:[],reviews:{},notes:{}};const original=structuredClone(state);
 const data={task:'knowledge_pill_backup',schema_version:2,packets:[],state:{bookmarks:['decision-models-01'],reviews:{'decision-models-01':{due:'2026-09-25'}},notes:{ok:'note',bad:42}}};
 assert.throws(()=>importLibrary(data,packets,state,['decision-models-01']));assert.deepEqual(state,original);
 data.state.notes={ok:'a saved note'};const imported=importLibrary(data,packets,state,['decision-models-01']);assert.equal(imported.state.notes.ok,'a saved note');assert.equal(imported.state.bookmarks.length,1);assert.deepEqual(state,original);
});
test('corrupt local progress is recovered without breaking rendering',()=>{
 const clean=cleanLearningState({language:'oops',bookmarks:'bad',reviews:{x:{due:'invalid'},y:{due:'2026-10-01',interval:-8}},notes:{x:{bad:true}}});
 assert.deepEqual(clean.bookmarks,[]);assert.equal(clean.language,'en');assert(!clean.reviews.x);assert.equal(clean.reviews.y.interval,1);assert.deepEqual(clean.notes,{});
});
test('review spacing and language edition selection work',()=>{
 const now=Date.parse('2026-09-24T12:00:00Z');assert.equal(scheduleReview(null,false,now).due,'2026-09-25T12:00:00.000Z');assert.equal(scheduleReview({interval:20},true,now).interval,30);
 assert.equal(latestFor(packets,'te').language,'te');assert.equal(latestFor(packets,'fr'),null);
});
test('headline dates and unsafe source URLs are rejected',()=>{
 const index=JSON.parse(fs.readFileSync(new URL('../dist/headlines.json',import.meta.url)));assert.equal(validateHeadlines(index),index);
 const bad=structuredClone(index);bad.items[0].url='javascript:alert(1)';assert.throws(()=>validateHeadlines(bad));
 bad.items[0].url=index.items[0].url;bad.items[0].published_at='2099-01-01';assert.throws(()=>validateHeadlines(bad));
});
