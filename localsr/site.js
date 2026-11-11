/* Small enhancements on every page: the download for this computer, the current section in
   "On this page", and closing the small-screen menu. Everything works without it. */
(() => {
  'use strict';

  const NAMES = { macos: 'macOS', windows: 'Windows', linux: 'Linux' };
  // What to do once the file is downloaded, shown under the main download button.
  const HINTS = {
    macos: 'Open the DMG and drag LocalSR onto Applications.',
    windows: 'The installer is not signed yet: if SmartScreen warns, choose More info, then Run anyway.',
    linux: 'Make the AppImage executable (chmod +x), then run it.',
  };

  // Desktop operating system of this browser, or null on phones, tablets and anything unknown.
  function detectPlatform(nav) {
    const ua = nav.userAgent || '';
    const platform = (nav.userAgentData && nav.userAgentData.platform) || nav.platform || '';
    if (/Android|iPhone|iPad|iPod|CrOS/i.test(ua) || /Android|Chrome OS|iOS/i.test(platform)) return null;
    if (/Mac/i.test(platform) || /Macintosh/.test(ua)) return nav.maxTouchPoints > 1 ? null : 'macos';
    if (/Win/i.test(platform) || /Windows/.test(ua)) return 'windows';
    if (/Linux|X11/i.test(platform) || /Linux|X11/.test(ua)) return 'linux';
    return null;
  }

  function markDownloads(doc, os) {
    const panels = [...doc.querySelectorAll('.platform[data-platform]')];
    const mine = panels.find(panel => panel.dataset.platform === os);
    if (mine) {
      mine.classList.add('is-yours');
      const button = mine.querySelector('.download-link');
      if (button) button.classList.add('btn-primary');
    }
    const hero = doc.querySelector('[data-os-download]');
    const note = doc.querySelector('[data-os-note]');
    if (!hero) return;
    if (mine) {
      const file = mine.querySelector('.download-link');
      hero.textContent = `Download for ${NAMES[os]}`;
      hero.setAttribute('href', file ? file.getAttribute('href') : `download/#${os}`);
      const requirements = mine.querySelector('.platform-req');
      if (note) {
        note.textContent = `Free, ${mine.dataset.size || 'one download'}. ${requirements ? requirements.textContent : NAMES[os]}. ${HINTS[os]}`;
      }
    } else {
      hero.setAttribute('href', '#download');
      if (note) note.textContent = 'A free desktop app for macOS, Windows and Linux.';
    }
  }

  function followSections(doc, win) {
    const links = [...doc.querySelectorAll('nav[aria-label="On this page"] a[href^="#"]')];
    if (!links.length || typeof win.IntersectionObserver !== 'function') return;
    const byId = new Map(links.map(link => [decodeURIComponent(link.getAttribute('href').slice(1)), link]));
    const sections = [...byId.keys()].map(id => doc.getElementById(id)).filter(Boolean);
    const visible = new Set();
    const observer = new win.IntersectionObserver(entries => {
      entries.forEach(entry => (entry.isIntersecting ? visible.add(entry.target) : visible.delete(entry.target)));
      const first = sections.find(section => visible.has(section));
      if (!first) {
        // Above the first section nothing is current yet.
        if (sections[0] && sections[0].getBoundingClientRect().top > win.innerHeight * 0.45) links.forEach(link => link.removeAttribute('aria-current'));
        return;
      }
      links.forEach(link => link.removeAttribute('aria-current'));
      byId.get(first.id).setAttribute('aria-current', 'true');
    }, { rootMargin: '-80px 0px -55% 0px' });
    sections.forEach(section => observer.observe(section));
  }

  // Tables that stack into rows on phones lose their table role in some browsers; say it explicitly.
  function keepTableRoles(doc) {
    doc.querySelectorAll('table.stack').forEach(table => {
      table.setAttribute('role', 'table');
      table.querySelectorAll('thead, tbody').forEach(group => group.setAttribute('role', 'rowgroup'));
      table.querySelectorAll('tr').forEach(row => row.setAttribute('role', 'row'));
      table.querySelectorAll('thead th').forEach(cell => cell.setAttribute('role', 'columnheader'));
      table.querySelectorAll('tbody th').forEach(cell => cell.setAttribute('role', 'rowheader'));
      table.querySelectorAll('td').forEach(cell => cell.setAttribute('role', 'cell'));
    });
  }

  function closeMenus(doc) {
    const menus = [...doc.querySelectorAll('details.menu')];
    doc.addEventListener('click', event => {
      menus.forEach(menu => { if (menu.open && !menu.contains(event.target)) menu.open = false; });
    });
    doc.addEventListener('keydown', event => {
      if (event.key !== 'Escape') return;
      menus.forEach(menu => {
        if (!menu.open) return;
        menu.open = false;
        menu.querySelector('summary').focus();
      });
    });
  }

  if (typeof module !== 'undefined') module.exports = { detectPlatform, markDownloads };
  if (typeof document === 'undefined') return;
  markDownloads(document, detectPlatform(navigator));
  followSections(document, window);
  keepTableRoles(document);
  closeMenus(document);
})();
