// A short guided tour over the real LocalSR interface. Each step points at one
// element and moves on when the visitor does the thing it describes (or
// presses Next), so the tour never fights the app.

export interface TourStep {
  title: string;
  body: string;
  /** Element to point at; none centres the card. */
  target?: string;
  /** Keep the card small at the side, with nothing dimmed, so the picture stays free. */
  aside?: boolean;
  /** Label of the button that moves on. */
  nextLabel?: string;
  /** Small print under the text (HTML). */
  note?: string;
  /** Moves on by itself when this returns true. */
  done?: () => boolean;
  /** Hide Next until `done` is met. */
  requireAction?: boolean;
  /** Extra buttons on the last card. */
  links?: { label: string; href: string; primary?: boolean }[];
}

const $ = (selector: string): HTMLElement | null => document.querySelector(selector);

function zoomPercent(): number {
  const label = $('.zoom-hud span')?.textContent ?? '';
  return Number.parseInt(label, 10) || 100;
}

export const steps: TourStep[] = [
  {
    title: 'Try LocalSR in your browser',
    body: 'This is the real LocalSR window, replaying a recorded upscale from a MacBook. Seven short steps, then the result is yours to explore. Nothing is uploaded: the photo and the result are part of this page.',
    // Phones get the app's compact layout; the tour still works, the window is just cramped.
  },
  {
    title: 'Your photo',
    body: 'Photos and videos you add are listed here. This is a night shot of Landskron castle at 800 × 450 pixels, about what a phone or a website keeps of a photo.',
    target: '.media-row',
  },
  {
    title: 'Choose Best',
    body: 'Quick is fast and clean. Best spends more time and rebuilds the most detail. Click Best.',
    target: '.recipe-grid .best',
    done: () => Boolean($('.recipe-grid .best.active')),
    requireAction: true,
  },
  {
    title: 'Start the upscale',
    body: 'Press the button. In the app, the first press also downloads the model, once.',
    target: '.status-bar .start',
    done: () => Boolean($('.model-activity') || $('.progressive-image.visible') || $('.result-image')),
    requireAction: true,
  },
  {
    title: 'Watch it work',
    body: 'LocalSR enlarges the photo four times in tiles; each tile shows up as soon as it is done. On the M1 Pro this run took 5 seconds, on the GPU, offline.',
    target: '.canvas-well',
    done: () => Boolean($('.result-image')),
    requireAction: true,
  },
  {
    title: 'Before and after',
    body: 'Left of the divider is the photo as it was, right is LocalSR’s result. Drag the divider across the castle.',
    target: '.compare-line span',
  },
  {
    title: 'Zoom into the castle',
    body: 'Scroll or pinch over the picture to zoom in. The divider stays where it is, so you always see both sides. Zoom to 400 % or more.',
    target: '.canvas-well',
    done: () => zoomPercent() >= 400,
  },
  {
    title: 'Original, Split, Enhanced',
    body: 'Switch between the whole original, the divider and the whole result up here. Or hold M to flash the original wherever you are.',
    target: '.view-switch',
  },
  {
    title: 'Now look for yourself',
    body: 'Drag the divider, zoom into the castle and the stars, switch between Original and Enhanced. Take as long as you like.',
    aside: true,
    nextLabel: 'I’m done looking',
  },
  {
    title: 'That’s LocalSR',
    body: 'A 3200 × 1800 result from an 800 × 450 photo, made on the computer that holds the photo. Free for macOS, Windows and Linux.',
    aside: true,
    note: 'Photo: Landskron castle by Hermes Reisner. Result: <a href="https://huggingface.co/Phips/4xNomosWebPhoto_RealPLKSR">RealPLKSR ×4 NomosWebPhoto</a> by Philip Hofmann, <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.',
    links: [
      { label: 'Download LocalSR', href: '../download/', primary: true },
      { label: 'Back to the showcase', href: '../' },
    ],
  },
];

