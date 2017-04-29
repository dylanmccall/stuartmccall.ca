from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse
from django.http import JsonResponse, Http404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, TemplateView

from sorl.thumbnail import get_thumbnail

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


class PortfolioView(TemplateView):
    template_name = 'artsite/index.html'

    def get_context_data(self, **kwargs):
        context = super(PortfolioView, self).get_context_data(**kwargs)

        site = get_current_site(self.request)

        try:
            portfolio = models.Portfolio.objects.get_for_site(site)
        except models.Portfolio.DoesNotExist:
            raise Http404(_("There is no portfolio for this site"))

        context['portfolio'] = portfolio
        context['galleries'] = list(portfolio.get_all_galleries())

        return context


class PortfolioDataView(ListView):
    model = models.Gallery

    template_name = 'artsite/gallery-data.js'
    content_type = 'application/javascript'

    def get_context_data(self, **kwargs):
        context = super(GalleriesDataView, self).get_context_data(**kwargs)

        galleries_dict = OrderedDict()

        for gallery in context['gallery_list']:
            media_list = []

            for media in gallery.get_all_media():
                # TODO: process Markdown

                media_obj = {
                    'title': media.title,
                    'caption_html': media.caption,
                    'extra_html': media.extra,
                }

                if media.image:
                    thumbnail = get_thumbnail(media.image, '650x650', quality=95)
                    media_obj['full'] = {
                        'src': thumbnail.url,
                        'width': thumbnail.width,
                        'height': thumbnail.height
                    }

                if media.thumbnail:
                    thumbnail = get_thumbnail(media.thumbnail, '80x80', crop='center', quality=95)
                    media_obj['thumb'] = {
                        'width': thumbnail.width,
                        'height': thumbnail.height,
                        'src': thumbnail.url
                    }

                media_list.append(media_obj)

            galleries_dict[gallery.slug] = {
                'synopsis': gallery.synopsis,
                'media': media_list
            }

        context['galleries_dict'] = galleries_dict
        return context
