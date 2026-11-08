/* Comparisons with a free choice of what is on each side. Without JavaScript the two default images show stacked. */
(() => {
  'use strict';

  document.querySelectorAll('[data-compare]').forEach(figure => {
    const frame = figure.querySelector('.comparison');
    const range = figure.querySelector('.comparison-range');
    const line = figure.querySelector('.comparison-line');
    const left = frame.querySelector('.before-image');
    const right = frame.querySelector('.after-image');
    const pickLeft = figure.querySelector('[data-side="left"]');
    const pickRight = figure.querySelector('[data-side="right"]');

    function label(select) {
      return select.options[select.selectedIndex].text;
    }

    function setSplit(value) {
      const position = Math.max(0, Math.min(100, Number(value)));
      frame.style.setProperty('--split', `${position}%`);
      range.setAttribute('aria-valuetext', `${position}% ${label(pickLeft)}, ${100 - position}% ${label(pickRight)}`);
    }

    function update() {
      left.src = pickLeft.value;
      left.alt = label(pickLeft);
      right.src = pickRight.value;
      right.alt = label(pickRight);
      setSplit(range.value);
    }

    pickLeft.addEventListener('change', update);
    pickRight.addEventListener('change', update);
    range.addEventListener('input', () => setSplit(range.value));
    frame.classList.add('is-ready');
    [range, line, figure.querySelector('.compare-pick')].forEach(element => { element.hidden = false; });
    setSplit(range.value);
  });
})();
