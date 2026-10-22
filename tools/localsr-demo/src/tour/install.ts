// Installs the scripted host before the app module runs (imports run in order).
import { installDemoBackend } from './backend';

try {
  localStorage.setItem('localsr.welcome.seen', '1');
} catch {
  // Private windows may refuse storage; the welcome note then shows once.
}

export const backend = installDemoBackend({
  source: 'media/landskron.webp',
  result: 'media/landskron-localsr.webp',
  run: 'media/landskron-run.json',
});
