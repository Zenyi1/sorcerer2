"""Optional plain-English narration of the result through the Claude API.

Needs ANTHROPIC_API_KEY (or an `ant auth login` profile) and `pip install anthropic`. The model
is asked to explain the numbers it is given, not to add any.
"""
from __future__ import annotations

import json
import os


def narrate(summary: dict, model: str = "claude-opus-5-5") -> str:
    try:
        from anthropic import Anthropic
    except ImportError:
        return "narration skipped: `pip install anthropic` to enable --narrate"
    if not os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        # A stored `ant auth login` profile also works; let the SDK try and report cleanly if not.
        pass
    client = Anthropic()
    prompt = (
        "You are writing for a biotech partnering team. Using only the JSON below, explain in plain English and under 250 words "
        "why the model reaches each launch verdict, which two or three inputs drive the difference between the countries, and "
        "where and why the model disagrees with the originator's own numbers. Do not invent numbers; quote the JSON values. "
        "No headers, no bullet lists longer than four items.\n\n" + json.dumps(summary, default=str)
    )
    try:
        resp = client.beta.messages.create(
            model=model,
            max_tokens=2000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:  # auth, network, quota
        return f"narration failed: {exc.__class__.__name__}: {exc}"
    if resp.stop_reason == "refusal":
        return "narration declined by the model's safety layer"
    return "\n".join(block.text for block in resp.content if getattr(block, "type", "") == "text").strip()
