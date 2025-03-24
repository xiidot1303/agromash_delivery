from django.urls import path, re_path
from bot.views import botwebhook
from config import BOT_API_TOKEN
from django.conf import settings
from django.conf.urls.static import static
from config import DEBUG

urlpatterns = [
    path(BOT_API_TOKEN, botwebhook.BotWebhookView.as_view())
]

if DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)