import uvicorn
from beanie import init_beanie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from api.config import get_settings
from api.models.catalog import DatasetMetadataDOC
from api.routes.catalog import router as catalog_router

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
    await init_beanie(database=app.mongodb, document_models=[DatasetMetadataDOC])


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()


app.include_router(catalog_router, tags=["Dataset"], prefix="/api/catalog")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
