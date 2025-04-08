from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import register_events, DjangoJobStore
from app.scheduled_job import *
from asgiref.sync import async_to_sync
from app.scheduled_job.bitrix_job import *

class jobs:
    scheduler = BackgroundScheduler(timezone='Asia/Tashkent')
    scheduler.add_jobstore(DjangoJobStore(), 'djangojobstore')
    register_events(scheduler)
    scheduler.add_job(
        async_to_sync(fetch_and_create_stores), 'interval', minutes=300)
    scheduler.add_job(
        async_to_sync(fetch_and_create_products), 'interval', minutes=20)
    scheduler.add_job(
        async_to_sync(fetch_and_create_store_products), 'interval', minutes=10)
