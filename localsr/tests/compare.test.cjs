// Exercise the comparison page script with controlled image loading, without a browser dependency.
const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '..', 'compare', 'compare.js'), 'utf8');
const tick = () => new Promise(resolve => setImmediate(resolve));

function element(extra = {}) {
  return {
    hidden: true, value: '50', textContent: '', src: '', alt: '', attrs: {}, listeners: {}, classes: new Set(), styles: {},
    setAttribute(key, value) { this.attrs[key] = value; },
    removeAttribute(key) { delete this.attrs[key]; },
    addEventListener(name, listener) { this.listeners[name] = listener; },
    fire(name) { this.listeners[name]?.(); },
    ...extra,
  };
}

function select(choices, chosen) {
  const options = choices.map(([value, text]) => ({ value, text }));
  const node = element({ options, selectedIndex: choices.findIndex(([value]) => value === chosen) });
  Object.defineProperty(node, 'value', {
    get() { return this.options[this.selectedIndex].value; },
    set(value) { this.selectedIndex = this.options.findIndex(option => option.value === value); },
  });
  return node;
}

function setup(failing = new Set()) {
  const choices = [['a.webp', 'Upscayl Standard'], ['b.webp', 'LocalSR Best'], ['c.webp', 'Original'], ['input.webp', 'Damaged input']];
  const left = element({ src: 'a.webp' });
  const right = element({ src: 'b.webp' });
  const frame = element({ querySelector: selector => ({ '.before-image': left, '.after-image': right })[selector] });
  frame.classList = { add: name => frame.classes.add(name) };
  frame.style = { setProperty: (key, value) => { frame.styles[key] = value; } };
  const toggle = element({ textContent: 'Show input' });
  const parts = {
    '.comparison': frame, '.comparison-range': element(), '[data-side="left"]': select(choices, 'a.webp'),
    '[data-side="right"]': select(choices, 'b.webp'), '[data-label="left"]': element({ textContent: 'Upscayl Standard' }),
    '[data-label="right"]': element({ textContent: 'LocalSR Best' }), '[data-status]': element({ hidden: false }),
    '[data-toggle-input]': toggle, '[data-swap]': toggle, '.compare-pick': element(),
  };
  const hidden = [parts['.compare-pick'], parts['.comparison-range'], parts['[data-label="left"]']];
  const figure = {
    querySelector: selector => {
      if (selector === '[data-toggle-input], [data-swap]') return toggle;
      return parts[selector];
    },
    querySelectorAll: () => hidden.filter(item => item.hidden),
  };
  class ControlledImage {
    set src(value) { this.url = value; }
    decode() { return failing.has(this.url) ? Promise.reject(new Error('missing')) : Promise.resolve(); }
  }
  vm.runInNewContext(source, {
    document: { querySelectorAll: () => [figure] }, Image: ControlledImage, Promise, Number, Math,
  });
  return { ...parts, toggle, left, right, frame, hidden };
}

test('the comparison is ready with both sides labelled', () => {
  const ui = setup();
  assert.ok(ui.frame.classes.has('is-ready'));
  assert.ok(ui.hidden.every(item => !item.hidden));
  assert.equal(ui.frame.styles['--split'], '50%');
  assert.equal(ui['.comparison-range'].attrs['aria-valuetext'], '50% Upscayl Standard, 50% LocalSR Best');
});

test('a new choice shows only after both images have loaded', async () => {
  const ui = setup();
  ui['[data-side="left"]'].value = 'c.webp';
  ui['[data-side="left"]'].fire('change');
  assert.equal(ui.left.src, 'a.webp');
  assert.equal(ui.frame.attrs['aria-busy'], 'true');
  await tick();
  assert.equal(ui.left.src, 'c.webp');
  assert.equal(ui.left.alt, 'Original');
  assert.equal(ui['[data-label="left"]'].textContent, 'Original');
  assert.equal(ui.frame.attrs['aria-busy'], undefined);
  assert.equal(ui['[data-status]'].textContent, 'Comparing Original with LocalSR Best.');
});

test('toggle switches between input vs original and the comparison', async () => {
  const ui = setup();
  assert.equal(ui.toggle.textContent, 'Show input');
  assert.equal(ui.toggle.attrs['aria-pressed'], 'false');

  // Click toggle: should show Damaged input on left and Original on right
  ui.toggle.fire('click');
  await tick();
  assert.equal(ui.left.src, 'input.webp');
  assert.equal(ui.left.alt, 'Damaged input');
  assert.equal(ui.right.src, 'c.webp');
  assert.equal(ui.right.alt, 'Original');
  assert.equal(ui['[data-side="left"]'].value, 'input.webp');
  assert.equal(ui['[data-side="right"]'].value, 'c.webp');
  assert.equal(ui.toggle.textContent, 'Show comparison');
  assert.equal(ui.toggle.attrs['aria-pressed'], 'true');

  // Click toggle again: should restore comparison (Upscayl Standard and LocalSR Best)
  ui.toggle.fire('click');
  await tick();
  assert.equal(ui.left.src, 'a.webp');
  assert.equal(ui.left.alt, 'Upscayl Standard');
  assert.equal(ui.right.src, 'b.webp');
  assert.equal(ui.right.alt, 'LocalSR Best');
  assert.equal(ui['[data-side="left"]'].value, 'a.webp');
  assert.equal(ui['[data-side="right"]'].value, 'b.webp');
  assert.equal(ui.toggle.textContent, 'Show input');
  assert.equal(ui.toggle.attrs['aria-pressed'], 'false');
});

test('a missing image keeps the previous comparison and says so', async () => {
  const ui = setup(new Set(['c.webp']));
  ui['[data-side="right"]'].value = 'c.webp';
  ui['[data-side="right"]'].fire('change');
  await tick();
  assert.equal(ui.right.src, 'b.webp');
  assert.equal(ui['[data-side="right"]'].value, 'b.webp');
  assert.match(ui['[data-status]'].textContent, /could not be loaded/);
});
