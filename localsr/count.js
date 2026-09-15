// Anonymous visit count described on privacy/. Never affects the page.
(() => {
  try {
    const nav = navigator;
    if (nav.doNotTrack === '1' || nav.globalPrivacyControl === true) return;
    if (location.protocol !== 'https:' || location.hostname !== 'herrei.github.io') return;
    let referrer = '';
    try {
      const host = document.referrer ? new URL(document.referrer).hostname : '';
      if (host !== 'herrei.github.io') referrer = host;
    } catch {
      referrer = '';
    }
    const query = new URLSearchParams({ p: location.pathname.slice(0, 200), r: referrer });
    fetch(`https://macmini-ci.tail34a4e0.ts.net/hit?${query}`, {
      mode: 'no-cors',
      keepalive: true,
      credentials: 'omit',
      referrerPolicy: 'no-referrer',
      cache: 'no-store',
    }).catch(() => {});
  } catch {
    // Counting is best effort only.
  }
})();
