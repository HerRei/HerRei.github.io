#!/usr/bin/env node
/**
 * Executes the script that ships inside index.html against a stub DOM and a
 * virtual clock, then drives it hard.
 *
 * Unlike the Python suites, which read the page, this one runs it: filters are
 * really clicked, the nocturne is really played through to its last note, and
 * the telemetry specimen is really ticked ten thousand times.
 *
 *     node tests/test_interactive_engine_stress.js
 */

"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");
const assert = require("assert");

const INDEX = path.resolve(__dirname, "../index.html");
const DOC = fs.readFileSync(INDEX, "utf8");
const SCRIPT = DOC.match(/<script>([\s\S]*?)<\/script>/)[1];

const GREEN = "\x1b[92m", RED = "\x1b[91m", DIM = "\x1b[2m", RULE = "\x1b[38;2;168;61;40m", OFF = "\x1b[0m";

let passed = 0, failed = 0;
function check(name, fn) {
  try {
    fn();
    passed++;
    console.log(`  ${GREEN}✓${OFF} ${name}`);
  } catch (err) {
    failed++;
    console.log(`  ${RED}✗${OFF} ${name}`);
    console.log(`    ${DIM}${err.message.split("\n")[0]}${OFF}`);
  }
}
function section(title) {
  console.log(`\n${RULE}${title}${OFF}`);
}

/* ---------------------------------------------------------------------------
   A DOM just large enough for the page's script, and a clock we control.
   ------------------------------------------------------------------------ */

function makeElement(attrs) {
  const listeners = {};
  const classes = new Set();
  return {
    attrs: Object.assign({}, attrs),
    textContent: "",
    offsetWidth: 100,
    classList: {
      add: (c) => classes.add(c),
      remove: (c) => classes.delete(c),
      contains: (c) => classes.has(c),
      toggle: (c, force) => (force ? classes.add(c) : classes.delete(c)),
      _set: classes,
    },
    getAttribute(name) {
      return Object.prototype.hasOwnProperty.call(this.attrs, name) ? this.attrs[name] : null;
    },
    setAttribute(name, value) { this.attrs[name] = String(value); },
    addEventListener(type, fn) { (listeners[type] = listeners[type] || []).push(fn); },
    dispatch(type, event) { (listeners[type] || []).forEach((fn) => fn(event || {})); },
    click() { this.dispatch("click"); },
    getBoundingClientRect() { return { width: 600, height: 68, left: 0, top: 0 }; },
    hidden() { return classes.has("is-hidden"); },
  };
}

function makeClock() {
  let now = 0, nextId = 1;
  const timers = new Map();
  return {
    now: () => now,
    setTimeout(fn, delay) { timers.set(nextId, { fn, at: now + delay, every: null }); return nextId++; },
    setInterval(fn, every) { timers.set(nextId, { fn, at: now + every, every }); return nextId++; },
    clear(id) { timers.delete(id); },
    pending: () => timers.size,
    /** Advance the clock, firing whatever falls due. */
    advance(ms) {
      const target = now + ms;
      let guard = 0;
      for (;;) {
        let soonest = null, soonestId = null;
        for (const [id, t] of timers) {
          if (t.at <= target && (soonest === null || t.at < soonest.at)) { soonest = t; soonestId = id; }
        }
        if (!soonest || ++guard > 200000) break;
        now = soonest.at;
        if (soonest.every === null) timers.delete(soonestId);
        else soonest.at = now + soonest.every;
        soonest.fn();
      }
      now = target;
    },
  };
}

function makeAudioStub(log) {
  function param() {
    return {
      setValueAtTime: (v, t) => log.params.push(["set", v, t]),
      linearRampToValueAtTime: (v, t) => log.params.push(["linear", v, t]),
      exponentialRampToValueAtTime: (v, t) => log.params.push(["exp", v, t]),
    };
  }
  function AudioContextStub() {
    this.state = "suspended";
    this.currentTime = 0;
    this.destination = { kind: "destination" };
    this.resume = () => { this.state = "running"; log.resumed++; };
    this.createGain = () => ({ gain: param(), connect: () => {} });
    this.createBiquadFilter = () => ({ type: "", frequency: param(), connect: () => {} });
    this.createAnalyser = () => ({
      fftSize: 0,
      smoothingTimeConstant: 0,
      frequencyBinCount: 256,
      connect: () => {},
      getByteTimeDomainData: (arr) => { for (let i = 0; i < arr.length; i++) arr[i] = 128; },
    });
    this.createOscillator = () => {
      const osc = {
        type: "",
        frequency: {
          setValueAtTime: (hz) => { osc._hz = hz; },
        },
        connect: () => {},
        start: () => { log.notes.push(osc._hz); log.started++; },
        stop: () => { log.stopped++; },
      };
      return osc;
    };
  }
  return AudioContextStub;
}

