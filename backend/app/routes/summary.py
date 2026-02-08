import json
import redis
from fastapi import APIRouter, Depends

from backend.app.core.deps import get_current_user
from backend.app.routes.appointments import get_repo

router = APIRouter(prefix="/summary", dependencies=[Depends(get_current_user)])

redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)

SUMMARY_QUEUE = "summary_jobs"
SUMMARY_RESULT_KEY = "latest_summary"


@router.post("/")
def queue_summary_job(repo=Depends(get_repo)):
    appointments = repo.list()
    job_data = {"appointments": [a.model_dump() for a in appointments]}

    redis_client.lpush(SUMMARY_QUEUE, json.dumps(job_data))

    return {"status": "queued", "count": len(appointments)}


@router.get("/result")
def get_summary_result():
    result = redis_client.get(SUMMARY_RESULT_KEY)

    if not result:
        return {"status": "pending", "summary": None}

    return {
        "status": "ready",
        "summary": result,
    }
