"""Kết nối mô hình ngôn ngữ chạy cục bộ qua Ollama (Buổi 1).

- chat(): gọi /api/chat, temperature = 0 để kết quả ổn định, dễ kiểm thử.
- embed(): gọi /api/embed để nhúng văn bản (Buổi 6).
- co_ollama(): kiểm tra Ollama có chạy không. Khi LLM_MODE=auto mà Ollama không chạy,
  các mô-đun RAG và agent chuyển sang chế độ offline (không cần mô hình), để hệ thống
  vẫn vận hành an toàn và có thể kiểm thử tự động trên máy CI.
"""
import time

import httpx

from . import config

_trang_thai = {"luc": 0.0, "co": False}


def co_ollama() -> bool:
    if config.LLM_MODE == "offline":
        return False
    if time.time() - _trang_thai["luc"] < 30:          # nhớ kết quả 30 giây
        return _trang_thai["co"]
    try:
        r = httpx.get(f"{config.OLLAMA_URL}/api/tags", timeout=2)
        ten = [m["name"] for m in r.json().get("models", [])]
        co = r.status_code == 200 and any(n.startswith(config.MO_HINH_SINH.split(":")[0]) for n in ten)
    except Exception:
        co = False
    if config.LLM_MODE == "ollama" and not co:
        raise RuntimeError("LLM_MODE=ollama nhưng không kết nối được Ollama hoặc chưa tải mô hình.")
    _trang_thai.update(luc=time.time(), co=co)
    return co


def chat(messages: list, tools: list | None = None) -> dict:
    body = {"model": config.MO_HINH_SINH, "messages": messages, "stream": False,
            "options": {"temperature": 0}}
    if tools:
        body["tools"] = tools
    r = httpx.post(f"{config.OLLAMA_URL}/api/chat", json=body, timeout=180)
    r.raise_for_status()
    return r.json()   # gồm message, prompt_eval_count (số token đầu vào thực tế)


def embed(texts: list[str]) -> list[list[float]]:
    r = httpx.post(f"{config.OLLAMA_URL}/api/embed",
                   json={"model": config.MO_HINH_NHUNG, "input": texts}, timeout=180)
    r.raise_for_status()
    return r.json()["embeddings"]