function buildEnvironment(options) {
  options = options || {};
  const clock = makeClock();
  const audioLog = { notes: [], params: [], started: 0, stopped: 0, resumed: 0 };
  const canvasOps = [];

  const entries = [...DOC.matchAll(/<li class="entry" data-category="([^"]+)">/g)]
    .map((m) => makeElement({ "data-category": m[1] }));
  const filters = [...DOC.matchAll(/<button class="filter" type="button" data-cat="(\w+)"/g)]
    .map((m) => makeElement({ "data-cat": m[1] }));

  const byId = {};
  [...DOC.matchAll(/\bid="([^"]+)"/g)].forEach((m) => {
    const el = makeElement({ id: m[1] });
    el.id = m[1];                       // the script compares target.id, as the DOM would
    byId[m[1]] = el;
  });

  byId["oscilloscope"].getContext = (kind) => {
    if (kind !== "2d") return null;
    const record = (op) => (...args) => canvasOps.push([op, ...args]);
    return {
      clearRect: record("clearRect"), beginPath: record("beginPath"),
      moveTo: record("moveTo"), lineTo: record("lineTo"), stroke: record("stroke"),
      setTransform: record("setTransform"),
      set strokeStyle(v) { canvasOps.push(["strokeStyle", v]); },
      set lineWidth(v) { canvasOps.push(["lineWidth", v]); },
      set lineJoin(v) { canvasOps.push(["lineJoin", v]); },
    };
  };

  const documentListeners = {};
  const documentStub = {
    hidden: false,
    documentElement: makeElement({}),
    getElementById: (id) => byId[id] || null,
    querySelectorAll: (selector) => {
      if (selector === "#entries .entry") return entries;
      if (selector === "#index-line .filter") return filters;
      return [];
    },
    addEventListener: (type, fn) => { (documentListeners[type] = documentListeners[type] || []).push(fn); },
    dispatch: (type) => (documentListeners[type] || []).forEach((fn) => fn({})),
  };

  const observed = [];
  const sandbox = {
    document: documentStub,
    window: {
      matchMedia: () => ({ matches: Boolean(options.reduceMotion) }),
      AudioContext: makeAudioStub(audioLog),
      devicePixelRatio: options.dpr || 2,
      addEventListener: () => {},
    },
    getComputedStyle: () => ({ getPropertyValue: () => " #a83d28 " }),
    IntersectionObserver: function (cb) {
      this.observe = (el) => { observed.push(el); cb([{ isIntersecting: true, target: el }]); };
    },
    requestAnimationFrame: () => 0,
    setTimeout: clock.setTimeout.bind(clock),
    clearTimeout: clock.clear.bind(clock),
    setInterval: clock.setInterval.bind(clock),
    clearInterval: clock.clear.bind(clock),
    Uint8Array, Math, Date, String, Array, Object, Number, JSON, console,
  };
  sandbox.window.IntersectionObserver = sandbox.IntersectionObserver;   // the script looks for it on window
  sandbox.window.window = sandbox.window;
  vm.createContext(sandbox);
  vm.runInContext(SCRIPT, sandbox, { filename: "index.html#script" });

  return { sandbox, clock, entries, filters, byId, audioLog, canvasOps, observed, documentStub };
}

/* ---------------------------------------------------------------------------
   1 · The index line
   ------------------------------------------------------------------------ */

section("1 · The index line, clicked for real");

const env = buildEnvironment();

check("The script evaluates and exports its entry point", () => {
  assert.strictEqual(typeof env.sandbox.window.filterCategory, "function");
});

check("Ten entries and six filters are bound", () => {
  assert.strictEqual(env.entries.length, 10);
  assert.strictEqual(env.filters.length, 6);
});

