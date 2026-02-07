import asyncio
import json
import os
import redis.asyncio as redis
from pydantic_ai import Agent

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
QUEUE = "summary_jobs"
SUMMARY_RESULT_KEY = "latest_summary"

if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY environment variable is missing!")

# Use Google Gemini with API key
MODEL_NAME = os.getenv("GOOGLE_MODEL", "google-gla:gemini-2.5-flash")
agent = Agent(MODEL_NAME, api_key=GOOGLE_API_KEY)


async def generate_summary(appointments: list[dict]) -> str:
    prompt = f"Generate a helpful summary for these appointments:\n{json.dumps(appointments, indent=2)}"
    result = await agent.run(prompt)
    return str(result.data)


async def worker_loop():
    client = await redis.from_url(REDIS_URL)
    print("Worker started. Waiting for jobs...")

    while True:
        try:
            job = await client.blpop(QUEUE, timeout=5)
            
            if job is None:
                continue
                
            _, raw = job
            data = json.loads(raw)
            appointments = data.get("appointments", [])

            summary = await generate_summary(appointments)
            await client.set(SUMMARY_RESULT_KEY, summary)
            print(f"Summary generated for {len(appointments)} appointments")

        except Exception as e:
            print(f"Error processing job: {e}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(worker_loop())