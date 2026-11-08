/* Comparisons with a free choice of what is on each side. Without JavaScript the two default images show stacked. */
(() => {
  'use strict';

  function load(src) {
    const image = new Image();
    image.src = src;
    return image.decode().then(() => src);
  }

  document.querySelectorAll('[data-compare]').forEach(figure => {
    const frame = figure.querySelector('.comparison');
    const range = figure.querySelector('.comparison-range');
    const left = frame.querySelector('.before-image');
    const right = frame.querySelector('.after-image');
    const pickLeft = figure.querySelector('[data-side="left"]');
    const pickRight = figure.querySelector('[data-side="right"]');
    const tagLeft = figure.querySelector('[data-label="left"]');
    const tagRight = figure.querySelector('[data-label="right"]');
    const status = figure.querySelector('[data-status]');
    let shown = [pickLeft.value, pickRight.value];
    let request = 0;

    function label(select) {
      return select.options[select.selectedIndex].text;
    }

    function setSplit(value) {
      const position = Math.max(0, Math.min(100, Number(value)));
      frame.style.setProperty('--split', `${position}%`);
      range.setAttribute('aria-valuetext', `${position}% ${tagLeft.textContent}, ${100 - position}% ${tagRight.textContent}`);
    }

    function selectValues(values) {
      [pickLeft.value, pickRight.value] = values;
    }

    function update() {
      const wanted = [pickLeft.value, pickRight.value];
      const names = [label(pickLeft), label(pickRight)];
      const id = ++request;
      frame.setAttribute('aria-busy', 'true');
      status.textContent = 'Loading…';
      Promise.all(wanted.map(load)).then(() => {
        if (id !== request) return;
        [left.src, right.src] = wanted;
        [left.alt, right.alt] = names;
        [tagLeft.textContent, tagRight.textContent] = names;
        shown = wanted;
        frame.removeAttribute('aria-busy');
        status.textContent = `Comparing ${names[0]} with ${names[1]}.`;
        setSplit(range.value);
      }).catch(() => {
        if (id !== request) return;
        selectValues(shown);
        frame.removeAttribute('aria-busy');
        status.textContent = 'That image could not be loaded. The previous comparison is still shown.';
      });
    }

    figure.querySelector('[data-swap]').addEventListener('click', () => {
      selectValues([pickRight.value, pickLeft.value]);
      update();
    });
    pickLeft.addEventListener('change', update);
    pickRight.addEventListener('change', update);
    range.addEventListener('input', () => setSplit(range.value));
    frame.classList.add('is-ready');
    figure.querySelectorAll('[hidden]').forEach(element => { element.hidden = false; });
    setSplit(range.value);
  });
})();