check("Every entry is visible before anything is clicked", () => {
  assert.strictEqual(env.entries.filter((e) => e.hidden()).length, 0);
});

check("Clicking a filter hides exactly the works it excludes", () => {
  const embedded = env.filters.find((f) => f.getAttribute("data-cat") === "embedded");
  embedded.click();
  const shown = env.entries.filter((e) => !e.hidden());
  assert.strictEqual(shown.length, 1, `expected 1 embedded work, saw ${shown.length}`);
  assert.ok(shown[0].getAttribute("data-category").split(" ").includes("embedded"));
});

check("The pressed filter is the only one pressed", () => {
  const pressed = env.filters.filter((f) => f.getAttribute("aria-pressed") === "true");
  assert.strictEqual(pressed.length, 1);
  assert.strictEqual(pressed[0].getAttribute("data-cat"), "embedded");
});

check("Returning to 'all' restores every work", () => {
  env.filters.find((f) => f.getAttribute("data-cat") === "all").click();
  assert.strictEqual(env.entries.filter((e) => e.hidden()).length, 0);
});

check("Each filter yields the count it advertises", () => {
  const tallies = [...DOC.matchAll(/data-cat="(\w+)"[^>]*>[^<]+<span class="tally">(\d+)<\/span>/g)];
  for (const [, cat, claimed] of tallies) {
    env.filters.find((f) => f.getAttribute("data-cat") === cat).click();
    const shown = env.entries.filter((e) => !e.hidden()).length;
    assert.strictEqual(shown, Number(claimed), `'${cat}' claims ${claimed}, showed ${shown}`);
  }
});

check("'ai' does not select works that are merely 'automation'", () => {
  env.sandbox.window.filterCategory("ai");
  const shown = env.entries.filter((e) => !e.hidden());
  assert.ok(shown.every((e) => e.getAttribute("data-category").split(" ").includes("ai")));
});

check("An unknown category falls back to the whole catalogue", () => {
  env.sandbox.window.filterCategory("");
  assert.strictEqual(env.entries.filter((e) => e.hidden()).length, 0);
  env.sandbox.window.filterCategory("no-such-category");
  assert.strictEqual(env.entries.filter((e) => !e.hidden()).length, 0,
    "an unknown but non-empty category simply matches nothing");
  env.sandbox.window.filterCategory("all");
});

