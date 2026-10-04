/* Progressive enhancement of a comparison made by the actual LocalSR engine. */
(() => {
  'use strict';

  const comparison = document.getElementById('comparison');
  if (!comparison) return;
  const range = document.getElementById('comparison-range');
  const before = document.getElementById('comparison-before');
  const after = document.getElementById('comparison-after');
  const status = document.getElementById('view-status');
  const viewButtons = [...document.querySelectorAll('[data-view]')];
  const presets = [...document.querySelectorAll('[data-split]')];
  const dimensions = comparison.querySelectorAll('.image-labels b');
  let view = 'frame';
  let requestId = 0;

  const views = {
    frame: { before: 'assets/marseille-input.png', after: 'assets/marseille-output.webp', input: '480 × 240', output: '1920 × 960', label: 'Full landscape crop. Input 480 by 240 pixels; LocalSR result 1920 by 960 pixels.' },
    detail: { before: 'assets/marseille-detail-input.png', after: 'assets/marseille-detail-output.webp', input: '160 × 80 crop', output: '640 × 320 crop', label: 'Closer view of the same area. Input crop 160 by 80 pixels; LocalSR result crop 640 by 320 pixels.' }
  };

  function updateSplit(value) {
    const numeric = Number(value);
    const position = Number.isFinite(numeric) ? Math.max(0, Math.min(100, numeric)) : 50;
    range.value = String(position);
    comparison.style.setProperty('--split', `${position}%`);
    range.setAttribute('aria-valuetext', `${position}% input and ${100 - position}% LocalSR result`);
    presets.forEach(button => button.setAttribute('aria-pressed', String(Number(button.dataset.split) === position)));
  }

  function preloadImage(src) {
    return new Promise((resolve, reject) => {
      const image = new Image();
      image.onload = () => resolve(image);
      image.onerror = () => reject(new Error('Image unavailable'));
      image.src = src;
    });
  }

  async function changeView(nextView) {
    if (!Object.hasOwn(views, nextView)) return;
    const currentRequest = ++requestId;
    if (nextView === view) {
      comparison.removeAttribute('aria-busy');
      status.textContent = views[view].label;
      return;
    }
    const next = views[nextView];
    comparison.setAttribute('aria-busy', 'true');
    try {
      // Swap the pair together so fast switching never compares different crops.
      await Promise.all([preloadImage(next.before), preloadImage(next.after)]);
      if (currentRequest !== requestId) return;
      before.src = next.before;
      after.src = next.after;
      before.alt = nextView === 'detail' ? 'A close crop of balcony railings in the low-resolution input.' : 'Low-resolution photograph of colored balconies and concrete railings in Marseille.';
      after.alt = nextView === 'detail' ? 'The matching crop from the actual four-times LocalSR output.' : 'The same photograph enlarged four times by LocalSR’s SPAN NomosUni model.';
      dimensions[0].textContent = next.input;
      dimensions[1].textContent = next.output;
      view = nextView;
      viewButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.view === nextView)));
      status.textContent = next.label;
    } catch {
      if (currentRequest === requestId) status.textContent = 'The selected view could not load. The current comparison is still available.';
    } finally {
      if (currentRequest === requestId) comparison.removeAttribute('aria-busy');
    }
  }

  function initialize() {
    if (!before.naturalWidth || !after.naturalWidth) return;
    comparison.classList.add('is-ready');
    document.querySelectorAll('.comparison-enhancement').forEach(element => { element.hidden = false; });
    updateSplit(range.value);
    range.addEventListener('input', () => updateSplit(range.value));
    presets.forEach(button => button.addEventListener('click', () => updateSplit(button.dataset.split)));
    viewButtons.forEach(button => button.addEventListener('click', () => { changeView(button.dataset.view); }));
  }

  Promise.all([before.decode(), after.decode()]).then(initialize).catch(() => {
    status.textContent = 'The comparison images could not load. Please reload the page to try again.';
  });
})();
