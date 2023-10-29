from django.core.management.base import BaseCommand, CommandError
import asyncio
from ._bot import start_bot

class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        asyncio.run(start_bot())