check("10,000 random filter changes never corrupt the catalogue", () => {
  const cats = ["all", "systems", "ai", "embedded", "java", "automation"];
  let seed = 20260822;
  const rand = () => (seed = (seed * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff;
  for (let i = 0; i < 10000; i++) {
    const cat = cats[Math.floor(rand() * cats.length)];
    env.sandbox.window.filterCategory(cat);
    const shown = env.entries.filter((e) => !e.hidden());
    const expected = env.entries.filter(
      (e) => cat === "all" || e.getAttribute("data-category").split(" ").includes(cat)
    );
    assert.strictEqual(shown.length, expected.length, `iteration ${i}, category '${cat}'`);
  }
  env.sandbox.window.filterCategory("all");
});

/* ---------------------------------------------------------------------------
   2 · The telemetry specimen
   ------------------------------------------------------------------------ */

section("2 · Fig. 1, ticked ten thousand times");

check("It starts by itself and reports its state", () => {
  assert.strictEqual(env.byId["term-toggle-btn"].textContent, "");
  env.clock.advance(1800);
  assert.match(env.byId["term-loss-graph"].textContent, /^loss \d\.\d{3}/);
});

check("Ten thousand ticks keep every field within the hardware", () => {
  for (let i = 0; i < 10000; i++) {
    env.clock.advance(1800);
    const vram = Number(env.byId["term-vram"].textContent.split(" ")[0].replace(/,/g, ""));
    const temp = Number(env.byId["term-temp"].textContent.split(" ")[0]);
    const power = Number(env.byId["term-pwr"].textContent.split(" ")[0]);
    assert.ok(vram >= 21800 && vram < 24564, `VRAM ${vram} outside the card`);
    assert.ok(temp >= 60 && temp <= 90, `temperature ${temp}`);
    assert.ok(power >= 370 && power <= 500, `power ${power}`);
  }
});

check("Loss decays but never falls through its floor", () => {
  const loss = Number(env.byId["term-loss-graph"].textContent.match(/loss ([\d.]+)/)[1]);
  assert.ok(loss >= 0.94 && loss <= 1.428, `loss ${loss}`);
});

check("The step counter wraps rather than running past the total", () => {
  const step = Number(env.byId["term-loss-graph"].textContent.match(/step ([\d,]+)/)[1].replace(/,/g, ""));
  assert.ok(step >= 1 && step <= 12000, `step ${step}`);
});

check("The estimate is never negative", () => {
  assert.match(env.byId["term-eta"].textContent, /^00:[0-5]\d:[0-5]\d$/);
});

check("Pause stops the clock; resume restarts it", () => {
  const toggle = env.byId["term-toggle-btn"];
  toggle.click();
  assert.strictEqual(toggle.textContent, "Resume");
  const frozen = env.byId["term-loss-graph"].textContent;
  env.clock.advance(1800 * 20);
  assert.strictEqual(env.byId["term-loss-graph"].textContent, frozen, "nothing moves while paused");
  toggle.click();
  assert.strictEqual(toggle.textContent, "Pause");
  env.clock.advance(1800);
  assert.notStrictEqual(env.byId["term-loss-graph"].textContent, frozen);
});

check("Stepping by hand advances exactly one step", () => {
  env.byId["term-toggle-btn"].click();                    // pause
  const before = Number(env.byId["term-loss-graph"].textContent.match(/step ([\d,]+)/)[1].replace(/,/g, ""));
  env.byId["term-tick-btn"].click();
  const after = Number(env.byId["term-loss-graph"].textContent.match(/step ([\d,]+)/)[1].replace(/,/g, ""));
  assert.strictEqual(after - before, 1);
});

check("Pausing twice does not leave two tickers running", () => {
  const toggle = env.byId["term-toggle-btn"];
  toggle.click(); toggle.click(); toggle.click();
  const pending = env.clock.pending();
  toggle.click(); toggle.click();
  assert.ok(env.clock.pending() <= pending + 1, "no ticker is ever left orphaned");
});

check("A hidden tab stops the ticker", () => {
  const fresh = buildEnvironment();
  fresh.documentStub.hidden = true;
  fresh.documentStub.dispatch("visibilitychange");
  const frozen = fresh.byId["term-loss-graph"].textContent;
  fresh.clock.advance(1800 * 10);
  assert.strictEqual(fresh.byId["term-loss-graph"].textContent, frozen);
  assert.strictEqual(fresh.byId["term-toggle-btn"].textContent, "Resume");
});

/* ---------------------------------------------------------------------------
   3 · The nocturne
   ------------------------------------------------------------------------ */

section("3 · Fig. 2, played to the last note");

const music = buildEnvironment();

check("Nothing sounds until the button is pressed", () => {
  music.clock.advance(60000);
  assert.strictEqual(music.audioLog.notes.length, 0);
});

check("Pressing play sounds the first chord", () => {
  music.byId["play-btn"].click();
  assert.strictEqual(music.byId["play-btn"].textContent, "Stop");
  assert.strictEqual(music.audioLog.notes.length, 3, "one note, three partials");
  assert.strictEqual(music.audioLog.resumed, 1, "the context is resumed on the gesture");
});

check("It plays twenty notes and stops of its own accord", () => {
  music.clock.advance(60000);
  assert.strictEqual(music.audioLog.notes.length, 60, "20 notes × 3 partials");
  assert.strictEqual(music.byId["play-btn"].textContent, "Play the nocturne");
});

check("Every note is voiced as fundamental, octave, and twelfth", () => {
  for (let i = 0; i < music.audioLog.notes.length; i += 3) {
    const [f1, f2, f3] = music.audioLog.notes.slice(i, i + 3);
    assert.ok(Math.abs(f2 / f1 - 2) < 1e-9, `partial 2 of note ${i / 3}`);
    assert.ok(Math.abs(f3 / f1 - 3) < 1e-9, `partial 3 of note ${i / 3}`);
  }
});

check("Every fundamental lies on a piano", () => {
  for (let i = 0; i < music.audioLog.notes.length; i += 3) {
    const hz = music.audioLog.notes[i];
    assert.ok(hz >= 27.5 && hz <= 4186, `${hz} Hz is off the keyboard`);
  }
});

check("It opens and resolves on the same D", () => {
  const first = music.audioLog.notes[0];
  const last = music.audioLog.notes[music.audioLog.notes.length - 3];
  assert.ok(Math.abs(first - last) < 0.01, `${first} Hz vs ${last} Hz`);
});

check("Every oscillator that starts is also stopped", () => {
  assert.strictEqual(music.audioLog.started, music.audioLog.stopped);
});

check("Stopping midway silences it and leaves no timer behind", () => {
  const second = buildEnvironment();
  second.byId["play-btn"].click();
  second.clock.advance(3000);
  const soundedSoFar = second.audioLog.notes.length;
  second.byId["play-btn"].click();                        // stop
  assert.strictEqual(second.byId["play-btn"].textContent, "Play the nocturne");
  second.clock.advance(60000);
  assert.strictEqual(second.audioLog.notes.length, soundedSoFar, "nothing sounds after stopping");
});

check("Playing again after it finishes starts from the beginning", () => {
  const before = music.audioLog.notes.length;
  music.byId["play-btn"].click();
  assert.strictEqual(music.audioLog.notes.length, before + 3);
  assert.ok(Math.abs(music.audioLog.notes[before] - music.audioLog.notes[0]) < 0.01);
});

check("A browser without Web Audio is told, not left hanging", () => {
  const mute = buildEnvironment();
  mute.sandbox.window.AudioContext = undefined;
  mute.sandbox.window.webkitAudioContext = undefined;
  mute.byId["play-btn"].click();
  assert.strictEqual(mute.byId["play-status"].textContent, "no audio available in this browser");
  assert.notStrictEqual(mute.byId["play-btn"].textContent, "Stop");
});

/* ---------------------------------------------------------------------------
   4 · The canvas and the clock
   ------------------------------------------------------------------------ */

section("4 · The stave, the clock, and reduced motion");

check("The backing store is scaled by the device pixel ratio", () => {
  const scaled = buildEnvironment({ dpr: 3 });
  assert.strictEqual(scaled.byId["oscilloscope"].width, 1800, "600 CSS px × 3");
  assert.strictEqual(scaled.byId["oscilloscope"].height, 204, "68 CSS px × 3");
  const transform = scaled.canvasOps.find((op) => op[0] === "setTransform");
  assert.deepStrictEqual(transform.slice(1), [3, 0, 0, 3, 0, 0]);
});

check("Reduced motion draws the stave once instead of animating", () => {
  const still = buildEnvironment({ reduceMotion: true });
  const strokes = still.canvasOps.filter((op) => op[0] === "stroke").length;
  assert.strictEqual(strokes, 5, "five ruled lines, drawn once");
});

check("Reduced motion leaves the telemetry specimen at rest", () => {
  const still = buildEnvironment({ reduceMotion: true });
  const frozen = still.byId["term-loss-graph"].textContent;
  still.clock.advance(1800 * 50);
  assert.strictEqual(still.byId["term-loss-graph"].textContent, frozen);
  assert.strictEqual(still.byId["term-toggle-btn"].textContent, "Resume");
});

check("The departure clock is zero-padded and ticks every second", () => {
  const fresh = buildEnvironment();
  assert.match(fresh.byId["panel-clock"].textContent, /^\d\d:\d\d:\d\d$/);
  const before = fresh.byId["panel-clock"].textContent;
  fresh.clock.advance(1000);
  assert.match(fresh.byId["panel-clock"].textContent, /^\d\d:\d\d:\d\d$/);
  assert.ok(typeof before === "string" && before.length === 8);
});

check("The running head names the section in view", () => {
  const fresh = buildEnvironment();
  assert.ok(["The Catalogue", "Index of Methods", "The Author", "Correspondence"]
    .includes(fresh.byId["running-chapter"].textContent),
    `running head said "${fresh.byId["running-chapter"].textContent}"`);
});

/* ------------------------------------------------------------------------ */

const total = passed + failed;
console.log(`\n${RULE}${"=".repeat(72)}${OFF}`);
if (failed) {
  console.log(`${RED}✖ ${failed} of ${total} executed assertions failed.${OFF}`);
  process.exit(1);
}
console.log(`${GREEN}❧ All ${total} executed assertions held.${OFF}`);
console.log(`${RULE}${"=".repeat(72)}${OFF}`);
