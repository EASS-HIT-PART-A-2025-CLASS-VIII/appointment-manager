import asyncio
import json
import os
import types

os.environ.setdefault("GOOGLE_API_KEY", "test-key")

from backend.app.workers import summary_worker


class FakeAgent:
    def __init__(self, response: str):
        self.response = response
        self.last_prompt = None

    async def run(self, prompt: str):
        self.last_prompt = prompt
        return types.SimpleNamespace(data=self.response)


def test_generate_summary_uses_agent(monkeypatch):
    fake_agent = FakeAgent("summary text")
    monkeypatch.setattr(summary_worker, "agent", fake_agent)

    appointments = [{"id": 1, "client_name": "A"}]
    result = summary_worker.generate_summary(appointments)
    summary = summary_worker.asyncio.run(result)

    assert summary == "summary text"
    assert "appointments" in fake_agent.last_prompt
    assert json.dumps(appointments, indent=2) in fake_agent.last_prompt


class FakeRedis:
    def __init__(self):
        self.data = {}

    async def set(self, key: str, value: str):
        self.data[key] = value


def test_process_job_sets_summary(monkeypatch):
    fake_agent = FakeAgent("ready")
    fake_redis = FakeRedis()
    monkeypatch.setattr(summary_worker, "agent", fake_agent)

    payload = {"appointments": [{"id": 1, "client_name": "A"}]}
    raw = json.dumps(payload)

    count = asyncio.run(summary_worker.process_job(fake_redis, raw))

    assert count == 1
    assert fake_redis.data[summary_worker.SUMMARY_RESULT_KEY] == "ready"
