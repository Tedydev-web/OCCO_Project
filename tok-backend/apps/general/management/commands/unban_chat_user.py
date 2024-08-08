from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Unban user after 90days'

    def handle(self, *args, **options):
        try:
            ...
        except Exception as e:
            print(f"Error Unban user after 90days: {str(e)}")
