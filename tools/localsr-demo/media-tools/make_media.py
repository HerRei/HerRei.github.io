"""Prepare the browser demo's media.

  make_media.py input <hero.jpg> <workdir>
      Crops Landskron from the hero photo and writes the 800 x 450 input
      (landskron.png) the recorded run starts from.

  make_media.py replay <events.jsonl> <result.png> <input.png> <demo media dir>
      Turns a recorded worker run (record_worker.py) into the files the demo
      loads: landskron.webp (input), landskron-localsr.webp (result) and
      landskron-run.json (the worker events, each finished tile carrying its
      pixels cut from the real result).

Needs Pillow.
"""

import base64
import io
import json
import sys
from pathlib import Path

from PIL import Image

CROP = (230, 450, 230 + 3200, 450 + 1800)  # 16:9 around the castle in the 4200 x 2362 hero
INPUT_SIZE = (800, 450)
PROGRESSIVE_LIMIT = 1600  # MAXIMUM_PROGRESSIVE_DIMENSION in desktop/src/lib/progressive-preview.ts
OUTPUT_PATH = "/Users/you/Pictures/LocalSR Results/landskron_localsr.png"


def make_input(hero: Path, workdir: Path) -> None:
    workdir.mkdir(parents=True, exist_ok=True)
    crop = Image.open(hero).convert("RGB").crop(CROP)
    # Box filter, no compression: JPEG blocks made both photo models smear the stars.
    crop.resize(INPUT_SIZE, Image.Resampling.BOX).save(workdir / "landskron.png")


def make_replay(events_path: Path, result_path: Path, input_path: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    result = Image.open(result_path).convert("RGB")
    result.save(out / "landskron-localsr.webp", quality=90, method=6)
    Image.open(input_path).convert("RGB").save(out / "landskron.webp", lossless=True)
    scale = PROGRESSIVE_LIMIT / max(result.size)
    events = []
    for line in events_path.read_text().splitlines():
        event = json.loads(line)
        kind, data = event["type"], event["data"]
        if kind in ("log", "live_preview_frame"):
            continue
        if kind == "tile_update" and data.get("phase") == "completed":
            box = (
                data["output_x"],
                data["output_y"],
                data["output_x"] + data["output_width"],
                data["output_y"] + data["output_height"],
            )
            tile = result.crop(box)
            size = (max(1, round(tile.width * scale)), max(1, round(tile.height * scale)))
            buffer = io.BytesIO()
            tile.resize(size, Image.Resampling.LANCZOS).save(buffer, "JPEG", quality=86)
            data["jpeg_base64"] = base64.b64encode(buffer.getvalue()).decode()
        if kind == "job_completed":
            data["output_path"] = OUTPUT_PATH
        events.append({"t": event["t"], "type": kind, "data": data})
    (out / "landskron-run.json").write_text(json.dumps(events, separators=(",", ":")))


if __name__ == "__main__":
    if sys.argv[1:2] == ["input"]:
        make_input(Path(sys.argv[2]), Path(sys.argv[3]))
    elif sys.argv[1:2] == ["replay"]:
        make_replay(*(Path(argument) for argument in sys.argv[2:6]))
    else:
        raise SystemExit(__doc__)
