// Exercise the shipped script with controlled image loading, without a browser dependency.
const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '..', 'showcase.js'), 'utf8');
const tick = () => new Promise(resolve => setImmediate(resolve));

function element(dataset = {}) {
  return {
    dataset, hidden: true, value: '50', naturalWidth: 480, textContent: '', src: '',
    attrs: {}, listeners: {}, classes: new Set(), styles: {},
    setAttribute(key, value) { this.attrs[key] = value; },
    removeAttribute(key) { delete this.attrs[key]; },
    addEventListener(name, listener) { this.listeners[name] = listener; },
    fire(name) { this.listeners[name]?.(); },
    decode: () => Promise.resolve(),
  };
}

async function setup(options = {}) {
  const ids = Object.fromEntries(['comparison', 'comparison-range', 'comparison-before', 'comparison-after', 'view-status'].map(id => [id, element()]));
  const dimensions = [element(), element()];
  const views = ['frame', 'detail'].map(view => element({ view }));
  const presets = ['100', '50', '0'].map(split => element({ split }));
  const enhancements = [ids['comparison-range'], ...views, ...presets];
  const pending = [];
  ids.comparison.classList = { add: name => ids.comparison.classes.add(name) };
  ids.comparison.style = { setProperty: (key, value) => { ids.comparison.styles[key] = value; } };
  ids.comparison.querySelectorAll = () => dimensions;
  ids['comparison-before'].src = 'assets/marseille-input.png';
  ids['comparison-after'].src = 'assets/marseille-output.webp';
  if (options.initialFailure) ids['comparison-after'].decode = () => Promise.reject(new Error('offline'));
  class ControlledImage {
    set src(value) { this.url = value; pending.push(this); }
  }
  vm.runInNewContext(source, {
    document: {
      getElementById: id => ids[id],
      querySelectorAll: selector => ({ '[data-view]': views, '[data-split]': presets, '.comparison-enhancement': enhancements })[selector],
    },
    Image: ControlledImage, Promise, Number, Object, String, Error,
  });
  await tick();
  return { ids, dimensions, views, presets, enhancements, pending };
}

test('controls appear after both comparison images load', async () => {
  const { ids, enhancements } = await setup();
  assert.ok(ids.comparison.classes.has('is-ready'));
  assert.ok(enhancements.every(item => !item.hidden));
  assert.equal(ids.comparison.styles['--split'], '50%');
  assert.equal(ids['comparison-range'].attrs['aria-valuetext'], '50% input and 50% LocalSR result');
});

test('input, split, and result controls reach both endpoints with accessible state', async () => {
  const { ids, presets } = await setup();
  for (const preset of presets) {
    preset.fire('click');
    assert.equal(ids.comparison.styles['--split'], preset.dataset.split + '%');
    assert.equal(preset.attrs['aria-pressed'], 'true');
    assert.equal(presets.filter(item => item.attrs['aria-pressed'] === 'true').length, 1);
  }
  ids['comparison-range'].value = '73';
  ids['comparison-range'].fire('input');
  assert.equal(ids.comparison.styles['--split'], '73%');
  assert.equal(ids['comparison-range'].attrs['aria-valuetext'], '73% input and 27% LocalSR result');
  assert.ok(presets.every(item => item.attrs['aria-pressed'] === 'false'));
});

test('detail switches both images together and retains divider position', async () => {
  const { ids, dimensions, views, pending } = await setup();
  ids['comparison-range'].value = '29';
  ids['comparison-range'].fire('input');
  views[1].fire('click');
  pending[0].onload();
  await tick();
  assert.equal(ids['comparison-before'].src, 'assets/marseille-input.png');
  pending[1].onload();
  await tick();
  assert.equal(ids['comparison-before'].src, 'assets/marseille-detail-input.png');
  assert.equal(ids['comparison-after'].src, 'assets/marseille-detail-output.webp');
  assert.equal(dimensions[1].textContent, '640 × 320 crop');
  assert.equal(ids.comparison.styles['--split'], '29%');
  assert.equal(views[1].attrs['aria-pressed'], 'true');
  assert.equal(ids.comparison.attrs['aria-busy'], undefined);
});

test('returning to the current view cancels a pending switch', async () => {
  const { ids, views, pending } = await setup();
  views[1].fire('click');
  views[0].fire('click');
  pending.forEach(image => image.onload());
  await tick();
  assert.equal(ids['comparison-before'].src, 'assets/marseille-input.png');
  assert.equal(ids['comparison-after'].src, 'assets/marseille-output.webp');
  assert.equal(ids.comparison.attrs['aria-busy'], undefined);
});

test('a failed detail image preserves the working pair and reports the problem', async () => {
  const { ids, views, pending } = await setup();
  views[1].fire('click');
  pending[0].onload();
  pending[1].onerror();
  await tick();
  assert.equal(ids['comparison-before'].src, 'assets/marseille-input.png');
  assert.equal(ids['comparison-after'].src, 'assets/marseille-output.webp');
  assert.match(ids['view-status'].textContent, /could not load/);
  assert.equal(ids.comparison.attrs['aria-busy'], undefined);
});

test('image startup failure leaves progressive controls hidden', async () => {
  const { ids, enhancements } = await setup({ initialFailure: true });
  assert.ok(!ids.comparison.classes.has('is-ready'));
  assert.ok(enhancements.every(item => item.hidden));
  assert.match(ids['view-status'].textContent, /could not load/);
});
