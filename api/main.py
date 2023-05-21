import asyncio
import logging

import uvicorn
from beanie import init_beanie
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from motor.motor_asyncio import AsyncIOMotorClient

from api.config import get_settings
from api.models.catalog import DatasetMetadataDOC
from api.models.user import Submission, User
from api.routes.catalog import router as catalog_router
from api.routes.discovery import router as discovery_router
from api.scheduler import app as app_rocketry
from api.triggers import watch_catalog_with_retry, watch_submissions_with_retry

# had to use load_dotenv() to get the env variables to work during testing
load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_db_client():
    settings = get_settings()
    app.mongodb_client = AsyncIOMotorClient(settings.db_connection_string)
    app.mongodb = app.mongodb_client[settings.database_name]
    await init_beanie(database=app.mongodb, document_models=[DatasetMetadataDOC, User, Submission])


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(catalog_router, tags=["Dataset"], prefix="/api/catalog")
app.include_router(discovery_router, tags=["Discovery"], prefix="/api/discovery")

openapi_schema = get_openapi(
    title="I-GUIDE Catalog API",
    version="1.0",
    description="Standardized interface with validation for managing catalog",
    routes=app.routes,
)
app.openapi_schema = openapi_schema


class Server(uvicorn.Server):
    def handle_exit(self, sig: int, frame) -> None:
        app_rocketry.session.shut_down()
        return super().handle_exit(sig, frame)


async def main():
    """Run Rocketry and FastAPI"""

    settings = get_settings()
    reload = settings.local_development is True
    server = Server(config=uvicorn.Config(app, workers=1, loop="asyncio", host="0.0.0.0", port=5002, reload=reload))
    api = asyncio.create_task(server.serve())
    if settings.local_development:
        await asyncio.wait([api])
    else:
        scheduler = asyncio.create_task(app_rocketry.serve())
        catalog_trigger = asyncio.create_task(watch_catalog_with_retry())
        submissions_trigger = asyncio.create_task(watch_submissions_with_retry())
        await asyncio.wait([api, catalog_trigger, submissions_trigger, scheduler])

if __name__ == "__main__":
    rocketry_logger = logging.getLogger("rocketry.task")
    rocketry_logger.addHandler(logging.StreamHandler())

    asyncio.run(main())
