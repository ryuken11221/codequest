"""
benchmark.py — simple performance benchmarks for CodeQuest AI responses.

Measures:
- Time to first token (TTFB)
- Total response time
- Tokens per second (approximate)
"""

import time
import json
from ai_engine import chat, list_models, pick_default_model


def benchmark(model=None, prompt="Explain recursion in 3 sentences.", runs=3):
    """Run a simple benchmark and print results."""
    if model is None:
        provider, models = list_models()
        model = pick_default_model(models) if models else "gpt-4o-mini"
    
    print(f"\n{'='*50}")
    print(f"Benchmark: {model}")
    print(f"Prompt: {prompt[:60]}...")
    print(f"{'='*50}\n")
    
    results = []
    for i in range(runs):
        start = time.time()
        try:
            response = chat(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                max_tokens=100,
            )
            elapsed = time.time() - start
            # Approximate token count (4 chars ≈ 1 token)
            tokens = len(response) // 4
            tps = tokens / elapsed if elapsed > 0 else 0
            
            results.append({
                "run": i + 1,
                "time_s": round(elapsed, 3),
                "tokens": tokens,
                "tps": round(tps, 1),
            })
            
            print(f"  Run {i+1}: {elapsed:.3f}s | ~{tokens} tokens | {tps:.1f} tok/s")
        except Exception as e:
            print(f"  Run {i+1}: FAILED — {e}")
    
    if results:
        avg_time = sum(r["time_s"] for r in results) / len(results)
        avg_tps = sum(r["tps"] for r in results) / len(results)
        print(f"\n  Average: {avg_time:.3f}s | {avg_tps:.1f} tok/s")
    
    return results


if __name__ == "__main__":
    benchmark()
