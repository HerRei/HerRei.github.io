"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { pathToFileURL } = require("node:url");
const { chromium } = require("playwright");
const AxeBuilder = require("@axe-core/playwright").default;

const root = path.resolve(__dirname, "..");
const url = process.env.PORTFOLIO_BASE_URL || pathToFileURL(path.join(root, "index.html")).href;
const output = process.env.PORTFOLIO_QA_DIR || path.join(os.tmpdir(), "herrei-portfolio-qa-results");
fs.mkdirSync(output, { recursive: true });

async function layout(page) {
  return page.evaluate(() => ({
    width: innerWidth,
    scrollWidth: document.documentElement.scrollWidth,
    overflowing: [...document.querySelectorAll("main h1, main h2, main h3, main p, main dt, main dd, main figcaption, nav, .entry, .address")]
      .filter(el => el.getBoundingClientRect().width && el.scrollWidth > el.clientWidth + 2)
      .map(el => ({ tag: el.tagName, class: el.className, text: el.textContent.trim().slice(0, 70) })),
    missingImages: [...document.images].filter(el => !el.complete || !el.naturalWidth).map(el => el.getAttribute("src")),
  }));
}

async function readWholePage(page) {
  await page.evaluate(async () => {
    await document.fonts.ready;
    document.querySelectorAll('img[loading="lazy"]').forEach(img => { img.loading = "eager"; });
    await Promise.all([...document.images].map(img => img.decode().catch(() => {})));
  });
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const report = { url, viewports: [], checks: [], errors: [] };
  try {
    for (const [width, height] of [[320, 568], [390, 844], [768, 1024], [1440, 1000], [1920, 1080]]) {
      const context = await browser.newContext({ viewport: { width, height }, reducedMotion: "reduce" });
      const page = await context.newPage();
      page.on("pageerror", err => report.errors.push(err.message));
      await page.goto(url, { waitUntil: "load" });
      await readWholePage(page);
      await page.screenshot({ path: path.join(output, `${width}-viewport.png`) });
      await page.screenshot({ path: path.join(output, `${width}-full.png`), fullPage: true });
      const state = await layout(page);
      report.viewports.push({ width, height, ...state });
      assert.ok(state.scrollWidth <= width + 1, `Horizontal overflow at ${width}px: ${JSON.stringify(state)}`);
      assert.deepEqual(state.overflowing, [], `Text or container overflow at ${width}px`);
      assert.deepEqual(state.missingImages, [], `Missing image at ${width}px`);
      assert.equal(await page.locator("h1").count(), 1);
      assert.equal(await page.locator("#entries > .entry").count(), 10);
      if (width === 390 || width === 1440) {
        const audit = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"]).analyze();
        fs.writeFileSync(path.join(output, `${width}-accessibility.json`), JSON.stringify(audit, null, 2));
        assert.deepEqual(audit.violations.map(v => ({ id: v.id, nodes: v.nodes.map(n => n.target) })), [], `Accessibility violations at ${width}px`);
      }
      await context.close();
    }
    report.checks.push("Responsive layout, text bounds, images, and automated accessibility");

    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: "reduce" });
    const page = await context.newPage();
    page.on("pageerror", err => report.errors.push(err.message));
    await page.goto(url);
    await readWholePage(page);
    const filters = await page.locator(".filter").evaluateAll(buttons => buttons.map(b => ({ category: b.dataset.cat, count: Number(b.querySelector(".tally").textContent) })));
    for (const filter of filters) {
      await page.locator(`.filter[data-cat="${filter.category}"]`).click();
      const visible = page.locator("#entries > .entry:visible");
      assert.equal(await visible.count(), filter.count, `Filter ${filter.category}`);
      assert.equal(await page.locator('.filter[aria-pressed="true"]').count(), 1);
      assert.equal(await page.locator("#project-count").innerText(), `${filter.count} of 10 projects`);
      if (filter.category !== "all") {
        const categories = await visible.evaluateAll(items => items.map(item => item.dataset.category.split(/\s+/)));
        assert.ok(categories.every(c => c.includes(filter.category)));
      }
    }
    await page.locator('.filter[data-cat="all"]').click();
    assert.equal(await page.locator("#entries > .entry:visible").count(), 10);
    report.checks.push("Every filter, announced count, category membership, and reset");

    await page.reload();
    await page.keyboard.press("Tab");
    assert.equal(await page.evaluate(() => document.activeElement.textContent.trim()), "Skip to projects");
    await page.keyboard.press("Enter");
    assert.equal(new URL(page.url()).hash, "#catalogue");
    await page.locator('.filter[data-cat="embedded"]').focus();
    await page.keyboard.press("Space");
    assert.equal(await page.locator("#entries > .entry:visible").count(), 1);
    await page.locator(".panel-study summary").click();
    assert.equal(await page.locator("#departure-panel").isVisible(), true);
    await page.locator('.filter[data-cat="all"]').click();
    report.checks.push("Skip link, keyboard filtering, and native disclosure");

    assert.equal(await page.locator("#term-toggle-btn").innerText(), "Resume");
    const before = await page.locator("#term-loss-graph").innerText();
    await page.locator("#term-tick-btn").click();
    assert.notEqual(await page.locator("#term-loss-graph").innerText(), before);
    await page.locator("#play-btn").click();
    assert.equal(await page.locator("#play-btn").innerText(), "Stop");
    assert.ok((await page.locator("#play-status").innerText()).includes("D3"));
    const canvas = await page.locator("canvas").evaluate(el => {
      const data = el.getContext("2d").getImageData(0, 0, el.width, el.height).data;
      return { width: el.width, height: el.height, painted: data.some((v, i) => i % 4 === 3 && v > 0) };
    });
    assert.ok(canvas.width > 0 && canvas.height > 0 && canvas.painted);
    await page.locator("#play-btn").click();
    report.checks.push("Reduced-motion telemetry, audio start/stop, and nonblank canvas");

    await page.locator('.filter[data-cat="embedded"]').click();
    await page.emulateMedia({ media: "print" });
    assert.equal(await page.locator("#entries > .entry:visible").count(), 10);
    await page.pdf({ path: path.join(output, "portfolio-print.pdf"), format: "A4" });
    await page.emulateMedia({ media: "screen" });
    await page.locator('.filter[data-cat="all"]').click();
    await page.evaluate(() => { document.documentElement.style.fontSize = "200%"; });
    for (const width of [1440, 390]) {
      await page.setViewportSize({ width, height: 1000 });
      const resized = await layout(page);
      assert.ok(resized.scrollWidth <= resized.width + 1, `Overflow with 200% text size at ${width}px`);
      assert.deepEqual(resized.overflowing, [], `Clipped content with 200% text size at ${width}px`);
      await page.screenshot({ path: path.join(output, `${width}-text-200-percent.png`), fullPage: true });
    }
    report.checks.push("Print includes filtered projects; text resizing to 200%");
    await context.close();

    const noJs = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
    const plain = await noJs.newPage();
    await plain.goto(url);
    assert.equal(await plain.locator("#entries > .entry:visible").count(), 10);
    assert.equal(await plain.locator(".filter:visible").count(), 0);
    assert.equal(await plain.locator("#play-btn:visible").count(), 0);
    assert.ok(await plain.locator('a[href="assets/lebenslauf.pdf"]').isVisible());
    await noJs.close();
    report.checks.push("Complete content and CV without JavaScript; inactive controls hidden");
    assert.deepEqual(report.errors, [], "Browser runtime errors");
    console.log(JSON.stringify(report, null, 2));
  } finally {
    fs.writeFileSync(path.join(output, "report.json"), JSON.stringify(report, null, 2));
    await browser.close();
  }
})().catch(err => { console.error(err); process.exitCode = 1; });
