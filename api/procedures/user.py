from beanie.odm.operators.update.general import Set

from api.models.user import User


async def create_or_update_user(preferred_username: str) -> User:
    await User.find_one(User.preferred_username == preferred_username).upsert(
        Set({'preferred_username': preferred_username}), on_insert=User(preferred_username=preferred_username)
    )
    user = await User.find_one(User.preferred_username == preferred_username)
    await user.fetch_all_links()
    return user
