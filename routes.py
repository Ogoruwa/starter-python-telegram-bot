from environs import Env
from fastapi import APIRouter, Response

env = Env()
env.read_env()

health_url = env.str("HEALTH_URL", "/health/")
webhook_url = env.str("WEBHOOK_URL", "/webhook/")

router = APIRouter(
    responses = {
        404: {"description": "Not found"},
        403: {"description": "Not authorized"},
    },
)


@router.get(health_url)
async def health_check():
    content = "Health is good"
    return Response( content )

