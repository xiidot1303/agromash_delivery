import json
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from bot.control.updater import application
from telegram import Update
import asyncio
from asgiref.sync import sync_to_async, async_to_sync

# @csrf_exempt
# def bot_webhook(request):
#     data = json.loads(request.body.decode("utf-8"))
#     update = Update.de_json(data = data, bot=application.bot)
#     async_to_sync(update_bot)(update)

#     return HttpResponse('')

@method_decorator(csrf_exempt, name='dispatch')
class BotWebhookView(View):
    async def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode("utf-8"))
        update = Update.de_json(data = data, bot=application.bot)
        await update_bot(update)
        return JsonResponse({'status': 'success'})

async def update_bot(update):
    await application.update_queue.put(update)
    