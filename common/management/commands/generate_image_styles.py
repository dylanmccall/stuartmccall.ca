from django.core.management.base import BaseCommand, CommandError

from common.utils import generate_image_styles
from galleries.models import Media

class Command(BaseCommand):
    help = 'Generate image styles for all uploaded media'

    def handle(self, *args, **options):
        media_count = Media.objects.count()

        for index, media in enumerate(Media.objects.iterator()):
            message = "Generating image styles for record {} / {}".format(index+1, media_count)
            print(message, end='\r')

            media.generate_image_styles()

        print("\nFinished")
