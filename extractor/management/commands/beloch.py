# extractor/management/commands/beloch.py

from django.core.management.base import BaseCommand, CommandParser
from django.core.management import call_command

class Command(BaseCommand):
    help = "Runs simplified paper processing (no animal gates, only electrophysiology relevance)."

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("--folder", type=str, default=None)
        parser.add_argument("--out", type=str, default="./OUT")
        parser.add_argument("--prompt", type=str, default="./PROMPT.txt")

    def handle(self, *args, **options):
        call_command(
            "process_papers",
            folder=options["folder"],
            out=options["out"],
            prompt=options["prompt"],
        )
