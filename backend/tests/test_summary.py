import json

from backend.app.routes import summary as summary_routes


class FakeRedis:
    def __init__(self):
        self.storage = {}
        self.queue = []

    def lpush(self, key: str, value: str):
        if key not in self.queue:
            self.queue.append(key)
        self.storage.setdefault(key, [])
        self.storage[key].insert(0, value)

    def get(self, key: str):
        return self.storage.get(key)

    def set(self, key: str, value: str):
        self.storage[key] = value


def test_queue_summary_job_enqueues_payload(client, auth_headers, monkeypatch):
    fake_redis = FakeRedis()
    monkeypatch.setattr(summary_routes, "redis_client", fake_redis)

    response = client.post("/summary/", headers=auth_headers)
    assert response.status_code == 200

    payload = fake_redis.storage[summary_routes.SUMMARY_QUEUE][0]
    data = json.loads(payload)
    assert "appointments" in data


def test_get_summary_result_pending(client, auth_headers, monkeypatch):
    fake_redis = FakeRedis()
    monkeypatch.setattr(summary_routes, "redis_client", fake_redis)

    response = client.get("/summary/result", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {"status": "pending", "summary": None}


def test_get_summary_result_ready(client, auth_headers, monkeypatch):
    fake_redis = FakeRedis()
    fake_redis.set(summary_routes.SUMMARY_RESULT_KEY, "hello")
    monkeypatch.setattr(summary_routes, "redis_client", fake_redis)

    response = client.get("/summary/result", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "summary": "hello"}
