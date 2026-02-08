import asyncio
import os
from typing import Iterable

import httpx
import redis.asyncio as redis

API_URL = os.getenv("API_URL", "http://backend:8000")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
JWT_TOKEN = os.getenv("JWT_TOKEN")


def _auth_headers(token: str | None) -> dict:
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


async def refresh_summary_job(
    label: str,
    r: redis.Redis,
    semaphore: asyncio.Semaphore,
    api_url: str,
    token: str | None,
    client: httpx.AsyncClient | None = None,
) -> str:
    async with semaphore:
        idempotency_key = f"refresh_lock:summary:{label}"
        if await r.exists(idempotency_key):
            print(f"SKIP {label}: already processed")
            return "skipped"

        if not token:
            raise RuntimeError("JWT_TOKEN is required to call the API")

        close_client = False
        if client is None:
            client = httpx.AsyncClient()
            close_client = True

        try:
            for attempt in range(3):
                try:
                    response = await client.post(
                        f"{api_url}/summary/",
                        headers=_auth_headers(token),
                    )
                    if response.status_code == 200:
                        await r.setex(idempotency_key, 300, "done")
                        print(f"DONE {label}")
                        return "done"
                except Exception as exc:
                    print(f"WARN {label} attempt {attempt + 1}: {exc}")
                    await asyncio.sleep(2**attempt)

            return "failed"
        finally:
            if close_client:
                await client.aclose()


async def run_refresh(labels: Iterable[str]):
    r = redis.from_url(REDIS_URL)
    semaphore = asyncio.Semaphore(3)

    async with httpx.AsyncClient() as client:
        tasks = [
            refresh_summary_job(label, r, semaphore, API_URL, JWT_TOKEN, client)
            for label in labels
        ]
        await asyncio.gather(*tasks)

    await r.aclose()


if __name__ == "__main__":
    asyncio.run(run_refresh(["daily"]))
