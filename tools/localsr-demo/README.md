# LocalSR browser demo

`localsr/demo/` runs the real LocalSR interface in a browser with a guided
tour. There is no inference engine: a scripted stand-in for the desktop host
(`src/tour/backend.ts`, built on `@tauri-apps/api/mocks`) answers the
interface's commands and replays one recorded upscale.

## Rebuild the page

```sh
tools/localsr-demo/build.sh ~/Projects/LocalSR/LocalSR-qwen-edit v0.2.1-beta
python3 localsr/tools/validate_site.py
```

The script takes the interface from the given tag of
[HerRei/local-upscale](https://github.com/HerRei/local-upscale), adds the tour
files, builds with `vite.demo.config.ts` and installs the result with
`finish_page.py`. The app's own code is not changed. `localsr/demo/media/` is
kept as it is.

## The recorded run

`localsr/demo/media/provenance.json` records the photo, the crop, the model and
the checksums. To record a new run:

1. `python3 media-tools/make_media.py input <hero.jpg> <workdir>` writes the
   800 × 450 input.
2. `python3 media-tools/record_worker.py <packaged localsr-worker> <workdir>/landskron.png <model.pth> <workdir>/result.png <workdir>/events.jsonl 128`
   runs one upscale and records the worker's events.
3. `python3 media-tools/make_media.py replay <workdir>/events.jsonl <workdir>/result.png <workdir>/landskron.png localsr/demo/media`
   writes the files the demo loads.

Keep the input free of JPEG compression: with compressed input both photo
models turned the stars into smears.
