from django.core.management.base import BaseCommand
from bot.control.updater import application
import asyncio
import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RestartOnChangeHandler(FileSystemEventHandler):
    def __init__(self, restart_callback):
        self.restart_callback = restart_callback

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(('.py', '.html', '.css', '.js')):
            self.restart_callback()

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(('.py', '.html', '.css', '.js')):
            self.restart_callback()
            
class Command(BaseCommand):
    help = 'Command to polling bot'

    def handle(self, *args, **options):
        observer = Observer()
        event_handler = RestartOnChangeHandler(self.restart)
        observer.schedule(event_handler, path='.', recursive=True)
        observer.start()

        try:
            print("Bot polling...")
            asyncio.run(application.run_polling())
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def restart(self):
        print("Restarting..\n\n")
        """Restart the current process."""
        os.execv(sys.executable, ['python'] + sys.argv)
