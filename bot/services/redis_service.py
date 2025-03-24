import redis
from bot.models import Bot_user
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from config import BOT_API_TOKEN

# Initialize Redis connection
redis_client = redis.StrictRedis(host='localhost', port=6379, db=13)


def save_langs_to_redis():
    """
    Save all Bot_user langs to Redis by user_id if Redis is empty.
    """
    user_lang_keys_exist = any(redis_client.scan_iter(match=f"{BOT_API_TOKEN}:user_lang:*"))
    # Check if Redis is empty
    if not user_lang_keys_exist:
        # Create a dictionary of user_id: lang
        user_langs = dict(
            Bot_user.objects.filter(user_id__isnull=False).annotate(
                redis_key=Concat(Value(f"{BOT_API_TOKEN}:user_lang:"), F(
                    "user_id"), output_field=CharField())
            ).values_list("redis_key", "lang")
        )

        if user_langs:  # Only proceed if there are users to save
            # Save the langs to Redis in bulk
            redis_client.mset(user_langs)
        else:
            print("No bot users found in the database to save.")
    else:
        print("Redis is not empty. No action taken.")


def set_user_lang(user_id, lang):
    redis_key = f"{BOT_API_TOKEN}:user_lang:{user_id}"
    redis_client.set(redis_key, lang)


def get_user_lang(user_id):
    # Construct the Redis key
    redis_key = f"{BOT_API_TOKEN}:user_lang:{user_id}"

    # Get the value from Redis
    lang = redis_client.get(redis_key)

    if lang is not None:
        # Decode the Redis byte response to string or integer
        # Assuming the language is stored as an integer
        return int(lang.decode())
    else:
        # Return None or handle the case where the user is not found
        return Bot_user._meta.get_field('lang').default
