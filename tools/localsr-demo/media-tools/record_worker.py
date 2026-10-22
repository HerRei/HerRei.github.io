"""Run one upscale through a packaged LocalSR worker and record every event (stdlib only).

usage: record_worker.py <worker> <image> <model> <output> <events.jsonl> [tile_size]
"""
import json, os, subprocess, sys, time
worker, image, model, output, events_path = sys.argv[1:6]
tile = int(sys.argv[6]) if len(sys.argv) > 6 else 128
job = {"job_id": "demo-landskron", "image_path": image, "model_path": model, "output_path": output,
       "output_format": "PNG", "device": "mps", "tile_size": tile, "halo": 16, "precision": "fp16",
       "jpeg_quality": 95, "preserve_metadata": True, "safe_memory": False, "output_scale": 4,
       "face_model_path": None, "face_fidelity": 0.7, "allow_unverified_checkpoint": None,
       "preview_enabled": True, "preview_max_fps": 30.0, "preview_max_dimension": 320,
       "scratch_directory": None, "output_temporary_directory": None, "stages": None}
env = dict(os.environ, LOCALSR_WORK_DIR=os.path.dirname(output), PYTHONUTF8="1")
p = subprocess.Popen([worker], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                     stderr=open(output + ".log", "w"), text=True, env=env)
def send(kind, data):
    p.stdin.write(json.dumps({"type": kind, "data": data}) + "\n"); p.stdin.flush()
out = open(events_path, "w"); start = None; sent = False; kinds = {}
for line in p.stdout:
    try: event = json.loads(line)
    except ValueError: continue
    kind = event["type"]
    if kind == "worker_ready" and not sent:
        send("job_request", job); sent = True; start = time.time(); continue
    if start is None: continue
    kinds[kind] = kinds.get(kind, 0) + 1
    out.write(json.dumps({"t": round(time.time() - start, 3), **event}) + "\n")
    if kind in ("job_completed", "job_failed", "protocol_error"):
        print(kind, "after %.1fs" % (time.time() - start), json.dumps(event["data"])[:200]); break
out.close(); print(kinds)
send("shutdown", {}); p.stdin.close(); p.wait(timeout=30)
