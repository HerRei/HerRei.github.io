// A scripted stand-in for the LocalSR host so the real interface runs in a
// browser. It answers every command the 0.6.0 interface calls and replays one
// recorded upscale (worker events captured from a real run, tiles cut from its output).
import { mockIPC, mockWindows } from '@tauri-apps/api/mocks';
import { emit } from '@tauri-apps/api/event';
import { demoSnapshot } from '../lib/demo';
import type { UpdateStatus } from '../lib/api';
import type {
  AppSnapshot,
  ComparePick,
  CompareSlot,
  ComparisonSlot,
  MediaResults,
  Recipe,
  UiSettings,
  WorkerEnvelope,
} from '../lib/types';

interface RecordedEvent {
  t: number;
  type: string;
  data: Record<string, unknown>;
}

const MEDIA_ID = 'landskron';
const JOB_ID = 'demo-landskron';
const OUTPUT_PATH = '/Users/you/Pictures/LocalSR Results/landskron_localsr.png';
const OUTPUT_NAME = 'landskron_localsr.png';
const MODEL_ID = 'realplksr_nomoswebphoto_x4';
const MODEL_LABEL = 'RealPLKSR ×4 NomosWebPhoto';
const INPUT_WIDTH = 800;
const INPUT_HEIGHT = 450;
const OUTPUT_WIDTH = 3200;
const OUTPUT_HEIGHT = 1800;
const GiB = 1024 ** 3;

export interface DemoAssets {
  source: string;
  result: string;
  run: string;
}

export interface DemoBackend {
  reset(): void;
}

