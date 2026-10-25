"""
ai_engine.py — the AI layer for CodeQuest 2 (the sequel).
Cross-platform, zero dependencies (stdlib only).

- Auto-detects Ollama on launch (Windows + macOS + Linux).
- Falls back to OpenAI if Ollama isn't available.
- Exposes one clean function: chat(messages, model) -> str
  plus list_models() and pick_default_model() for auto-detection.

Works offline: if Ollama is running locally, no internet or API key needed.
"""

import os
import json
import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# Provider config (auto-detected, overridable)
# ---------------------------------------------------------------------------
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

# Preferred model ranking when auto-detecting Ollama.
# Fast + strong first so the game feels instant on an RTX 3090;
# the big 27B model stays available to pick explicitly.
PREFERRED_OLLAMA = [
    "qwen2.5-coder:7b",
    "gemma3:12b",
    "qwen2.5:7b",
    "gemma4:26b",
    "qwen3.8-27b-obiterated-mythos-class-agentic",
]


def _http_json(url, body=None, headers=None, timeout=30):
    """Tiny stdlib HTTP helper. Returns (status_code, parsed_json_or_text)."""
    data = None
    hdrs = {"Content-Type": "application/json"}
    if headers:
        hdrs.update(headers)
    if body is not None:
        data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=hdrs, method="POST" if body else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode()
            try:
                return r.status, json.loads(raw)
            except json.JSONDecodeError:
                return r.status, raw
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return None, str(e)


# ---------------------------------------------------------------------------
# Ollama
# ---------------------------------------------------------------------------
def ollama_available():
    """True if an Ollama server is reachable."""
    status, body = _http_json(OLLAMA_HOST + "/api/version", timeout=3)
    return status == 200


def list_models():
    """Return (provider, [model names]) auto-detected on launch."""
    if ollama_available():
        status, body = _http_json(OLLAMA_HOST + "/api/tags", timeout=5)
        if status == 200 and isinstance(body, dict):
            names = [m.get("name", "") for m in body.get("models", [])]
            names = [n for n in names if n]
            return "ollama", names
    if OPENAI_API_KEY:
        return "openai", [OPENAI_MODEL]
    return "none", []


def pick_default_model(models):
    """Pick the best model from a detected list, or None."""
    for pref in PREFERRED_OLLAMA:
        for m in models:
            if m == pref:
                return m
    if models:
        return models[0]
    return None


def _ollama_chat(messages, model):
    status, body = _http_json(
        OLLAMA_HOST + "/api/chat",
        body={"model": model, "messages": messages, "stream": False},
    )
    if status != 200 or not isinstance(body, dict):
        raise RuntimeError(f"Ollama chat failed: status={status} body={body}")
    return body.get("message", {}).get("content", "")


# ---------------------------------------------------------------------------
# OpenAI (fallback)
# ---------------------------------------------------------------------------
def _openai_chat(messages, model):
    if not OPENAI_API_KEY:
        raise RuntimeError("No OPENAI_API_KEY set and Ollama unreachable.")
    status, body = _http_json(
        "https://api.openai.com/v1/chat/completions",
        body={"model": model, "messages": messages},
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
    )
    if status != 200 or not isinstance(body, dict):
        raise RuntimeError(f"OpenAI chat failed: status={status} body={body}")
    return body["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def chat(messages, model=None):
    """Send a chat to the detected provider. `messages` is a list of
    {"role": "system"|"user"|"assistant", "content": str} dicts.
    Returns the assistant's text response."""
    provider, models = list_models()
    if provider == "ollama":
        if model is None:
            model = pick_default_model(models)
        return _ollama_chat(messages, model)
    if provider == "openai":
        if model is None:
            model = OPENAI_MODEL
        return _openai_chat(messages, model)
    raise RuntimeError("No AI provider available: start Ollama or set OPENAI_API_KEY.")


def self_test():
    """Quick connectivity check, returns a human-readable string."""
    provider, models = list_models()
    if provider == "none":
        return "No AI backend found (no Ollama, no OPENAI_API_KEY)."
    default = pick_default_model(models) if provider == "ollama" else (models[0] if models else OPENAI_MODEL)
    try:
        out = chat([{"role": "user", "content": "Reply with exactly: OK"}], model=default)
        return f"{provider}/{default}: {out.strip()[:60]}"
    except Exception as e:
        return f"{provider}/{default} detected but chat failed: {e}"


if __name__ == "__main__":
    print(self_test())
