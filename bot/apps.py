from django.apps import AppConfig


class bot(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot'

    def ready(self):
        import bot.signals
        # save bot user lang codes to redis
        from bot.services.redis_service import save_langs_to_redis
        try:
            save_langs_to_redis()
        except:
            None
        # run_once = os.environ.get('CMDLINERUNNER_RUN_ONCE_BOT')
        # if run_once is not None:
        #     return
        # os.environ['CMDLINERUNNER_RUN_ONCE_BOT'] = 'True'
        from bot.scheduled_job.updater import jobs
        jobs.scheduler.start()