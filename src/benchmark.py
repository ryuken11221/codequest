"""
benchmark.py — quick AI backend benchmark.
Times N round-trips against the active provider and prints p50/p95.
Run:  python src/benchmark.py
"""
import time, statistics, sys, json
sys.path.insert(0, ".")
from src.ai_engine import chat, list_models, pick_default_model

N = int(sys.argv[1]) if len(sys.argv) > 1 else 3

provider, models = list_models()
if provider == "none":
    print("No provider available — aborting.")
    sys.exit(1)
model = pick_default_model(models) if provider == "ollama" else (models[0] if models else None)
print(f"provider={provider} model={model} n={N}")

times = []
for i in range(N):
    t0 = time.perf_counter()
    out = chat([{"role": "user", "content": "Reply with exactly: OK"}], model=model)
    dt = time.perf_counter() - t0
    times.append(dt)
    print(f"  [{i+1}/{N}] {dt*1000:.0f} ms  response={out.strip()[:40]!r}")

times.sort()
print()
print(f"min   = {times[0]*1000:.0f} ms")
print(f"p50   = {times[len(times)//2]*1000:.0f} ms")
print(f"p95   = {times[min(len(times)-1, int(len(times)*0.95))]*1000:.0f} ms")
print(f"max   = {times[-1]*1000:.0f} ms")
print(f"mean  = {statistics.mean(times)*1000:.0f} ms")
print(f"total = {sum(times):.2f} s")
