"""Offline stand-ins for paid or online services, so AI-integration exercises run free and deterministically.

MockLLM      behaves like a chat-completion client: scripted replies, every request recorded.
HashEmbedder turns text into fixed-size vectors by hashing words: lexical, not semantic, but deterministic.
fake_get     answers HTTP GET requests from a dictionary of canned responses.
Real clients appear in the lessons too; tests always use these, so they never need a key or a network.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Callable
from dataclasses import dataclass, field

__all__ = ["FakeResponse", "HashEmbedder", "MockLLM", "fake_get"]


@dataclass
class MockLLM:
    """replies: a list used in order (the last one repeats) or a function(messages) -> str."""
    replies: list[str] | Callable[[list[dict]], str]
    calls: list[dict] = field(default_factory=list)

    def complete(self, messages: list[dict], **options) -> str:
        if not messages or any({"role", "content"} - set(m) for m in messages):
            raise ValueError("messages must be a non-empty list of {'role': ..., 'content': ...} dicts")
        self.calls.append({"messages": messages, **options})
        if callable(self.replies):
            return self.replies(messages)
        return self.replies[min(len(self.calls), len(self.replies)) - 1]


@dataclass
class HashEmbedder:
    """Bag-of-words vectors: each lower-case word adds +1 or -1 to one of `dim` slots; vectors have length 1."""
    dim: int = 64

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for word in re.findall(r"[a-z0-9]+", text.lower()):
            digest = hashlib.blake2b(word.encode(), digest_size=8).digest()
            slot = int.from_bytes(digest[:4], "big") % self.dim
            vec[slot] += 1.0 if digest[4] % 2 == 0 else -1.0
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]


@dataclass
class FakeResponse:
    """The parts of requests.Response / httpx.Response that the course uses."""
    status_code: int = 200
    payload: object = None

    @property
    def text(self) -> str:
        return json.dumps(self.payload)

    def json(self):
        return self.payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def fake_get(routes: dict[str, FakeResponse]) -> Callable[..., FakeResponse]:
    """Return a get(url, **kwargs) function that answers from `routes` (404 for anything else)."""
    def get(url: str, **kwargs) -> FakeResponse:
        return routes.get(url, FakeResponse(404, {"error": "not found"}))
    return get
