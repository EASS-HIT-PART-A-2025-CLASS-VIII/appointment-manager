import asyncio

import pytest
import redis.asyncio as redis

from backend.scripts.refresh import refresh_summary_job


@pytest.mark.anyio
async def test_refresh_idempotency():
    r = redis.from_url("redis://redis:6379")
    sem = asyncio.Semaphore(1)
    label = "daily"

    try:
        await r.ping()
    except Exception:
        await r.aclose()
        pytest.skip("Redis is not available")

    await r.set(f"refresh_lock:summary:{label}", "done")

    result = await refresh_summary_job(label, r, sem, "http://backend:8000", None)
    assert result == "skipped"

    await r.delete(f"refresh_lock:summary:{label}")
    await r.aclose()
