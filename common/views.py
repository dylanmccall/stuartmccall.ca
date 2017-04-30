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

    def get_queryset(self):
        # Return a list of galleries for the current portfolio.
        # TODO: this should really be a serializer for Portfolio.
        site = get_current_site(self.request)

        try:
            portfolio = models.Portfolio.objects.get_for_site(site)
        except models.Portfolio.DoesNotExist:
            raise Http404(_("There is no portfolio for this site"))

        return self.model.objects.filter(
            portfoliogallery__portfolio=portfolio
        )

    def get_context_data(self, **kwargs):
        context = super(PortfolioDataView, self).get_context_data(**kwargs)

        galleries_dict = OrderedDict()

        for gallery in context['gallery_list']:
            media_list = []

            for media in gallery.get_all_media():
                # TODO: process Markdown

                media_obj = {
                    'title': media.title,
                    'captionHtml': media.caption,
                    'extraHtml': media.extra,
                }

                if media.image:
                    image = self._compress_full(media.image)
                    media_obj['full'] = {
                        'src': image.url,
                        'width': image.width,
                        'height': image.height
                    }

                if media.thumbnail:
                    image = self._compress_thumbnail(media.thumbnail)
                    media_obj['thumb'] = {
                        'width': image.width,
                        'height': image.height,
                        'src': image.url
                    }

                media_list.append(media_obj)

            galleries_dict[gallery.slug] = {
                'synopsis': gallery.synopsis,
                'abstractId': 'abstract-{slug}'.format(slug=gallery.slug),
                'media': media_list
            }

        context['galleries_dict'] = galleries_dict
        return context

    def _compress_full(self, image):
        ratio = image.width / float(image.height)

        if ratio >= 2.0:
            crop = 'x400'
        else:
            crop = '650x650'

        return get_thumbnail(image, crop, quality=95)

    def _compress_thumbnail(self, image):
        return get_thumbnail(image, '80x80', crop='center', quality=95)
