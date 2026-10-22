import { backend } from './install';
import '../main';
import './tour.css';
import { startTour } from './tour';

// Let the app mount and load its snapshot before the first card appears.
setTimeout(() => startTour(() => backend.reset()), 700);
