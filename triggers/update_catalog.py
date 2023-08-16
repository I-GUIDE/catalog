import logging
import typer

from asyncio import run as aiorun
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from api.config import get_settings
from api.models.user import Submission


logger = logging.getLogger()

async def _main():
    logger.warning("starting up watch catalog")
    settings = get_settings()
    db = AsyncIOMotorClient(settings.db_connection_string)[get_settings().database_name]
    await init_beanie(database=db, document_models=[Submission])

    try:
        while True:
            try:
                await watch_catalog(db)
            except:
                logger.exception("Submission Watch Task failed, restarting the task")
    finally:
        db.close()


async def watch_catalog(db: AsyncIOMotorClient):
    async with db["catalog"].watch(full_document="updateLookup", full_document_before_change="whenAvailable") as stream:
        # stream.resume_token
        async for change in stream:
            if change["operationType"] == "delete":
                document = change["fullDocumentBeforeChange"]
                await db["discovery"].delete_one({"_id": document["_id"]})
            else:
                document = change["fullDocument"]
                catalog_entry = await db["catalog"].find_one({"_id": document["_id"]})
                submission: Submission = await Submission.find_one({"identifier": document["_id"]})
                catalog_entry["registrationDate"] = submission.submitted
                await db["discovery"].find_one_and_replace(
                        {"_id": document["_id"]}, catalog_entry, upsert=True
                    )


def main():
    aiorun(_main())


if __name__ == "__main__":
    typer.run(main)
