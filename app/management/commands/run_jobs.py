from django.core.management.base import BaseCommand
from app.scheduled_job.updater import jobs as app_jobs
from bot.scheduled_job.updater import jobs as bot_jobs

class Command(BaseCommand):
    help = 'Run scheduled jobs'

    def handle(self, *args, **kwargs):
        app_jobs.scheduler.start()
        bot_jobs.scheduler.start()
        self.stdout.write(self.style.SUCCESS('Successfully started scheduled jobs'))

        import time
        try:
            while True:
                time.sleep(2)
        except (KeyboardInterrupt, SystemExit):
            app_jobs.scheduler.shutdown()
            bot_jobs.scheduler.shutdown()
            self.stdout.write(self.style.SUCCESS('Scheduler stopped!'))