// A scripted stand-in for the LocalSR host so the real interface runs in a
// browser. It answers the commands the tour needs and replays one recorded
// upscale (worker events captured from a real run, tiles cut from its output).
import { mockIPC, mockWindows } from '@tauri-apps/api/mocks';
import { emit } from '@tauri-apps/api/event';
import { demoSnapshot } from '../lib/demo';
import type { AppSnapshot, UiSettings, WorkerEnvelope } from '../lib/types';

interface RecordedEvent {
  t: number;
  type: string;
  data: Record<string, unknown>;
}

const MEDIA_ID = 'landskron';
const JOB_ID = 'demo-landskron';
const OUTPUT_PATH = '/Users/you/Pictures/LocalSR Results/landskron_localsr.png';
const GiB = 1024 ** 3;

export interface DemoAssets {
  source: string;
  result: string;
  run: string;
}

export interface DemoBackend {
  reset(): void;
}

function initialSnapshot(assets: DemoAssets): AppSnapshot {
  const snapshot = demoSnapshot();
  const installed = new Set(['span_photo_x4', 'realplksr_nomoswebphoto_x4']);
  for (const model of snapshot.catalog.models) model.installed = installed.has(model.model_id);
  snapshot.app_version = '0.2.1-beta';
  Object.assign(snapshot.settings, {
    task: 'upscale',
    content: 'photo',
    quality: 'quick',
    device_id: 'mps',
    output_scale: 4,
    output_directory: '/Users/you/Pictures/LocalSR Results',
  });
  snapshot.capabilities = {
    ...snapshot.capabilities,
    system_ram_total: 16 * GiB,
    system_ram_available: 8 * GiB,
    system_memory_pressure_percent: 30,
    system_memory_pressure_level: 'normal',
    devices: [
      {
        id: 'mps',
        type: 'mps',
        name: 'Apple GPU (Metal)',
        total_memory: 16 * GiB,
        free_memory: 8 * GiB,
        supports_fp16: true,
        is_integrated: true,
        recommended_tile_sizes: [128, 192, 256, 384],
      },
      {
        id: 'cpu',
        type: 'cpu',
        name: 'CPU',
        total_memory: 16 * GiB,
        free_memory: 8 * GiB,
        supports_fp16: false,
        is_integrated: true,
        recommended_tile_sizes: [64, 128, 192, 256],
      },
    ],
  } as AppSnapshot['capabilities'];
  snapshot.engine = {
    ...snapshot.engine,
    protocol_version: 1,
    minimum_protocol_version: 1,
    engine_id: 'macos-arm64-mps',
    engine_version: '0.2.1-beta',
    features: ['image', 'video', 'image_edit'],
    model_formats: ['safetensors', 'pth'],
    video_engines: ['seedvr2'],
  } as AppSnapshot['engine'];
  snapshot.media = [
    {
      id: MEDIA_ID,
      path: '/Users/you/Pictures/landskron.png',
      name: 'landskron.png',
      kind: 'image',
      width: 800,
      height: 450,
      frame_count: 1,
      fps: 0,
      duration_seconds: 0,
      preview_data_url: assets.source,
      probe_status: 'ready',
      error: '',
      selected: true,
    },
  ] as AppSnapshot['media'];
  Object.assign(snapshot.runtime, {
    worker: 'ready',
    status_title: 'Ready',
    status_detail: '',
  });
  return snapshot;
}

export function installDemoBackend(assets: DemoAssets): DemoBackend {
  let snapshot = initialSnapshot(assets);
  let recording: Promise<RecordedEvent[]> | undefined;
  let timers: ReturnType<typeof setTimeout>[] = [];

  const copy = (): AppSnapshot => structuredClone(snapshot);
  const changed = (): void => void emit('state-changed', null);
  const worker = (message: WorkerEnvelope): void => void emit('worker-message', message);

  function loadRun(): Promise<RecordedEvent[]> {
    recording ??= fetch(assets.run).then((response) => response.json());
    return recording;
  }

  function finish(): void {
    const job = snapshot.jobs.find((item) => item.id === JOB_ID);
    if (job) Object.assign(job, { status: 'completed', progress: 100, output_path: OUTPUT_PATH });
    Object.assign(snapshot.runtime, {
      active_job_id: '',
      progress: 100,
      status_title: 'Done',
      status_detail: 'Saved landskron_localsr.png · 3200 × 1800',
      last_output_path: OUTPUT_PATH,
      comparison_media_id: MEDIA_ID,
      comparison_output_path: OUTPUT_PATH,
      comparison_preview_data_url: assets.result,
    });
    changed();
  }

  async function start(): Promise<void> {
    const events = await loadRun();
    for (const timer of timers) clearTimeout(timer);
    snapshot.jobs = [
      {
        id: JOB_ID,
        media_id: MEDIA_ID,
        media_name: 'landskron.png',
        media_kind: 'image',
        status: 'running',
        progress: 0,
        output_path: '',
        error: '',
        created_at: Date.now() / 1000,
      },
    ] as AppSnapshot['jobs'];
    Object.assign(snapshot.runtime, {
      active_job_id: JOB_ID,
      progress: 0,
      comparison_media_id: '',
      comparison_output_path: '',
      comparison_preview_data_url: '',
      result_preview_data_url: '',
      status_title: 'Starting',
      status_detail: 'Loading the Best model on the Apple GPU',
    });
    changed();
    // A short pause stands in for loading the model, then the run replays at
    // its recorded speed.
    const lead = 600;
    timers = events.map((event) =>
      setTimeout(() => {
        worker({ type: event.type, data: event.data } as WorkerEnvelope);
        if (event.type === 'job_completed') finish();
      }, lead + event.t * 1000),
    );
  }

  mockWindows('main');
  mockIPC(
    async (command, args) => {
      const input = (args ?? {}) as Record<string, unknown>;
      switch (command) {
        case 'bootstrap':
        case 'get_snapshot':
          return copy();
        case 'save_settings':
          snapshot.settings = { ...snapshot.settings, ...(input.settings as Partial<UiSettings>) };
          return null;
        case 'select_media':
          for (const media of snapshot.media) media.selected = media.id === input.id;
          changed();
          return null;
        case 'start_jobs':
          void start();
          return null;
        case 'cancel_jobs':
          for (const timer of timers) clearTimeout(timer);
          snapshot = initialSnapshot(assets);
          changed();
          return null;
        case 'request_image_comparison':
          if (snapshot.jobs.some((job) => job.status === 'completed')) finish();
          return null;
        case 'take_launch_intents':
        case 'detect_external_ffmpeg':
          return [];
        case 'update_status':
        case 'check_update':
          return {
            configured: false,
            managed_by_store: false,
            channel: 'beta',
            target: '',
            stage: 'idle',
            version: '',
            notes: '',
            size: 0,
            downloaded: 0,
            message: '',
            settings_recovery: false,
          };
        case 'integration_status':
          return { platform: 'macos', installed: false, summary: '', command_name: 'localsr' };
        case 'diagnostic_summary':
          return 'LocalSR browser demo: a recorded run, no inference engine.';
        default:
          // Opening files, folders and dialogs has no meaning in the browser.
          return null;
      }
    },
    { shouldMockEvents: true },
  );

  return {
    reset() {
      for (const timer of timers) clearTimeout(timer);
      snapshot = initialSnapshot(assets);
      changed();
    },
  };
}