function emptyUpdateStatus(): UpdateStatus {
  return {
    configured: false,
    managed_by_store: false,
    managed_by_package_manager: false,
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
}

function emptyMediaResults(mediaId: string): MediaResults {
  return {
    media_id: mediaId,
    results: [],
    total_count: 0,
    completed_count: 0,
    available_count: 0,
    default_result_id: null,
    next_before: null,
  };
}

function initialSnapshot(assets: DemoAssets): AppSnapshot {
  const snapshot = demoSnapshot();
  const installed = new Set(['span_photo_x4', MODEL_ID]);
  for (const model of snapshot.catalog.models) model.installed = installed.has(model.model_id);
  snapshot.app_version = '0.6.0-beta';
  Object.assign(snapshot.settings, {
    task: 'upscale',
    content: 'photo',
    quality: 'quick',
    device_id: 'mps',
    neural_engine: false,
    output_scale: 4,
    output_directory: '/Users/you/Pictures/LocalSR Results',
    privacy_choice_made: true,
    check_updates_at_launch: false,
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
    media: {
      system_codecs: {
        label: 'macOS',
        decode: ['h264', 'hevc'],
        encode: ['h264', 'hevc', 'prores'],
        containers: ['mp4', 'mov'],
      },
      image_output: ['heic'],
      external_ffmpeg: { detected: [], candidates: [] },
    },
    gpu_suggestion: null,
    npu_hint: null,
  };
  snapshot.engine = {
    protocol_version: 1,
    minimum_protocol_version: 1,
    engine_id: 'macos-arm64-mps',
    engine_version: snapshot.app_version,
    features: ['image', 'video', 'image_edit', 'image_multi_fix', 'video_interpolation'],
    model_formats: ['safetensors', 'pth'],
    video_engines: ['seedvr2'],
  };
  snapshot.gpu_download_notice = null;
  snapshot.linux_menu_offer = false;
  snapshot.linux_menu_installed = false;
  snapshot.linux_menu_available = false;
  snapshot.engines = {
    supported: false,
    managed_by_store: false,
    configured: false,
    active_backend: 'mps',
    active_engine_id: 'macos-arm64-mps',
    bundled_backend: 'mps',
    installed: [],
    recommendation: { backend: '' },
    catalog: [],
    catalog_error: null,
    download: {
      stage: 'idle',
      backend: '',
      engine_id: '',
      downloaded: 0,
      total: 0,
      error: null,
    },
  };
  snapshot.media = [
    {
      id: MEDIA_ID,
      path: '/Users/you/Pictures/landskron.png',
      name: 'landskron.png',
      kind: 'image',
      width: INPUT_WIDTH,
      height: INPUT_HEIGHT,
      frame_count: 1,
      fps: 0,
      duration_seconds: 0,
      preview_data_url: assets.source,
      probe_status: 'ready',
      error: '',
      selected: true,
    },
  ];
  Object.assign(snapshot.runtime, {
    worker: 'ready',
    status_title: 'Ready',
    status_detail: '',
    comparison_pair: {
      media_id: '',
      generation: 0,
      showing: { target_id: '', preview_data_url: '' },
      against: { target_id: '', preview_data_url: '' },
    },
  });
  return snapshot;
}

export function installDemoBackend(assets: DemoAssets): DemoBackend {
  let snapshot = initialSnapshot(assets);
  let recording: Promise<RecordedEvent[]> | undefined;
  let timers: ReturnType<typeof setTimeout>[] = [];
  let compareGeneration = 0;
  let completedAt = 0;
  let cacheBytes = 0;

  const copy = (): AppSnapshot => structuredClone(snapshot);
  const changed = (): void => void emit('state-changed', null);
  const worker = (message: WorkerEnvelope): void => void emit('worker-message', message);

  function pairSlot(target: string): ComparisonSlot {
    if (target === 'original') {
      return {
        target_id: 'original',
        preview_data_url: '',
        width: INPUT_WIDTH,
        height: INPUT_HEIGHT,
      };
    }
    return {
      target_id: target,
      preview_data_url: assets.result,
      error: '',
      width: OUTPUT_WIDTH,
      height: OUTPUT_HEIGHT,
      preview_width: OUTPUT_WIDTH,
      preview_height: OUTPUT_HEIGHT,
    };
  }

  function mediaResults(): MediaResults {
    const done = snapshot.jobs.some((job) => job.id === JOB_ID && job.status === 'completed');
    if (!done) return emptyMediaResults(MEDIA_ID);
    return {
      media_id: MEDIA_ID,
      results: [
        {
          job_id: JOB_ID,
          completed_at: completedAt,
          status: 'completed',
          kind: 'upscale',
          output_path: OUTPUT_PATH,
          output_name: OUTPUT_NAME,
          size_bytes: 0,
          available: true,
          model_id: MODEL_ID,
          model_label: MODEL_LABEL,
          scale: 4,
          prompt: '',
          max_dimension: 0,
          stages: [],
          notes: '',
          elapsed_seconds: 5.08,
          device: 'mps',
          ui: { quality: 'Best', content: 'photo', recipe_name: '' },
        },
      ],
      total_count: 1,
      completed_count: 1,
      available_count: 1,
      default_result_id: JOB_ID,
      next_before: null,
    };
  }

  function compareSlots(picks: ComparePick[]): CompareSlot[] {
    return picks.map((pick) => {
      const isOutput = pick.kind === 'output';
      return {
        pick,
        media_kind: 'image',
        status: 'ready',
        preview_data_url: isOutput ? assets.result : assets.source,
        error: '',
        width: isOutput ? OUTPUT_WIDTH : INPUT_WIDTH,
        height: isOutput ? OUTPUT_HEIGHT : INPUT_HEIGHT,
        preview_width: isOutput ? OUTPUT_WIDTH : INPUT_WIDTH,
        preview_height: isOutput ? OUTPUT_HEIGHT : INPUT_HEIGHT,
      };
    });
  }

  function loadRun(): Promise<RecordedEvent[]> {
    recording ??= fetch(assets.run).then((response) => response.json());
    return recording;
  }

  function finish(): void {
    completedAt = Math.floor(Date.now() / 1000);
    const job = snapshot.jobs.find((item) => item.id === JOB_ID);
    if (job) {
      Object.assign(job, {
        status: 'completed',
        progress: 100,
        output_path: OUTPUT_PATH,
        elapsed_seconds: 5.08,
        model_id: MODEL_ID,
        model_label: MODEL_LABEL,
      });
    }
    Object.assign(snapshot.runtime, {
      active_job_id: '',
      progress: 100,
      status_title: 'Done',
      status_detail: 'Saved landskron_localsr.png · 3200 × 1800',
      last_output_path: OUTPUT_PATH,
      result_preview_data_url: assets.result,
      comparison_media_id: MEDIA_ID,
      comparison_output_path: OUTPUT_PATH,
      comparison_preview_data_url: assets.result,
      comparison_pair: {
        media_id: MEDIA_ID,
        generation: ++compareGeneration,
        showing: pairSlot(JOB_ID),
        against: pairSlot('original'),
      },
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
        model_id: MODEL_ID,
        model_label: MODEL_LABEL,
        status: 'running',
        progress: 0,
        output_path: '',
        error: '',
        created_at: Date.now() / 1000,
      },
    ];
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
        worker({ type: event.type, data: event.data });
        if (event.type === 'job_completed') finish();
      }, lead + event.t * 1000),
    );
  }

  function resetState(): void {
    for (const timer of timers) clearTimeout(timer);
    timers = [];
    completedAt = 0;
    snapshot = initialSnapshot(assets);
    changed();
  }

  mockWindows('main');
  mockIPC(
    async (command, args) => {
      const input = (args ?? {}) as Record<string, unknown>;
      switch (command) {
        case 'bootstrap':
        case 'get_snapshot':
          return copy();
        case 'cache_size':
          return cacheBytes;
        case 'clear_cache':
          cacheBytes = 0;
          return 0;
        case 'save_settings':
          snapshot.settings = { ...snapshot.settings, ...(input.settings as Partial<UiSettings>) };
          return null;
        case 'set_preference':
          (snapshot.settings as unknown as Record<string, unknown>)[String(input.name)] =
            input.value;
          changed();
          return null;
        case 'set_privacy_choice':
          Object.assign(snapshot.settings, {
            appearance: input.appearance as UiSettings['appearance'],
            colour_blind_palette: Boolean(input.colourBlindPalette),
            check_updates_at_launch: Boolean(input.checkAtLaunch),
            anonymous_update_count: Boolean(input.anonymousCount),
            crash_reports: Boolean(input.crashReports),
            privacy_choice_made: true,
          });
          return null;
        case 'set_model_directory':
          snapshot.settings.model_directory = String(input.path ?? '');
          changed();
          return null;
        case 'reset_model_directory':
          snapshot.settings.model_directory = '';
          changed();
          return null;
        case 'dismiss_gpu_download_notice':
          snapshot.settings.gpu_download_notice_dismissed = true;
          changed();
          return null;
        case 'dismiss_linux_menu_prompt':
          snapshot.settings.linux_menu_prompt_dismissed = true;
          snapshot.linux_menu_offer = false;
          changed();
          return null;
        case 'install_linux_menu':
          snapshot.linux_menu_installed = true;
          snapshot.linux_menu_offer = false;
          changed();
          return null;
        case 'uninstall_linux_menu':
          snapshot.linux_menu_installed = false;
          changed();
          return null;
        case 'refresh_capabilities':
          changed();
          return null;
        case 'refresh_engine_catalog':
          return snapshot.engines?.catalog ?? [];
        case 'checkpoint_consent':
          return Boolean(input.allow);
        case 'select_media':
          for (const media of snapshot.media) media.selected = media.id === input.id;
          changed();
          return null;
        case 'remove_media':
          snapshot.media = snapshot.media.filter((media) => media.id !== input.id);
          changed();
          return null;
        case 'clear_media':
          snapshot.media = [];
          changed();
          return null;
        case 'clear_results':
          snapshot.jobs = [];
          completedAt = 0;
          Object.assign(snapshot.runtime, {
            last_output_path: '',
            result_preview_data_url: '',
            comparison_media_id: '',
            comparison_output_path: '',
            comparison_preview_data_url: '',
            comparison_pair: {
              media_id: '',
              generation: ++compareGeneration,
              showing: { target_id: '', preview_data_url: '' },
              against: { target_id: '', preview_data_url: '' },
            },
          });
          changed();
          return null;
        case 'use_result_as_input':
          for (const media of snapshot.media) media.selected = media.id === MEDIA_ID;
          return MEDIA_ID;
        case 'start_jobs':
          void start();
          return null;
        case 'cancel_jobs':
        case 'cancel_jobs_for_media':
          resetState();
          return null;
        case 'list_all_media_results': {
          const entry = mediaResults();
          return entry.results.length ? [entry] : [];
        }
        case 'list_media_results':
          return input.mediaId === MEDIA_ID
            ? mediaResults()
            : emptyMediaResults(String(input.mediaId ?? ''));
        case 'request_image_comparison':
          if (input.showing) {
            snapshot.runtime.comparison_pair = {
              media_id: String(input.mediaId ?? MEDIA_ID),
              generation: ++compareGeneration,
              showing: pairSlot(String(input.showing)),
              against: pairSlot(String(input.against ?? 'original')),
            };
          } else if (snapshot.jobs.some((job) => job.status === 'completed')) {
            finish();
          }
          return null;
        case 'request_compare':
          snapshot.runtime.compare = {
            generation: ++compareGeneration,
            slots: compareSlots((input.picks as ComparePick[] | undefined) ?? []),
          };
          return null;
        case 'prepare_video_comparison':
          return {
            playback_note: '',
            original_path: '',
            enhanced_path: '',
            original_url: '',
            enhanced_url: '',
          };
        case 'save_recipe': {
          const recipe = input.recipe as Recipe | undefined;
          if (recipe) {
            const idx = snapshot.recipes.findIndex((item) => item.id === recipe.id);
            if (idx >= 0) snapshot.recipes[idx] = recipe;
            else snapshot.recipes.push(recipe);
            changed();
          }
          return null;
        }
        case 'delete_recipe':
          snapshot.recipes = snapshot.recipes.filter((recipe) => recipe.id !== input.id);
          changed();
          return null;
        case 'take_launch_intents':
        case 'detect_external_ffmpeg':
        case 'choose_media_files':
        case 'scan_media_folder':
        case 'start_model_trials':
        case 'estimate_model_trials':
        case 'list_crash_reports':
          return [];
        case 'update_status':
        case 'skip_update':
        case 'check_update':
        case 'check_update_at_launch':
          return emptyUpdateStatus();
        case 'integration_status':
        case 'install_integrations':
        case 'uninstall_integrations':
          return {
            platform: 'macos',
            installed: false,
            summary: 'File manager actions are available in the desktop app.',
            command_name: 'localsr',
          };
        case 'diagnostic_summary':
          return 'LocalSR browser demo: a recorded run, no inference engine.';
        default:
          // Opening files, folders, external tools and dialogs has no meaning in the browser.
          return null;
      }
    },
    { shouldMockEvents: true },
  );

  return {
    reset: resetState,
  };
}
