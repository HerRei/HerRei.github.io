/* The example viewer on the home page: real LocalSR results, a line to drag, and a choice of examples.
   Without JavaScript the first result shows on its own. */
(() => {
  'use strict';

  const viewer = document.getElementById('viewer');
  if (!viewer) return;
  const split = viewer.querySelector('.split');
  const before = split.querySelector('.split-before');
  const after = split.querySelector('.split-after');
  const range = split.querySelector('.split-range');
  const line = split.querySelector('.split-line');
  const wordGroup = viewer.querySelector('.words');
  const words = [...viewer.querySelectorAll('[data-view]')];
  const pickGroup = viewer.querySelector('.picks');
  const picks = [...viewer.querySelectorAll('.picks button')];
  const status = viewer.querySelector('[data-status]');
  const facts = {};
  viewer.querySelectorAll('[data-fact]').forEach(element => { facts[element.dataset.fact] = element; });
  let request = 0;

  function clamp(value) {
    const number = Number(value);
    return Number.isFinite(number) ? Math.max(0, Math.min(100, number)) : 50;
  }

  function setSplit(value) {
    const position = clamp(value);
    range.value = String(position);
    split.style.setProperty('--split', `${position}%`);
    range.setAttribute('aria-valuetext', `${position}% original, ${100 - position}% result`);
  }

  function setView(view) {
    split.dataset.view = view;
    words.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.view === view)));
    if (view === 'before') split.style.setProperty('--split', '100%');
    else if (view === 'after') split.style.setProperty('--split', '0%');
    else setSplit(range.value);
  }

  function load(src) {
    const image = new Image();
    image.src = src;
    return image.decode().then(() => src);
  }

  function pick(button) {
    if (button.getAttribute('aria-pressed') === 'true') return;
    const data = button.dataset;
    const id = ++request;
    split.setAttribute('aria-busy', 'true');
    status.textContent = 'Loading…';
    // Swap both images together so the two sides never come from different examples.
    Promise.all([load(data.before), load(data.after)]).then(() => {
      if (id !== request) return;
      before.src = data.before;
      after.src = data.after;
      before.alt = data.altBefore;
      after.alt = data.altAfter;
      ['name', 'dims', 'task', 'model', 'size', 'ran'].forEach(key => {
        if (facts[key]) facts[key].textContent = data[key];
      });
      picks.forEach(other => other.setAttribute('aria-pressed', String(other === button)));
      range.value = '50';
      setView('split');
      split.removeAttribute('aria-busy');
      status.textContent = `Showing ${data.name}.`;
    }).catch(() => {
      if (id !== request) return;
      split.removeAttribute('aria-busy');
      status.textContent = 'That example could not load. The previous one is still shown.';
    });
  }

  function initialize() {
    split.classList.add('is-ready');
    [wordGroup, pickGroup, line, range].forEach(element => { if (element) element.hidden = false; });
    setView('split');
    range.addEventListener('input', () => {
      if (split.dataset.view !== 'split') setView('split');
      setSplit(range.value);
    });
    words.forEach(button => button.addEventListener('click', () => setView(button.dataset.view)));
    picks.forEach(button => button.addEventListener('click', () => pick(button)));
  }

  Promise.all([before.decode(), after.decode()]).then(initialize).catch(() => {
    status.textContent = 'The comparison images could not load. The result is shown on its own.';
  });
})();
