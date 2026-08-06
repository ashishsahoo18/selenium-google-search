"""Optional OpenAI features."""
from __future__ import annotations

import base64
from pathlib import Path
from config import OPENAI_API_KEY, OPENAI_MODEL


def _client():
    if not OPENAI_API_KEY:
        return None
    from openai import OpenAI
    return OpenAI(api_key=OPENAI_API_KEY)


def improve_query(query: str) -> str:
    """Produce a concise, intent-preserving query when configured."""
    client = _client()
    if not client:
        return query
    response = client.chat.completions.create(model=OPENAI_MODEL, temperature=0.2,
        messages=[{"role": "system", "content": "Improve web-search queries. Return only the improved query."},
                  {"role": "user", "content": query}])
    return response.choices[0].message.content.strip() or query


def analyze_screenshot(path: Path) -> str:
    """Analyze a screenshot with vision-capable OpenAI model."""
    client = _client()
    if not client:
        return "Add OPENAI_API_KEY to .env to enable AI screenshot analysis."
    encoded = base64.b64encode(path.read_bytes()).decode()
    response = client.chat.completions.create(model=OPENAI_MODEL, messages=[{"role": "user", "content": [
        {"type": "text", "text": "Summarize this screenshot, list important text, main topic, and useful suggestions."},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded}"}},
    ]}])
    return response.choices[0].message.content
