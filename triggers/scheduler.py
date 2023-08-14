import logging

import typer
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from rocketry import Rocketry
from rocketry.conds import daily

from api.adapters.utils import RepositoryType, get_adapter_by_type
from api.config import get_settings
from api.models.catalog import DatasetMetadataDOC
from api.models.user import Submission

app = Rocketry(config={"task_execution": "async"})
logger = logging.getLogger()


async def retrieve_repository_record(submission: Submission):
    """Retrieve the repository record from the repository and return it as a Catalog Record"""
    if submission.repository in RepositoryType.__members__:
        adapter = get_adapter_by_type(RepositoryType[submission.repository])
        try:
            repo_record_metadata = await adapter.get_metadata(submission.repository_identifier)
        except Exception as err:
            if hasattr(err, "detail"):
                err_details = err.detail
            else:
                err_details = str(err)

            err_msg = (f"Error retrieving metadata from {submission.repository} repository "
                       f"for record id: {submission.repository_identifier}: {err_details}")
            logger.error(err_msg)
            return None
        return adapter.to_catalog_record(repo_record_metadata)
    else:
        err_msg = f"Repository type {submission.repository} is not supported"
        logger.error(err_msg)
        raise Exception(err_msg)


@app.task(daily)
async def do_daily():
    settings = get_settings()
    db = AsyncIOMotorClient(settings.db_connection_string)[settings.database_name]
    await init_beanie(database=db, document_models=[Submission, DatasetMetadataDOC])

    async for submission in Submission.find(Submission.repository != None):
        try:
            dataset = await DatasetMetadataDOC.get(submission.identifier)
            if dataset is None:
                logger.warning(f"No catalog record was found for submission: {submission.identifier}")
                continue

            updated_dataset = await retrieve_repository_record(submission)
            if updated_dataset is not None:
                # update catalog record
                await dataset.set(updated_dataset.dict(exclude_unset=True, by_alias=True))

                # update submission record
                dataset = await DatasetMetadataDOC.get(submission.identifier)
                updated_submission = dataset.as_submission()
                updated_submission.repository_identifier = submission.repository_identifier
                updated_submission.repository = submission.repository
                await submission.set(updated_submission.dict(exclude_unset=True))

            else:
                # couldn't retrieve matching repository record
                await db["discovery"].delete_one({"_id": submission.identifier})
        except:
            logger.exception(f"Failed to collect submission {submission.url}")


def main():
    app.run()


if __name__ == "__main__":
    typer.run(main)
