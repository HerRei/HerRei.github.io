// Platform detection and the download for this computer (site.js), without a browser.
const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { detectPlatform, markDownloads } = require(path.join(__dirname, '..', 'site.js'));

test('desktop systems are recognised from the user agent or client hints', () => {
  const cases = [
    [{ userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/26.0 Safari/605.1.15', platform: 'MacIntel', maxTouchPoints: 0 }, 'macos'],
    [{ userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/142.0 Safari/537.36', platform: 'Win32' }, 'windows'],
    [{ userAgent: 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0', platform: 'Linux x86_64' }, 'linux'],
    [{ userAgent: 'Mozilla/5.0', userAgentData: { platform: 'Windows' } }, 'windows'],
  ];
  for (const [nav, expected] of cases) assert.equal(detectPlatform(nav), expected, nav.userAgent);
});

test('phones, tablets and Chromebooks get no installer', () => {
  const cases = [
    { userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 26_1 like Mac OS X) Mobile/15E148', platform: 'iPhone' },
    { userAgent: 'Mozilla/5.0 (Linux; Android 16; Pixel 9) Chrome/142.0 Mobile Safari/537.36', platform: 'Linux armv8l' },
    { userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Version/26.0 Safari/605.1.15', platform: 'MacIntel', maxTouchPoints: 5 },
    { userAgent: 'Mozilla/5.0 (X11; CrOS x86_64 16181.0.0) Chrome/142.0 Safari/537.36', platform: 'Linux x86_64' },
    { userAgent: '' },
  ];
  for (const nav of cases) assert.equal(detectPlatform(nav), null, nav.userAgent);
});

function fakePage() {
  const make = (extra = {}) => ({
    attrs: {}, classes: new Set(), textContent: '', dataset: {},
    classList: null, setAttribute(key, value) { this.attrs[key] = value; },
    querySelector() { return null; }, ...extra,
  });
  const panels = ['macos', 'windows', 'linux'].map(id => {
    const button = make();
    button.classList = { add: name => button.classes.add(name) };
    const requirements = make({ textContent: { macos: 'Apple Silicon · macOS 14+', windows: 'Windows 10 / 11 · x86-64', linux: 'Linux · x86-64' }[id] });
    button.attrs.href = `https://github.com/HerRei/local-upscale/releases/download/v0.3.0-beta/${id}.file`;
    button.getAttribute = key => button.attrs[key];
    const panel = make({ dataset: { platform: id, size: { macos: '419 MB', windows: '179 MB', linux: '631 MB' }[id] } });
    panel.classList = { add: name => panel.classes.add(name) };
    panel.querySelector = selector => ({ '.download-link': button, '.platform-req': requirements })[selector];
    return Object.assign(panel, { button });
  });
  const doc = { querySelectorAll: selector => (selector === '.platform[data-platform]' ? panels : []) };
  return { doc, panels };
}

test('the visitor’s platform gets the red button and the others stay neutral', () => {
  const { doc, panels } = fakePage();
  markDownloads(doc, 'windows');
  assert.ok(panels[1].classes.has('is-yours') && panels[1].button.classes.has('btn-primary'));
  assert.ok(!panels[0].button.classes.has('btn-primary') && !panels[2].button.classes.has('btn-primary'));
});

test('without a desktop platform no download is singled out', () => {
  const { doc, panels } = fakePage();
  markDownloads(doc, null);
  assert.ok(panels.every(panel => !panel.classes.has('is-yours') && !panel.button.classes.has('btn-primary')));
});
