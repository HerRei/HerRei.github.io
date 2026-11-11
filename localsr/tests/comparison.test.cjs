// Exercise the home page viewer (showcase.js) with controlled image loading, without a browser.
const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '..', 'showcase.js'), 'utf8');
const tick = () => new Promise(resolve => setImmediate(resolve));

function element(extra = {}) {
  return {
    hidden: true, value: '50', textContent: '', src: '', alt: '', dataset: {}, attrs: {}, listeners: {},
    classes: new Set(), styles: {},
    setAttribute(key, value) { this.attrs[key] = String(value); },
    getAttribute(key) { return this.attrs[key]; },
    removeAttribute(key) { delete this.attrs[key]; },
    addEventListener(name, listener) { this.listeners[name] = listener; },
    fire(name) { this.listeners[name]?.(); },
    decode: () => Promise.resolve(),
    ...extra,
  };
}

const EXAMPLES = [
  { name: 'Butterfly', dims: 'Detail at 1:1', before: 'b-in.png', after: 'b-out.webp', altBefore: 'b before', altAfter: 'b after', task: 'Upscale', model: 'RealPLKSR', size: '768 → 3072', ran: 'M1 Pro' },
  { name: 'Sign', dims: 'Whole photo', before: 's-in.png', after: 's-out.webp', altBefore: 's before', altAfter: 's after', task: 'Fix blur', model: 'NAFNet', size: '256 → 1024', ran: 'RX 9060 XT' },
];

async function setup(options = {}) {
  const pending = [];
  class ControlledImage {
    set src(value) { this.url = value; }
    decode() { return new Promise((resolve, reject) => pending.push({ url: this.url, resolve, reject })); }
  }
  const before = element({ src: EXAMPLES[0].before });
  const after = element({ src: EXAMPLES[0].after });
  if (options.initialFailure) after.decode = () => Promise.reject(new Error('offline'));
  const range = element();
  const line = element();
  const split = element({
    querySelector: selector => ({ '.split-before': before, '.split-after': after, '.split-range': range, '.split-line': line })[selector],
  });
  split.classList = { add: name => split.classes.add(name) };
  split.style = { setProperty: (key, value) => { split.styles[key] = value; } };
  const words = ['before', 'split', 'after'].map(view => element({ dataset: { view } }));
  const picks = EXAMPLES.map((data, index) => element({ dataset: { ...data }, attrs: { 'aria-pressed': String(index === 0) } }));
  const facts = ['name', 'dims', 'task', 'model', 'size', 'ran'].map(fact => element({ dataset: { fact } }));
  const wordGroup = element();
  const pickGroup = element();
  const status = element();
  const viewer = element({
    querySelector: selector => ({ '.split': split, '.words': wordGroup, '.picks': pickGroup, '[data-status]': status })[selector],
    querySelectorAll: selector => ({ '[data-view]': words, '.picks button': picks, '[data-fact]': facts })[selector],
  });
  vm.runInNewContext(source, {
    document: { getElementById: id => (id === 'viewer' ? viewer : null) },
    Image: ControlledImage, Promise, Number, String, Math,
  });
  await tick();
  const factText = name => facts.find(item => item.dataset.fact === name).textContent;
  return { split, before, after, range, line, words, picks, wordGroup, pickGroup, status, pending, factText };
}

test('controls appear once both images of the first example load', async () => {
  const { split, range, line, wordGroup, pickGroup, words } = await setup();
  assert.ok(split.classes.has('is-ready'));
  assert.ok([range, line, wordGroup, pickGroup].every(item => !item.hidden));
  assert.equal(split.dataset.view, 'split');
  assert.equal(split.styles['--split'], '50%');
  assert.equal(range.attrs['aria-valuetext'], '50% original, 50% result');
  assert.equal(words[1].attrs['aria-pressed'], 'true');
});

test('the line follows the range and Original or Enhanced show one side whole', async () => {
  const { split, range, words } = await setup();
  range.value = '73';
  range.fire('input');
  assert.equal(split.styles['--split'], '73%');
  assert.equal(range.attrs['aria-valuetext'], '73% original, 27% result');
  words[0].fire('click');
  assert.equal(split.dataset.view, 'before');
  assert.equal(split.styles['--split'], '100%');
  assert.deepEqual(words.map(word => word.attrs['aria-pressed']), ['true', 'false', 'false']);
  words[2].fire('click');
  assert.equal(split.styles['--split'], '0%');
  range.value = '40';
  range.fire('input');
  assert.equal(split.dataset.view, 'split', 'dragging returns to the split view');
  assert.equal(split.styles['--split'], '40%');
});

test('picking an example swaps both images and every fact together', async () => {
  const { split, before, after, range, picks, pending, factText, status } = await setup();
  range.value = '20';
  range.fire('input');
  picks[1].fire('click');
  assert.equal(split.attrs['aria-busy'], 'true');
  pending[0].resolve();
  await tick();
  assert.equal(before.src, 'b-in.png', 'nothing changes until both images are ready');
  pending[1].resolve();
  await tick();
  assert.equal(before.src, 's-in.png');
  assert.equal(after.src, 's-out.webp');
  assert.equal(after.alt, 's after');
  assert.equal(factText('ran'), 'RX 9060 XT');
  assert.equal(factText('task'), 'Fix blur');
  assert.deepEqual(picks.map(item => item.attrs['aria-pressed']), ['false', 'true']);
  assert.equal(split.styles['--split'], '50%', 'a new example starts centred');
  assert.equal(split.attrs['aria-busy'], undefined);
  assert.equal(status.textContent, 'Showing Sign.');
});

test('a quicker second pick wins over a slower first one', async () => {
  const { before, picks, pending } = await setup();
  picks[1].fire('click');
  picks[1].attrs['aria-pressed'] = 'false';
  picks[0].attrs['aria-pressed'] = 'false';
  picks[0].fire('click');
  pending[2].resolve();
  pending[3].resolve();
  await tick();
  pending[0].resolve();
  pending[1].resolve();
  await tick();
  assert.equal(before.src, 'b-in.png');
});

test('a failed example keeps the working pair and says so', async () => {
  const { before, after, picks, pending, status, split } = await setup();
  picks[1].fire('click');
  pending[0].resolve();
  pending[1].reject(new Error('offline'));
  await tick();
  assert.equal(before.src, 'b-in.png');
  assert.equal(after.src, 'b-out.webp');
  assert.match(status.textContent, /could not load/);
  assert.equal(split.attrs['aria-busy'], undefined);
  assert.equal(picks[0].attrs['aria-pressed'], 'true');
});

test('if the first images fail, the controls stay hidden', async () => {
  const { split, range, pickGroup, status } = await setup({ initialFailure: true });
  assert.ok(!split.classes.has('is-ready'));
  assert.ok(range.hidden && pickGroup.hidden);
  assert.match(status.textContent, /could not load/);
});
