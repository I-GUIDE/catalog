import logging

import motor
from beanie import init_beanie
from rocketry import Rocketry
from rocketry.conds import daily

from api.config import get_settings
from api.models.catalog import CoreMetadataDOC, Submission

app = Rocketry(config={"task_execution": "async"})

logger = logging.getLogger()


@app.task(daily)
async def do_daily():
    """This daily scheduled job maintains one-to-one relationship between catalog and submission"""

    settings = get_settings()
    db = motor.motor_asyncio.AsyncIOMotorClient(settings.db_connection_string)[settings.database_name]
    await init_beanie(database=db, document_models=[Submission, CoreMetadataDOC])

    async for catalog in CoreMetadataDOC.find_all(with_children=True):
        submission = await Submission.find(Submission.identifier == catalog.id).first_or_none()
        if not submission:
            await catalog.delete()

    async for submission in Submission.find_all():
        catalog = await CoreMetadataDOC.find(
            CoreMetadataDOC.id == submission.identifier, with_children=True
        ).first_or_none()
        if not catalog:
            await submission.delete()


if __name__ == "__main__":
    # Run only Rocketry
    app.run()
