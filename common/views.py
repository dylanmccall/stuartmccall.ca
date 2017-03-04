from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, TemplateView

from galleries import models

from collections import OrderedDict


class JsonResponseMixin(object):
    # From https://docs.djangoproject.com/en/1.10/topics/class-based-views/mixins/#jsonresponsemixin-example

    def render_to_json_response(self, context, **response_kwargs):
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        return context


class GalleryView(TemplateView):
    template_name = 'artsite/index.html'

    def get_context_data(self, **kwargs):
        context = super(GalleryView, self).get_context_data(**kwargs)

        context['galleries'] = models.Gallery.objects.all()

        return context


class GalleriesDataView(ListView):
    model = models.Gallery

    template_name = 'artsite/gallery-data.js'

    def get_context_data(self, **kwargs):
        context = super(GalleriesDataView, self).get_context_data(**kwargs)

        galleries_dict = OrderedDict()

        for gallery in context['gallery_list'].all():
            media_list = []

            for media in gallery.media_set.all():
                # TODO: process Markdown

                media_obj = {
                    'title': media.title,
                    'caption_html': media.caption,
                    'extra_html': media.extra,
                }

                if media.image:
                    media_obj['full'] = {
                        'w': media.image.width,
                        'h': media.image.height,
                        'src': media.image.url
                    }

                if media.thumbnail:
                    media_obj['thumb'] = {
                        'w': media.image.width,
                        'h': media.image.height,
                        'src': media.image.url
                    }

                media_list.append(media_obj)

            galleries_dict[gallery.slug] = {
                'synopsis': gallery.synopsis,
                'media': media_list
            }

        context['galleries_dict'] = galleries_dict
        return context
