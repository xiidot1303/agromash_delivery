from bot.models import Message, Bot_user
from bot.control.updater import application
from bot import NewsletterUpdate
from django.conf import settings


async def send_message():
    async for message in Message.objects.filter(is_sent=False):
        # save message as sent
        message.is_sent = True
        await message.asave()
        # get users
        users = Bot_user.objects.all().values_list('user_id', flat=True)
        async for user_id in users:
            await application.update_queue.put(NewsletterUpdate(
                user_id=int(user_id),
                text=message.text,
                photo=f"{settings.MEDIA_URL}/{message.photo.name}" if message.photo else None,
                video=f"{settings.MEDIA_URL}/{message.video.name}" if message.video else None,
                document=f"{settings.MEDIA_URL}/{message.file.name}" if message.file else None
            ))
