from django.core.management.base import BaseCommand, CommandError

from collections import OrderedDict
import argparse
import json
import os
import sys

from django.core.files import File

from galleries.models import (
    Gallery,
    GalleryMedia,
    Media,
    Portfolio,
    PortfolioGallery
)

THUMB_DIR = '80'
FULL_DIR = '650'

class Command(BaseCommand):
    help = 'Imports data from artsite2014'

    def add_arguments(self, parser):
        parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
        parser.add_argument('--basepath', required=True)

    def handle(self, *args, **options):
        infile = options['infile']
        basepath = options['basepath']

        data = json.load(infile, object_pairs_hook=OrderedDict)

        portfolio = Portfolio(title="Imported portfolio")
        portfolio.save()

        for gallery_index, gallery_id in enumerate(data):
            gallery_data = data[gallery_id]

            self.stdout.write("Importing {id}".format(id=gallery_id))

            try:
                gallery = Gallery.objects.get(slug=gallery_id)
            except Gallery.DoesNotExist:
                gallery = Gallery(slug=gallery_id)

            gallery.name = gallery_data.get('name', "{id} (imported)".format(id=gallery_id))
            gallery.synopsis = gallery_data.get('synopsis')
            gallery.abstract = gallery_data.get('abstract-id')

            media_json = gallery_data.get('media', dict())

            gallery.save()

            portfolio_gallery = PortfolioGallery(portfolio=portfolio, gallery=gallery)
            portfolio_gallery.save()

            for media_index, media_id in enumerate(media_json):
                self.stdout.write("\t{id}".format(id=media_id))

                media_data = media_json[media_id]

                media = Media()
                media.sort_order = media_index
                media.title = media_id
                media.caption = media_data.get('caption')

                media_type = media_data.get('type')

                if media_type == 'video-youtube':
                    media.media_type = 'external-video'
                    video_id = media_data.get('youtube-video-id')
                    thumbnail_id = media_data.get('thumbnail')
                    thumbnail_path = os.path.join(basepath, gallery_id, THUMB_DIR, thumbnail_id)

                    if video_id:
                        media.link = 'https://youtu.be/{video_id}'.format(video_id=video_id)

                    with open(thumbnail_path, 'r') as thumbnail_file:
                        media.thumbnail.save(
                            thumbnail_id,
                            File(thumbnail_file)
                        )
                else:
                    media.media_type = 'image'
                    image_path = os.path.join(basepath, gallery_id, FULL_DIR, media_id)
                    thumbnail_path = os.path.join(basepath, gallery_id, THUMB_DIR, media_id)

                    with open(image_path, 'r') as image_file:
                        media.image.save(
                            media_id,
                            File(image_file)
                        )

                    with open(thumbnail_path, 'r') as thumbnail_file:
                        media.thumbnail.save(
                            media_id,
                            File(thumbnail_file)
                        )

                print_dimensions = media_data.get('print-dimensions')

                if print_dimensions:
                    w, h = print_dimensions
                    media.extra = u"{w}\u2033 \u00D7 {h}\u2033".format(w=w, h=h)

                media.save()

                gallery_media = GalleryMedia(gallery=gallery, media=media)
                gallery_media.save()