export function startTour(onRestart: () => void): void {
  const layer = document.createElement('div');
  layer.className = 'tour-layer';
  const ring = document.createElement('div');
  ring.className = 'tour-ring';
  ring.hidden = true;
  const card = document.createElement('section');
  card.className = 'tour-card';
  card.setAttribute('role', 'dialog');
  card.setAttribute('aria-live', 'polite');
  card.setAttribute('aria-label', 'Guided tour');
  layer.append(ring, card);
  document.body.append(layer);

  const pill = document.createElement('button');
  pill.className = 'tour-pill';
  pill.type = 'button';
  pill.textContent = 'Guided tour';
  pill.hidden = true;
  document.body.append(pill);

  let index = 0;
  let frame = 0;

  function close(): void {
    layer.hidden = true;
    pill.hidden = false;
    cancelAnimationFrame(frame);
  }

  function open(at: number): void {
    index = at;
    layer.hidden = false;
    pill.hidden = true;
    render();
    track();
  }

  pill.addEventListener('click', () => {
    if (index >= steps.length - 1) {
      onRestart();
      open(1);
    } else open(index);
  });

  function render(): void {
    const step = steps[index];
    const last = index === steps.length - 1;
    const counted = steps.length - 3; // without the intro, the free look and the last card
    const counter =
      index === 0 || index > counted ? '' : `<span class="tour-count">${index} of ${counted}</span>`;
    const actions: string[] = [];
    if (index === 0) {
      actions.push('<button type="button" class="tour-primary" data-act="next">Start the tour</button>');
      actions.push('<button type="button" data-act="close">Look around on my own</button>');
    } else if (last) {
      for (const link of step.links ?? [])
        actions.push(`<a class="${link.primary ? 'tour-primary' : ''}" href="${link.href}">${link.label}</a>`);
      actions.push('<button type="button" data-act="restart">Start again</button>');
    } else {
      actions.push('<button type="button" data-act="back">Back</button>');
      actions.push(
        `<button type="button" class="tour-primary" data-act="next"${step.requireAction ? ' hidden' : ''}>${step.nextLabel ?? 'Next'}</button>`,
      );
      actions.push('<button type="button" class="tour-quiet" data-act="close">Close</button>');
    }
    const narrow =
      index === 0 && window.innerWidth < 1100
        ? '<p class="tour-note">Best on a computer screen: LocalSR is a desktop app.</p>'
        : '';
    const note = step.note ? `<p class="tour-note">${step.note}</p>` : '';
    card.innerHTML = `${counter}<h2>${step.title}</h2><p>${step.body}</p>${narrow}${note}<div class="tour-actions">${actions.join('')}</div>`;
    card.querySelectorAll<HTMLElement>('[data-act]').forEach((button) =>
      button.addEventListener('click', () => {
        const act = button.dataset.act;
        if (act === 'next') open(Math.min(steps.length - 1, index + 1));
        if (act === 'back') open(Math.max(1, index - 1));
        if (act === 'close') close();
        if (act === 'restart') {
          onRestart();
          open(1);
        }
      }),
    );
    card.querySelector<HTMLElement>('.tour-primary')?.focus({ preventScroll: true });
  }

  function place(): void {
    const step = steps[index];
    card.classList.toggle('aside', Boolean(step.aside));
    if (step.aside) {
      // Bottom left, over the media list, with nothing dimmed.
      ring.hidden = true;
      card.classList.remove('centred');
      const status = $('.status-bar')?.getBoundingClientRect().height ?? 56;
      card.style.left = '16px';
      card.style.top = `${window.innerHeight - status - card.offsetHeight - 16}px`;
      return;
    }
    const target = step.target ? $(step.target) : null;
    const rect = target?.getBoundingClientRect();
    if (!target || !rect || rect.width === 0) {
      ring.hidden = true;
      card.classList.add('centred');
      card.style.left = '';
      card.style.top = '';
      return;
    }
    card.classList.remove('centred');
    ring.hidden = false;
    const pad = 6;
    Object.assign(ring.style, {
      left: `${rect.left - pad}px`,
      top: `${rect.top - pad}px`,
      width: `${rect.width + pad * 2}px`,
      height: `${rect.height + pad * 2}px`,
    });
    const gap = 16;
    const width = card.offsetWidth;
    const height = card.offsetHeight;
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    // Big targets (the picture) keep the card off the image, over the media list.
    if (rect.width * rect.height > vw * vh * 0.3) {
      const status = $('.status-bar')?.getBoundingClientRect().height ?? 56;
      card.style.left = `${gap}px`;
      card.style.top = `${vh - status - height - gap}px`;
      return;
    }
    // Prefer the side with room: right, left, below, above; big targets get the card inside.
    let left = rect.right + gap;
    let top = rect.top;
    if (left + width > vw - gap) left = rect.left - width - gap;
    if (left < gap) {
      left = Math.min(Math.max(gap, rect.left), vw - width - gap);
      top = rect.bottom + gap;
      if (top + height > vh - gap) top = rect.top - height - gap;
      if (top < gap) top = rect.top + gap;
    }
    top = Math.min(Math.max(gap, top), vh - height - gap);
    card.style.left = `${left}px`;
    card.style.top = `${top}px`;
  }

  function track(): void {
    cancelAnimationFrame(frame);
    const tick = (): void => {
      if (layer.hidden) return;
      place();
      const step = steps[index];
      if (step.done?.()) {
        if (step.requireAction) open(Math.min(steps.length - 1, index + 1));
        else card.querySelector<HTMLElement>('[data-act="next"]')?.classList.add('ready');
        if (step.requireAction) return;
      }
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
  }

  open(0);
}
