import json

from beanie import DeleteRules, WriteRules

from api.models.user import User


async def delete_submission(identifier: str, user: User):
    submission = user.submission(identifier)
    await submission.delete(link_rule=DeleteRules.DELETE_LINKS)


async def create_or_update_submission(identifier, record, user: User, metadata_json):
    submission = record.to_submission(identifier)
    submission.metadata_json = json.dumps(metadata_json, default=str)
    existing_submission = user.submission(identifier)
    if existing_submission:
        await existing_submission.set(submission.model_dump(exclude_unset=True))
    else:
        user.submissions.append(submission)
        await user.save(link_rule=WriteRules.WRITE)
