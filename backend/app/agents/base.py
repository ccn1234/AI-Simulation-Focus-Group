import asyncio
import contextvars
import json
import time
from openai import OpenAI
from app.config import AI_MAX_RETRIES, AI_REQUEST_TIMEOUT_SECONDS, AI_RETRY_DELAY_SECONDS, OPENAI_API_KEY, OPENAI_MODEL

_client = OpenAI(api_key=OPENAI_API_KEY)
_usage_context = contextvars.ContextVar("ai_usage_context", default=None)

def start_usage_context():
    return _usage_context.set([])

def end_usage_context(token):
    records = _usage_context.get() or []
    _usage_context.reset(token)
    return records

def _request(messages, temperature):
    kwargs = {"model": OPENAI_MODEL, "messages": messages, "response_format": {"type": "json_object"}, "temperature": temperature}
    try:
        return _client.chat.completions.create(**kwargs)
    except Exception as exc:
        if "temperature" not in str(exc): raise
        kwargs.pop("temperature", None)
        return _client.chat.completions.create(**kwargs)

async def call_json_agent(system_prompt: str, user_prompt: str, temperature: float = 0.7, agent_name: str = "unknown") -> dict:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not configured")
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
    last_error = None
    for attempt in range(1, AI_MAX_RETRIES + 2):
        started = time.perf_counter()
        try:
            completion = await asyncio.wait_for(asyncio.to_thread(_request, messages, temperature), timeout=AI_REQUEST_TIMEOUT_SECONDS)
            raw = completion.choices[0].message.content
            if not raw: raise ValueError("AI response was empty")
            data = json.loads(raw)
            usage = getattr(completion, "usage", None)
            record = {"agent_name": agent_name, "model_name": OPENAI_MODEL, "prompt_tokens": getattr(usage, "prompt_tokens", None), "completion_tokens": getattr(usage, "completion_tokens", None), "total_tokens": getattr(usage, "total_tokens", None), "elapsed_ms": int((time.perf_counter()-started)*1000), "attempt": attempt, "status": "succeeded"}
            if _usage_context.get() is not None: _usage_context.get().append(record)
            return data
        except Exception as exc:
            last_error = exc
            if attempt > AI_MAX_RETRIES: break
            await asyncio.sleep(AI_RETRY_DELAY_SECONDS * (2 ** (attempt - 1)))
    record = {"agent_name": agent_name, "model_name": OPENAI_MODEL, "elapsed_ms": int((time.perf_counter()-started)*1000), "attempt": AI_MAX_RETRIES + 1, "status": "failed", "error_type": type(last_error).__name__, "error_message": str(last_error)[:500]}
    if _usage_context.get() is not None: _usage_context.get().append(record)
    raise last_error
