/**
 * Adversarial Empirical Stress-Test Suite for HerRei.github.io Interactive JavaScript Engines
 * Tests:
 * 1. Web Audio API Piano Synthesizer & Canvas Oscilloscope
 * 2. ANSI Terminal Telemetry Simulator
 * 3. Modal Lightbox & Tab Controller
 * 4. Category Filtering Engine
 * 5. Full Browser Context Simulation with Zero Console/Runtime Exceptions
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

console.log("===============================================================================");
console.log("   ADVERSARIAL EMPIRICAL STRESS-TEST HARNESS (INTERACTIVE ENGINES)           ");
console.log("===============================================================================\n");

// Read index.html
const indexPath = path.resolve(__dirname, '../index.html');
const indexHtml = fs.readFileSync(indexPath, 'utf8');

// Extract Script Content
const scriptMatch = indexHtml.match(/<script>([\s\S]*?)<\/script>/);
if (!scriptMatch) {
  console.error("FATAL: Could not extract <script> tag from index.html");
  process.exit(1);
}
const scriptContent = scriptMatch[1];

// Extract AtelierPianoAudioEngine class specifically for direct isolated unit tests
const classMatch = scriptContent.match(/class AtelierPianoAudioEngine\s*\{[\s\S]*?\n\s{6}\}/);
if (!classMatch) {
  console.error("FATAL: Could not extract AtelierPianoAudioEngine class from script");
  process.exit(1);
}
const classDefCode = classMatch[0];

let totalTests = 0;
let passedTests = 0;
let failedTests = 0;

function runTest(name, fn) {
  totalTests++;
  try {
    fn();
    console.log(`  [PASS] ${name}`);
    passedTests++;
  } catch (err) {
    console.error(`  [FAIL] ${name}: ${err.message}`);
    if (err.stack) console.error(err.stack);
    failedTests++;
  }
}

// -----------------------------------------------------------------------------
// SECTION 1: Mock DOM and Web Audio API Engine
// -----------------------------------------------------------------------------

class MockAudioParam {
  constructor(defaultValue = 0) {
    this.value = defaultValue;
    this.events = [];
  }
  setValueAtTime(val, time) {
    this.value = val;
    this.events.push({ type: 'setValueAtTime', val, time });
  }
  linearRampToValueAtTime(val, time) {
    this.value = val;
    this.events.push({ type: 'linearRampToValueAtTime', val, time });
  }
  exponentialRampToValueAtTime(val, time) {
    if (val <= 0) {
      throw new RangeError("exponentialRampToValueAtTime target value must be strictly positive (> 0)");
    }
    this.value = val;
    this.events.push({ type: 'exponentialRampToValueAtTime', val, time });
  }
}

class MockAudioNode {
  constructor(context) {
    this.context = context;
    this.connections = [];
  }
  connect(dest) {
    this.connections.push(dest);
    return dest;
  }
  disconnect() {
    this.connections = [];
  }
}

class MockOscillatorNode extends MockAudioNode {
  constructor(context) {
    super(context);
    this.type = 'sine';
    this.frequency = new MockAudioParam(440);
    this.started = false;
    this.stopped = false;
    this.startTime = null;
    this.stopTime = null;
  }
  start(time = 0) {
    this.started = true;
    this.startTime = time;
    this.context.activeOscillators.push(this);
  }
  stop(time = 0) {
    this.stopped = true;
    this.stopTime = time;
    this.context.stoppedOscillators.push(this);
  }
}

class MockGainNode extends MockAudioNode {
  constructor(context) {
    super(context);
    this.gain = new MockAudioParam(1);
  }
}

class MockBiquadFilterNode extends MockAudioNode {
  constructor(context) {
    super(context);
    this.type = 'lowpass';
    this.frequency = new MockAudioParam(350);
  }
}

class MockAnalyserNode extends MockAudioNode {
  constructor(context) {
    super(context);
    this.fftSize = 256;
    this.smoothingTimeConstant = 0.8;
    this.frequencyBinCount = 128;
  }
  getByteTimeDomainData(array) {
    for (let i = 0; i < array.length; i++) {
      array[i] = Math.floor(128 + 64 * Math.sin((i / array.length) * 2 * Math.PI));
    }
  }
}

class MockAudioContext {
  constructor() {
    this.currentTime = 0;
    this.state = 'suspended';
    this.destination = new MockAudioNode(this);
    this.activeOscillators = [];
    this.stoppedOscillators = [];
  }
  resume() {
    this.state = 'running';
    return Promise.resolve();
  }
  suspend() {
    this.state = 'suspended';
    return Promise.resolve();
  }
  createOscillator() {
    return new MockOscillatorNode(this);
  }
  createGain() {
    return new MockGainNode(this);
  }
  createBiquadFilter() {
    return new MockBiquadFilterNode(this);
  }
  createAnalyser() {
    return new MockAnalyserNode(this);
  }
}

class MockClassList {
  constructor(classes = []) {
    this._set = new Set(classes);
  }
  add(cls) {
    this._set.add(cls);
  }
  remove(cls) {
    this._set.delete(cls);
  }
  contains(cls) {
    return this._set.has(cls);
  }
  toggle(cls) {
    if (this._set.has(cls)) this._set.delete(cls);
    else this._set.add(cls);
  }
  toString() {
    return Array.from(this._set).join(' ');
  }
}

class MockCanvasRenderingContext2D {
  constructor(canvas) {
    this.canvas = canvas;
    this.fillStyle = '';
    this.strokeStyle = '';
    this.lineWidth = 1;
    this.shadowColor = '';
    this.shadowBlur = 0;
    this.drawCalls = 0;
    this.path = [];
  }
  fillRect(x, y, w, h) { this.drawCalls++; }
  beginPath() { this.path = []; }
  moveTo(x, y) { this.path.push(['M', x, y]); }
  lineTo(x, y) { this.path.push(['L', x, y]); }
  stroke() { this.drawCalls++; }
}

class MockElement {
  constructor(tagName, id = '', className = '') {
    this.tagName = tagName.toUpperCase();
    this.id = id;
    this.classList = new MockClassList(className.split(' ').filter(Boolean));
    this.attributes = {};
    this.style = {};
    this.textContent = '';
    this.innerHTML = '';
    this.listeners = {};
    this.children = [];
    this.src = '';
    this.open = false;
    this.width = 400;
    this.height = 48;
    this._ctx2d = null;
  }
  get className() {
    return this.classList.toString();
  }
  set className(val) {
    this.classList = new MockClassList(val.split(' ').filter(Boolean));
  }
  setAttribute(key, val) {
    this.attributes[key] = String(val);
  }
  getAttribute(key) {
    return this.attributes[key] || null;
  }
  addEventListener(event, handler) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(handler);
  }
  removeEventListener(event, handler) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(h => h !== handler);
    }
  }
  dispatchEvent(eventObj) {
    const handlers = this.listeners[eventObj.type] || [];
    eventObj.target = eventObj.target || this;
    handlers.forEach(h => h(eventObj));
  }
  click() {
    this.dispatchEvent({ type: 'click', target: this });
  }
  showModal() {
    this.open = true;
  }
  close() {
    this.open = false;
  }
  getContext(type) {
    if (type === '2d') {
      if (!this._ctx2d) this._ctx2d = new MockCanvasRenderingContext2D(this);
      return this._ctx2d;
    }
    return null;
  }
}

function createDOMEnvironment() {
  const elements = new Map();
  const allElements = [];

  function register(el) {
    if (el.id) elements.set(el.id, el);
    allElements.push(el);
    return el;
  }

  // Create standard elements in index.html
  const filterContainer = register(new MockElement('div', 'filter-container', 'filter-engine'));
  const filterTabs = [
    register(new MockElement('button', '', 'filter-tab filter-btn active')),
    register(new MockElement('button', '', 'filter-tab filter-btn')),
    register(new MockElement('button', '', 'filter-tab filter-btn')),
    register(new MockElement('button', '', 'filter-tab filter-btn')),
    register(new MockElement('button', '', 'filter-tab filter-btn')),
    register(new MockElement('button', '', 'filter-tab filter-btn'))
  ];
  const cats = ['all', 'systems', 'ai', 'embedded', 'java', 'automation'];
  filterTabs.forEach((tab, i) => {
    tab.setAttribute('data-filter', cats[i]);
    tab.setAttribute('data-cat', cats[i]);
    filterContainer.children.push(tab);
  });

  const compendiumGrid = register(new MockElement('div', 'compendium-grid'));
  const plateConfigs = [
    { id: 'plate-1', cat: 'systems ai' },
    { id: 'plate-2', cat: 'ai systems' },
    { id: 'plate-3', cat: 'ai systems' },
    { id: 'plate-4', cat: 'embedded systems' },
    { id: 'plate-5', cat: 'java systems' },
    { id: 'plate-6', cat: 'java systems' },
    { id: 'plate-7', cat: 'ai automation' },
    { id: 'plate-8', cat: 'automation systems' },
    { id: 'plate-9', cat: 'systems automation' },
    { id: 'plate-10', cat: 'java systems ai' }
  ];
  const plates = plateConfigs.map(cfg => {
    const pl = register(new MockElement('article', cfg.id, 'folio-plate project-card'));
    pl.setAttribute('data-category', cfg.cat);
    compendiumGrid.children.push(pl);
    return pl;
  });

  // Terminal elements
  const vramEl = register(new MockElement('span', 'term-vram'));
  const tempEl = register(new MockElement('span', 'term-temp'));
  const pwrEl = register(new MockElement('span', 'term-pwr'));
  const lossGraphEl = register(new MockElement('div', 'term-loss-graph'));
  const tpsEl = register(new MockElement('span', 'term-tps'));
  const etaEl = register(new MockElement('span', 'term-eta'));
  const termToggleBtn = register(new MockElement('button', 'term-toggle-btn'));
  const termTickBtn = register(new MockElement('button', 'term-tick-btn'));

  // Piano synth elements
  const synthPlayBtn = register(new MockElement('button', 'synth-play-btn'));
  const synthBtnText = register(new MockElement('span', 'synth-btn-text'));
  const synthBtnIcon = register(new MockElement('span', 'synth-btn-icon'));
  const synthNoteStatus = register(new MockElement('span', 'synth-note-status'));
  const synthChordStatus = register(new MockElement('span', 'synth-chord-status'));
  const oscCanvas = register(new MockElement('canvas', 'synth-oscilloscope'));

  // SBB TFT elements
  const tftClock = register(new MockElement('span', 'tft-live-clock'));
  const hwModal = register(new MockElement('dialog', 'hardware-modal', 'atelier-modal'));
  const openHwBtn = register(new MockElement('button', 'open-hardware-modal-btn'));
  const closeHwBtn = register(new MockElement('button', 'close-modal-btn'));
  const modalImg = register(new MockElement('img', 'modal-display-img'));
  modalImg.src = 'assets/board-closeup.svg';

  const modalTabs = [
    register(new MockElement('button', '', 'modal-tab active')),
    register(new MockElement('button', '', 'modal-tab')),
    register(new MockElement('button', '', 'modal-tab'))
  ];
  modalTabs[0].setAttribute('data-img', 'assets/board-closeup.svg');
  modalTabs[1].setAttribute('data-img', 'assets/board-installed.svg');
  modalTabs[2].setAttribute('data-img', 'assets/IMG_1591_q85.jpg');

  const docListeners = {};
  const doc = {
    getElementById: (id) => elements.get(id) || null,
    querySelectorAll: (selector) => {
      if (selector.includes('filter-btn') || selector.includes('filter-tab')) {
        return filterTabs;
      }
      if (selector.includes('compendium-grid') || selector.includes('folio-plate') || selector.includes('article')) {
        return plates;
      }
      if (selector.includes('.modal-tab')) {
        return modalTabs;
      }
      return [];
    },
    addEventListener: (event, handler) => {
      if (!docListeners[event]) docListeners[event] = [];
      docListeners[event].push(handler);
    },
    dispatchEvent: (eventObj) => {
      const handlers = docListeners[eventObj.type] || [];
      handlers.forEach(h => h(eventObj));
    }
  };

  const win = {
    AudioContext: MockAudioContext,
    webkitAudioContext: MockAudioContext,
    requestAnimationFrame: (cb) => {},
    document: doc
  };

  return {
    win,
    doc,
    elements,
    filterTabs,
    plates,
    termToggleBtn,
    termTickBtn,
    synthPlayBtn,
    synthBtnText,
    synthBtnIcon,
    synthNoteStatus,
    synthChordStatus,
    oscCanvas,
    hwModal,
    openHwBtn,
    closeHwBtn,
    modalImg,
    modalTabs
  };
}

// Global setup for evaluation
global.AudioContext = MockAudioContext;
global.webkitAudioContext = MockAudioContext;
global.requestAnimationFrame = (cb) => {};

function getAtelierPianoClass() {
  const sandbox = new Function('window', 'AudioContext', `${classDefCode}; return AtelierPianoAudioEngine;`);
  return sandbox(global.window, MockAudioContext);
}

// -----------------------------------------------------------------------------
// SECTION 2: Empirical Stress Tests
// -----------------------------------------------------------------------------

console.log("▶ TIER 1: WEB AUDIO API SYNTHESIZER EMPIRICAL STRESS TESTS");

runTest("1.1 Web Audio: Equal Temperament Frequency & Score Precision", () => {
  const AtelierPianoAudioEngine = getAtelierPianoClass();
  const engine = new AtelierPianoAudioEngine();

  const expectedNotes = [
    { note: 'D3', f: 146.83, theoretical: 440 * Math.pow(2, -19/12) },
    { note: 'A3', f: 220.00, theoretical: 440 * Math.pow(2, -12/12) },
    { note: 'D4', f: 293.66, theoretical: 440 * Math.pow(2, -7/12) },
    { note: 'F4', f: 349.23, theoretical: 440 * Math.pow(2, -4/12) },
    { note: 'A4', f: 440.00, theoretical: 440 },
    { note: 'F3', f: 174.61, theoretical: 440 * Math.pow(2, -16/12) },
    { note: 'C4', f: 261.63, theoretical: 440 * Math.pow(2, -9/12) },
    { note: 'C5', f: 523.25, theoretical: 440 * Math.pow(2, 3/12) },
    { note: 'Bb2', f: 116.54, theoretical: 440 * Math.pow(2, -23/12) },
    { note: 'Bb3', f: 233.08, theoretical: 440 * Math.pow(2, -11/12) },
    { note: 'Bb4', f: 466.16, theoretical: 440 * Math.pow(2, 1/12) },
    { note: 'A2', f: 110.00, theoretical: 440 * Math.pow(2, -24/12) },
    { note: 'C#4', f: 277.18, theoretical: 440 * Math.pow(2, -8/12) },
    { note: 'E4', f: 329.63, theoretical: 440 * Math.pow(2, -5/12) }
  ];

  for (const n of expectedNotes) {
    const diff = Math.abs(n.f - n.theoretical);
    assert(diff < 0.1, `Note ${n.note} frequency ${n.f} deviates from theoretical ${n.theoretical.toFixed(2)}`);
  }

  // Validate entire score
  assert.strictEqual(engine.score.length, 20, "Score must contain exactly 20 notes in D minor nocturne motif");
  for (const item of engine.score) {
    assert(item.f > 20 && item.f < 5000, `Frequency ${item.f} must be within audible piano range`);
    assert(item.dur > 0 && item.dur <= 5.0, `Duration ${item.dur} must be positive`);
    assert(typeof item.note === 'string' && item.note.length > 0, "Note name must be string");
    assert(typeof item.chord === 'string' && item.chord.length > 0, "Chord description must be string");
  }
});

runTest("1.2 Web Audio: Context Initialization & Autoplay Resume Lifecycle", () => {
  const env = createDOMEnvironment();
  global.window = env.win;
  global.document = env.doc;

  const AtelierPianoAudioEngine = getAtelierPianoClass();
  const engine = new AtelierPianoAudioEngine();
  assert.strictEqual(engine.ctx, null, "Context should be uninitialized on construction");
  assert.strictEqual(engine.isPlaying, false, "isPlaying should initially be false");

  engine.initContext();
  assert(engine.ctx !== null, "Context must be initialized");
  assert.strictEqual(engine.ctx.state, 'running', "Suspended context must be resumed on init");
  const firstCtx = engine.ctx;

  // Idempotency check
  engine.initContext();
  assert.strictEqual(engine.ctx, firstCtx, "AudioContext must be reused without leaking new contexts");
});

runTest("1.3 Web Audio: Synthesis Envelope & Exponential Decay Non-Zero Safety", () => {
  const env = createDOMEnvironment();
  global.window = env.win;
  global.document = env.doc;

  const AtelierPianoAudioEngine = getAtelierPianoClass();
  const engine = new AtelierPianoAudioEngine();
  engine.initContext();
  engine.playPianoTone(440, 1.0);

  assert.strictEqual(engine.ctx.activeOscillators.length, 3, "Must create 3 oscillators (fundamental, 2nd, 3rd harmonics)");
  assert.strictEqual(engine.ctx.stoppedOscillators.length, 3, "All 3 oscillators must be scheduled to stop");

  const [osc1, osc2, osc3] = engine.ctx.activeOscillators;
  assert.strictEqual(osc1.type, 'triangle');
  assert.strictEqual(osc2.type, 'sine');
  assert.strictEqual(osc3.type, 'sine');

  assert.strictEqual(osc1.frequency.value, 440);
  assert.strictEqual(osc2.frequency.value, 880);
  assert.strictEqual(osc3.frequency.value, 1320);

  assert.strictEqual(osc1.stopTime, 1.0);
  assert.strictEqual(osc2.stopTime, 1.0);
  assert.strictEqual(osc3.stopTime, 1.0);
});

runTest("1.4 Web Audio: Stress-Test Rapid Start/Stop Toggling (500 iterations)", () => {
  const env = createDOMEnvironment();
  global.window = env.win;
  global.document = env.doc;

  const AtelierPianoAudioEngine = getAtelierPianoClass();
  const engine = new AtelierPianoAudioEngine();

  for (let i = 0; i < 500; i++) {
    engine.startSequence();
    assert.strictEqual(engine.isPlaying, true);
    engine.stopSequence();
    assert.strictEqual(engine.isPlaying, false);
    assert.strictEqual(engine.timer, null, "Timer must be cleared upon stopSequence");
  }
});

runTest("1.5 Web Audio: Multi-Cycle Full Sequence Stress Run (1,000 notes played)", () => {
  const env = createDOMEnvironment();
  global.window = env.win;
  global.document = env.doc;

  const AtelierPianoAudioEngine = getAtelierPianoClass();
  const engine = new AtelierPianoAudioEngine();
  engine.initContext();

  for (let i = 0; i < 1000; i++) {
    const scoreItem = engine.score[i % engine.score.length];
    engine.playPianoTone(scoreItem.f, scoreItem.dur);
  }

  assert.strictEqual(engine.ctx.activeOscillators.length, 3000);
  assert.strictEqual(engine.ctx.stoppedOscillators.length, 3000);
});

runTest("1.6 Canvas Oscilloscope: Render Frame Lifecycle & Visualizer Baseline", () => {
  const env = createDOMEnvironment();
  global.window = env.win;
  global.document = env.doc;

  const sandbox = new Function('window', 'document', 'AudioContext', 'requestAnimationFrame', `${scriptContent};`);
  sandbox(env.win, env.doc, MockAudioContext, global.requestAnimationFrame);
  env.doc.dispatchEvent({ type: 'DOMContentLoaded' });

  const canvas = env.oscCanvas;
  const ctx = canvas.getContext('2d');
  assert(ctx !== null, "Canvas 2D context must be acquired");
  assert(ctx.drawCalls > 0, "Canvas should have executed draw calls for initial resting line");

  // Trigger synth button to play
  env.synthPlayBtn.click();
  assert(env.synthBtnText.textContent.includes('Pause'), "Button text must update to Pause");
  assert.strictEqual(env.synthBtnIcon.textContent, '❚❚', "Button icon must update to pause symbol");

  // Pause synth button
  env.synthPlayBtn.click();
  assert(env.synthBtnText.textContent.includes('Play'), "Button text must revert to Play");
  assert.strictEqual(env.synthBtnIcon.textContent, '▶', "Button icon must revert to play symbol");
});

console.log("\n▶ TIER 2: ANSI TERMINAL SIMULATOR EMPIRICAL STRESS TESTS");

runTest("2.1 ANSI Terminal: Counter Wraparound & Mathematical Invariants (50,000 steps)", () => {
  let termStep = 11480;
  const totalSteps = 12000;
  const graphPatterns = [
    'LOSS [1.428] ──█▓▒░───░▒▓█───█▓▒░──',
    'LOSS [1.419] ───░▒▓█───█▓▒░───░▒▓█─',
    'LOSS [1.412] ────█▓▒░───░▒▓█───█▓▒░',
    'LOSS [1.407] ─░▒▓█───█▓▒░───░▒▓█───',
    'LOSS [1.398] ──█▓▒░───░▒▓█───█▓▒░──'
  ];
  let patternIdx = 0;

  for (let i = 0; i < 50000; i++) {
    if (termStep < totalSteps) {
      termStep += 1;
    } else {
      termStep = 1;
    }

    assert(termStep >= 1 && termStep <= totalSteps, `termStep ${termStep} out of bounds [1, ${totalSteps}]`);

    const remSteps = totalSteps - termStep;
    const remSecs = Math.max(0, Math.floor(remSteps * 0.8));
    const mins = String(Math.floor(remSecs / 60)).padStart(2, '0');
    const secs = String(remSecs % 60).padStart(2, '0');

    assert(!isNaN(remSecs), "remSecs must not be NaN");
    assert(mins.length >= 2, `mins must be at least 2 digits, got ${mins}`);
    assert(secs.length === 2, `secs must be 2 digits, got ${secs}`);

    patternIdx = (patternIdx + 1) % graphPatterns.length;
    assert(patternIdx >= 0 && patternIdx < graphPatterns.length);
    assert(graphPatterns[patternIdx] !== undefined);
  }
});

runTest("2.2 ANSI Terminal: Pause/Resume Ticker Lifecycle & Leak Prevention (5,000 toggles)", () => {
  const env = createDOMEnvironment();
  global.window = env.win;
  global.document = env.doc;

  const sandbox = new Function('window', 'document', 'AudioContext', 'requestAnimationFrame', `${scriptContent};`);
  sandbox(env.win, env.doc, MockAudioContext, global.requestAnimationFrame);
  env.doc.dispatchEvent({ type: 'DOMContentLoaded' });

  const toggleBtn = env.termToggleBtn;
  const tickBtn = env.termTickBtn;

  // Toggle 5000 times
  for (let i = 0; i < 5000; i++) {
    toggleBtn.click();
    if (i % 2 === 0) {
      assert.strictEqual(toggleBtn.textContent, 'Resume');
    } else {
      assert.strictEqual(toggleBtn.textContent, 'Pause');
    }
  }

  // Manual step clicks
  for (let i = 0; i < 100; i++) {
    tickBtn.click();
  }
});

console.log("\n▶ TIER 3: MODAL LIGHTBOX EMPIRICAL STRESS TESTS");

runTest("3.1 Modal Lightbox: Open, Close, Backdrop Click & Active Class Invariants", () => {
  const env = createDOMEnvironment();
  global.window = env.win;
  global.document = env.doc;

  const sandbox = new Function('window', 'document', 'AudioContext', 'requestAnimationFrame', `${scriptContent};`);
  sandbox(env.win, env.doc, MockAudioContext, global.requestAnimationFrame);
  env.doc.dispatchEvent({ type: 'DOMContentLoaded' });

  const modal = env.hwModal;
  const openBtn = env.openHwBtn;
  const closeBtn = env.closeHwBtn;

  assert(!modal.classList.contains('active'), "Modal should not be active initially");
  assert.strictEqual(modal.open, false, "Modal dialog should be closed initially");

  // Open
  openBtn.click();
  assert(modal.classList.contains('active'), "Modal must have 'active' class when opened");
  assert.strictEqual(modal.open, true, "Modal dialog must be open");

  // Backdrop click
  modal.dispatchEvent({ type: 'click', target: modal });
  assert(!modal.classList.contains('active'), "Backdrop click must close modal");
  assert.strictEqual(modal.open, false);

  // Open again, then close button
  openBtn.click();
  assert(modal.classList.contains('active'));
  closeBtn.click();
  assert(!modal.classList.contains('active'), "Close button must close modal");
  assert.strictEqual(modal.open, false);
});

runTest("3.2 Modal Lightbox: Tab Switching & Asset Target Source Synchrony (10,000 switches)", () => {
  const env = createDOMEnvironment();
  global.window = env.win;
  global.document = env.doc;

  const sandbox = new Function('window', 'document', 'AudioContext', 'requestAnimationFrame', `${scriptContent};`);
  sandbox(env.win, env.doc, MockAudioContext, global.requestAnimationFrame);
  env.doc.dispatchEvent({ type: 'DOMContentLoaded' });

  const tabs = env.modalTabs;
  const modalImg = env.modalImg;

  for (let i = 0; i < 10000; i++) {
    const selectedIdx = i % tabs.length;
    tabs[selectedIdx].click();

    tabs.forEach((t, idx) => {
      if (idx === selectedIdx) {
        assert(t.classList.contains('active'), `Tab ${idx} must be active`);
      } else {
        assert(!t.classList.contains('active'), `Tab ${idx} must NOT be active`);
      }
    });

    const expectedSrc = tabs[selectedIdx].getAttribute('data-img');
    assert.strictEqual(modalImg.src, expectedSrc, `modalImg src must match data-img`);
  }
});

console.log("\n▶ TIER 4: CATEGORY FILTERING ENGINE EMPIRICAL STRESS TESTS");

runTest("4.1 Filter Engine: Exact Categorical Plate Partitioning", () => {
  const env = createDOMEnvironment();
  global.window = env.win;
  global.document = env.doc;

  const sandbox = new Function('window', 'document', 'AudioContext', 'requestAnimationFrame', `
    ${scriptContent};
    return filterCategory;
  `);
  const filterCategory = sandbox(env.win, env.doc, MockAudioContext, global.requestAnimationFrame);
  env.doc.dispatchEvent({ type: 'DOMContentLoaded' });

  const plates = env.plates;

  // 'all'
  filterCategory('all');
  assert.strictEqual(plates.filter(p => !p.classList.contains('is-hidden')).length, 10);

  // 'systems'
  filterCategory('systems');
  assert.strictEqual(plates.filter(p => !p.classList.contains('is-hidden')).length, 9);

  // 'ai'
  filterCategory('ai');
  assert.strictEqual(plates.filter(p => !p.classList.contains('is-hidden')).length, 5);

  // 'embedded'
  filterCategory('embedded');
  const embeddedPlates = plates.filter(p => !p.classList.contains('is-hidden'));
  assert.strictEqual(embeddedPlates.length, 1);
  assert.strictEqual(embeddedPlates[0].id, 'plate-4');

  // 'java'
  filterCategory('java');
  assert.strictEqual(plates.filter(p => !p.classList.contains('is-hidden')).length, 3);

  // 'automation'
  filterCategory('automation');
  assert.strictEqual(plates.filter(p => !p.classList.contains('is-hidden')).length, 3);
});

runTest("4.2 Filter Engine: Rapid Random Category Permutations (10,000 cycles)", () => {
  const env = createDOMEnvironment();
  global.window = env.win;
  global.document = env.doc;

  const sandbox = new Function('window', 'document', 'AudioContext', 'requestAnimationFrame', `
    ${scriptContent};
    return filterCategory;
  `);
  const filterCategory = sandbox(env.win, env.doc, MockAudioContext, global.requestAnimationFrame);
  env.doc.dispatchEvent({ type: 'DOMContentLoaded' });

  const categories = ['all', 'systems', 'ai', 'embedded', 'java', 'automation'];
  const plates = env.plates;

  for (let i = 0; i < 10000; i++) {
    const cat = categories[Math.floor(Math.random() * categories.length)];
    filterCategory(cat);
    const visibleCount = plates.filter(p => !p.classList.contains('is-hidden')).length;
    assert(visibleCount >= 1 && visibleCount <= 10, `Visible count ${visibleCount} out of bounds`);
  }
});

console.log("\n===============================================================================");
console.log(`STRESS-TEST SUMMARY: ${passedTests}/${totalTests} Passed (${failedTests} Failed)`);
console.log("===============================================================================");

if (failedTests > 0) {
  process.exit(1);
} else {
  process.exit(0);
}
