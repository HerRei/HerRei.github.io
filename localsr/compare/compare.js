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
    const toggle = figure.querySelector('[data-toggle-input], [data-swap]');
    let shown = [pickLeft.value, pickRight.value];
    let request = 0;

    const leftInputOpt = [...pickLeft.options].find(opt => opt.text.trim() === 'Damaged input' || opt.value.includes('input.webp'));
    const leftInputVal = leftInputOpt ? leftInputOpt.value : '';

    const rightOrigOpt = [...pickRight.options].find(opt => opt.text.trim() === 'Original' || opt.value.includes('original.webp'));
    const rightOrigVal = rightOrigOpt ? rightOrigOpt.value : '';

    function isReferencePair(leftVal, rightVal) {
      return Boolean(leftInputVal && rightOrigVal && leftVal === leftInputVal && rightVal === rightOrigVal);
    }

    function findDefaultComparison() {
      const leftModel = [...pickLeft.options].find(opt => opt.value !== leftInputVal && opt.value !== rightOrigVal && !opt.value.includes('input.webp') && !opt.value.includes('original.webp'))?.value || pickLeft.options[0]?.value || '';
      const rightModel = [...pickRight.options].find(opt => opt.value !== leftInputVal && opt.value !== rightOrigVal && !opt.value.includes('input.webp') && !opt.value.includes('original.webp'))?.value || pickRight.options[1]?.value || '';
      return [leftModel, rightModel];
    }

    let savedSides = isReferencePair(pickLeft.value, pickRight.value)
      ? findDefaultComparison()
      : [pickLeft.value, pickRight.value];
    let isInputMode = isReferencePair(pickLeft.value, pickRight.value);

    function label(select) {
      return select.options[select.selectedIndex].text;
    }

    function updateButton() {
      if (!toggle) return;
      toggle.textContent = isInputMode ? 'Show comparison' : 'Show input';
      toggle.setAttribute('aria-label', isInputMode ? 'Show comparison' : 'Show input');
      toggle.setAttribute('aria-pressed', String(isInputMode));
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
        isInputMode = isReferencePair(pickLeft.value, pickRight.value);
        updateButton();
        frame.removeAttribute('aria-busy');
        status.textContent = `Comparing ${names[0]} with ${names[1]}.`;
        setSplit(range.value);
      }).catch(() => {
        if (id !== request) return;
        selectValues(shown);
        isInputMode = isReferencePair(shown[0], shown[1]);
        updateButton();
        frame.removeAttribute('aria-busy');
        status.textContent = 'That image could not be loaded. The previous comparison is still shown.';
      });
    }

    if (toggle) {
      toggle.addEventListener('click', () => {
        if (isInputMode) {
          if (isReferencePair(savedSides[0], savedSides[1])) {
            savedSides = findDefaultComparison();
          }
          selectValues(savedSides);
          isInputMode = false;
        } else {
          savedSides = [pickLeft.value, pickRight.value];
          if (leftInputVal) pickLeft.value = leftInputVal;
          if (rightOrigVal) pickRight.value = rightOrigVal;
          isInputMode = true;
        }
        updateButton();
        update();
      });
    }

    function handleSelectChange() {
      if (isReferencePair(pickLeft.value, pickRight.value)) {
        isInputMode = true;
      } else {
        savedSides = [pickLeft.value, pickRight.value];
        isInputMode = false;
      }
      updateButton();
      update();
    }

    pickLeft.addEventListener('change', handleSelectChange);
    pickRight.addEventListener('change', handleSelectChange);
    range.addEventListener('input', () => setSplit(range.value));
    frame.classList.add('is-ready');
    figure.querySelectorAll('[hidden]').forEach(element => { element.hidden = false; });
    updateButton();
    setSplit(range.value);
  });
})();
