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
    """Pick the best model from the detected list."""
    if not models:
        return None
    for preferred in PREFERRED_OLLAMA:
        if preferred in models:
            return preferred
    return models[0]


# ---------------------------------------------------------------------------
# Unified chat interface
# ---------------------------------------------------------------------------
def chat(messages, model=None, temperature=0.7, max_tokens=2048):
    """Send a chat completion request and return the text response.
    
    Args:
        messages: list of {"role": "system"|"user"|"assistant", "content": str}
        model: model name (auto-picked if None)
        temperature: sampling temperature
        max_tokens: max tokens in response
    
    Returns:
        str: the assistant's text response
    """
    if model is None:
        provider, models = list_models()
        if provider == "ollama":
            model = pick_default_model(models)
        elif provider == "openai":
            model = OPENAI_MODEL
        else:
            raise RuntimeError("No LLM provider available. Start Ollama or set OPENAI_API_KEY.")
    
    if model in PREFERRED_OLLAMA or provider_is_ollama(model):
        return _chat_ollama(messages, model, temperature, max_tokens)
    else:
        return _chat_openai(messages, model, temperature, max_tokens)


def provider_is_ollama(model):
    return any(model.startswith(p) for p in ["qwen", "gemma", "llama", "mistral", "phi"])


def _chat_ollama(messages, model, temperature, max_tokens):
    url = OLLAMA_HOST + "/api/chat"
    body = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    status, body_resp = _http_json(url, body)
    if status != 200:
        raise RuntimeError(f"Ollama error ({status}): {body_resp}")
    return body_resp.get("message", {}).get("content", "")


def _chat_openai(messages, model, temperature, max_tokens):
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set.")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    status, body_resp = _http_json(url, body, headers)
    if status != 200:
        raise RuntimeError(f"OpenAI error ({status}): {body_resp}")
    return body_resp["choices"][0]["message"]["content"]


def list_available_models():
    """Convenience: return (provider, models) for display."""
    return list_models()
