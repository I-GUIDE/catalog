import asyncio
import logging
import re

from motor.motor_asyncio import AsyncIOMotorClient

from api.config import get_settings

logger = logging.getLogger()


def sanitize(text):
    # remove urls form text
    text = re.sub(r'https?://\S+', '', text)
    # remove all single characters except "a"
    text = re.sub(r"\b[a-zA-Z](?<!a)\b", "", text)
    # replace parentheses and forward slash with space
    text = re.sub('[()/]', ' ', text)
    # remove double dashes
    text = re.sub('--', '', text)
    # remove special characters
    text = re.sub('[^a-zA-Z0-9,\-_ ]', '', text)
    # remove leading/trailing hyphens
    words = text.split(' ')
    for i in range(len(words)):
        words[i] = words[i].strip("-")
    text = " ".join(words)
    # remove extra spaces
    text = " ".join(text.split())
    return text


def get_db():
    settings = get_settings()
    return AsyncIOMotorClient(settings.db_connection_string)[settings.database_name]


def extract_keyword(value):
    if isinstance(value, dict):
        return value['name']
    return value


async def watch_catalog():
    db = get_db()
    async with db["catalog"].watch(full_document="updateLookup") as stream:
        async for change in stream:
            if change["operationType"] != "delete":
                document = change["fullDocument"]
                sanitized = {
                    '_id': document['_id'],
                    'name': sanitize(document['name']),
                    'description': sanitize(document['description']),
                    'keywords': [sanitize(extract_keyword(keyword)) for keyword in document['keywords']],
                }
                await db["typeahead"].find_one_and_replace({"_id": sanitized["_id"]}, sanitized, upsert=True)
            else:
                await db["typeahead"].delete_one({"_id": change["documentKey"]["_id"]})


async def watch_catalog_with_retry():
    while True:
        try:
            await watch_catalog()
        except:
            logger.exception("Catalog Watch Task failed, restarting the task after 1 second")
            await asyncio.sleep(1)


async def watch_submissions():
    db = get_db()
    async with db["Submission"].watch(full_document_before_change="whenAvailable") as stream:
        async for change in stream:
            logger.warning(f"start with a {change}")
            if change["operationType"] == "delete":
                document = change["fullDocumentBeforeChange"]
                await db["catalog"].delete_one({"_id": document["identifier"]})


async def watch_submissions_with_retry():
    while True:
        try:
            await watch_submissions()
        except:
            logger.exception("Submission Watch Task failed, restarting the task after 1 second")
            await asyncio.sleep(1)
