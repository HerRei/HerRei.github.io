#!/usr/bin/env python3
"""Reproduce the website comparison using the actual LocalSR automation pipeline.

Run with LocalSR's Python environment:
    /path/to/LocalSR/.venv/bin/python localsr/tools/prepare_demo.py --localsr /path/to/LocalSR

The verified SPAN NomosUni model must already be installed in LocalSR.
Pillow prepares a documented input and encodes web assets; LocalSR produces the result.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request

from PIL import Image

SOURCE_PAGE = "https://unsplash.com/photos/modern-apartment-building-with-colorful-balconies-against-blue-sky-n4bofMDUS_Y"
SOURCE_IMAGE = "https://images.unsplash.com/photo-1760905662814-d1288d915ab5?auto=format&fit=max&w=2400&q=95"
PHOTO_CROP = (0, 1900, 2268, 3034)
DETAIL_CROP = (96, 32, 256, 112)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--localsr", required=True, type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()
    assets = Path(__file__).resolve().parents[1] / "assets"
    assets.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="localsr-showcase-") as temporary:
        work = Path(temporary)
        source = args.source
        if source is None:
            source = work / "source.jpg"
            urllib.request.urlretrieve(SOURCE_IMAGE, source)
        photo = Image.open(source).convert("RGB")
        if photo.size != (2268, 4032):
            raise ValueError(f"Source dimensions changed: {photo.size}; review the crop first.")
        frame = photo.crop(PHOTO_CROP)
        before = frame.resize((480, 240), Image.Resampling.LANCZOS)
        input_path = work / "marseille.png"
        before.save(input_path)
        output = work / "output"
        command = [
            sys.executable, "-m", "localsr", "process", str(input_path),
            "--output", str(output), "--model", "span_photo_x4", "--scale", "4",
            "--device", args.device, "--precision", "fp32", "--format", "png",
            "--tile-size", "256", "--halo", "16", "--no-metadata", "--json",
        ]
        completed = subprocess.run(command, cwd=args.localsr, check=True, capture_output=True, text=True)
        print(completed.stdout)
        result_files = list(output.glob("*.png"))
        if len(result_files) != 1:
            raise RuntimeError(f"Expected one LocalSR output, got {result_files}")
        result_path = result_files[0]
        after = Image.open(result_path).convert("RGB")
        if after.size != (1920, 960):
            raise ValueError(f"Unexpected LocalSR dimensions: {after.size}")

        before.save(assets / "marseille-input.png", optimize=True)
        after.save(assets / "marseille-output.webp", lossless=True, method=6)
        before.crop(DETAIL_CROP).save(assets / "marseille-detail-input.png", optimize=True)
        after.crop(tuple(value * 4 for value in DETAIL_CROP)).save(
            assets / "marseille-detail-output.webp", lossless=True, method=6
        )
        after.resize((960, 480), Image.Resampling.LANCZOS).save(
            assets / "marseille-print.webp", quality=88, method=6
        )
        provenance = {
            "photographer": "Tim Ziegelbaum",
            "source_page": SOURCE_PAGE,
            "source_image": SOURCE_IMAGE,
            "source_sha256": sha256(source),
            "license": "Unsplash License",
            "license_url": "https://unsplash.com/license",
            "subject": "Unité d’Habitation, Marseille, France",
            "source_dimensions": list(photo.size),
            "source_crop_xyxy": PHOTO_CROP,
            "input_preparation": "Selected landscape crop resized with Pillow Lanczos; no added blur or noise.",
            "input_dimensions": list(before.size),
            "output_dimensions": list(after.size),
            "detail_crop_input_xyxy": DETAIL_CROP,
            "pipeline": "LocalSR automation CLI, process",
            "localsr_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=args.localsr, text=True
            ).strip(),
            "model_id": "span_photo_x4",
            "model_name": "SPAN 4x NomosUni — Quick",
            "model_author": "Philip Hofmann",
            "model_url": "https://github.com/Phhofm/models/releases/tag/4xNomosUni_span_multijpg",
            "model_license": "CC BY 4.0",
            "model_sha256": "3a9037c36de90e7825c030176c8e193dfd7897ef4b5df91b8bdc59ffb6ab65ca",
            "device": args.device,
            "precision": "fp32",
            "tile_size": 256,
            "halo": 16,
            "output_encoding": "Lossless WebP, no additional sharpening or color adjustment",
            "assets": {path.name: sha256(path) for path in sorted(assets.glob("marseille-*"))},
            "processing_events": [json.loads(line) for line in completed.stdout.splitlines() if line.startswith("{")],
        }
        # CLI events contain local paths; retain only a public-safe account of the operation.
        provenance.pop("processing_events")
        (assets / "image-provenance.json").write_text(
            json.dumps(provenance, indent=2, ensure_ascii=False) + "\n"
        )
        print("Saved real comparison assets and image-provenance.json")


if __name__ == "__main__":
    main()
