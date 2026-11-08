/* Before/after dividers for the comparison page. Without JavaScript both images show stacked. */
(() => {
  'use strict';

  document.querySelectorAll('[data-compare]').forEach(figure => {
    const frame = figure.querySelector('.comparison');
    const range = figure.querySelector('.comparison-range');
    const line = figure.querySelector('.comparison-line');
    const views = [...figure.querySelectorAll('[data-show]')];
    const left = frame.querySelector('.before-image');
    const sources = { upscayl: left.getAttribute('src'), input: figure.dataset.input, original: figure.dataset.original };
    const labels = { upscayl: 'Upscayl', input: 'Damaged input', original: 'Original' };
    const leftLabel = figure.querySelector('[data-left-label]');

    function setSplit(value) {
      const position = Math.max(0, Math.min(100, Number(value)));
      frame.style.setProperty('--split', `${position}%`);
      range.setAttribute('aria-valuetext', `${position}% ${leftLabel.textContent}, ${100 - position}% LocalSR`);
    }

    function show(name) {
      left.src = sources[name];
      leftLabel.textContent = labels[name];
      views.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.show === name)));
      setSplit(range.value);
    }

    range.addEventListener('input', () => setSplit(range.value));
    views.forEach(button => button.addEventListener('click', () => show(button.dataset.show)));
    frame.classList.add('is-ready');
    range.hidden = false;
    line.hidden = false;
    figure.querySelector('.compare-views').hidden = false;
    setSplit(range.value);
  });
})();
