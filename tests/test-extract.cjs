const assert = require('node:assert/strict');
const {extractPinned}=require('../companion/extract.js');
const card={getAttribute:()=> 'abc-12', querySelector:(s)=>s.includes('Unpin')? {} : {textContent:s.includes('heading')?'<img src="https://invalid/">':'Note text'}};
const doc={querySelector:s=>s.includes('dialog')?null:{}, querySelectorAll:()=>[card,card]};
const location={hash:'',pathname:'/u/1/'};
const result=extractPinned(doc,location);
assert.equal(result.notes.length,1);
assert.equal(result.notes[0].title,'<img src="https://invalid/">');
assert.equal(result.accountPath,'/u/1/');
assert.equal(extractPinned(doc,{...location,hash:'#archive'}),null);
assert.equal(extractPinned({...doc,querySelector:()=>null},location),null);
assert.equal(extractPinned({...doc,querySelectorAll:()=>[]},location).notes.length,0);
console.log('Extraction fixture tests passed');

// Current Keep layout: no public note ID, short Unpin label, new title class.
const currentCard = {
  getAttribute: () => null,
  querySelector: selector => selector.includes('Unpin') ? {} :
    selector.includes('vIzZGf-r4nke') ? {innerText:'Pinned title'} : {innerText:'Pinned body'}
};
const currentDoc = {querySelector:s=>s.includes('dialog')?null:{}, querySelectorAll:()=>[currentCard]};
const current = extractPinned(currentDoc, location).notes[0];
assert.match(current.id, /^local_[a-f0-9]{1,8}$/);
const {readKeepCard} = require('../companion/extract.js');
assert.equal(readKeepCard(currentCard).id, current.id);
assert.equal(current.title, 'Pinned title');
assert.equal(current.text, 'Pinned body');
console.log('Direct navigation identity test passed');
