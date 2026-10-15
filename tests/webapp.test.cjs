const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
function app(telegram) {
  const nodes = {selection:{},usercard:{}};
  const buttons = ['1','2'].map(id => ({dataset:{item:id},setAttribute(k,v){this[k]=v},addEventListener(k,fn){this.click=fn}}));
  vm.runInNewContext(fs.readFileSync('app.js','utf8'), {window:{Telegram:telegram},document:{getElementById:id=>nodes[id],querySelectorAll:()=>buttons}});
  return {nodes,buttons};
}
test('standalone preview works without Telegram SDK', () => {
  const {nodes,buttons}=app(); buttons[0].click();
  assert.match(nodes.usercard.textContent,/Предпросмотр/); assert.equal(buttons[0]['aria-pressed'],'true');
});
test('switching products selects the latest and clicking again clears', () => {
  const {buttons}=app();buttons[0].click();buttons[1].click();
  assert.equal(buttons[0]['aria-pressed'],'false');assert.equal(buttons[1]['aria-pressed'],'true');
  buttons[1].click();assert.equal(buttons[1]['aria-pressed'],'false');
});
test('Telegram sends only a selected product and tolerates absent user', () => {
  const sent=[];let click; const tg={initData:'demo',ready(){},expand(){},MainButton:{setText(){},show(){},hide(){}},onEvent(e,fn){click=fn},sendData:x=>sent.push(x)};
  const {buttons}=app({WebApp:tg});click();assert.deepEqual(sent,[]);buttons[1].click();click();assert.deepEqual(sent,['2']);
});
test('user names are assigned as text', () => {
  const tg={initData:'demo',initDataUnsafe:{user:{first_name:'<b>Demo</b>'}},ready(){},expand(){},MainButton:{},onEvent(){}};
  const {nodes}=app({WebApp:tg});assert.equal(nodes.usercard.textContent,'Здравствуйте, <b>Demo</b>!');assert.equal(nodes.usercard.innerHTML,undefined);
});
