from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, TemplateView

from galleries import models

from common.utils import compress_image

from collections import OrderedDict

try:
    from urlparse import urlparse, parse_qs
except ImportError:
    from urllib.parse import urlparse, parse_qs


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
        else:
            all_galleries = list(portfolio.get_all_galleries())

        gallery_slug = kwargs.get('gallery_slug')

        if gallery_slug:
            selected_gallery = next((x for x in all_galleries if x.slug == gallery_slug), None)
        else:
            selected_gallery = None

        context['portfolio'] = portfolio
        context['all_galleries'] = all_galleries
        context['selected_gallery'] = selected_gallery

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if kwargs.get('gallery_slug') and not context.get('selected_gallery'):
            index_url = reverse('index')
            return HttpResponseRedirect(index_url)
        else:
            return self.render_to_response(context)


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
                if media.media_type == 'image':
                    media_obj = self._media_obj_image(media)
                elif media.media_type == 'external-video':
                    media_obj = self._media_obj_external_video(media)
                else:
                    media_obj = None

                if media_obj:
                    media_list.append(media_obj)

            galleries_dict[gallery.slug] = {
                'synopsis': gallery.synopsis,
                'abstractId': 'abstract-{slug}'.format(slug=gallery.slug),
                'media': media_list
            }

        context['galleries_dict'] = galleries_dict
        return context

    def _media_obj_image(self, media):
        result = {
            'title': media.title,
            'captionHtml': media.caption,
            'extraHtml': media.extra,
        }

        if media.image:
            result['full'] = self._compress_full(media.image)

        if media.thumbnail:
            result['thumb'] = self._compress_thumbnail(media.thumbnail)

        return result

    def _media_obj_external_video(self, media):
        result = {
            'title': media.title,
            'captionHtml': media.caption,
            'extraHtml': media.extra,
        }

        if media.link:
            url = urlparse(media.link)

            if url.hostname == 'youtube.com':
                params = parse_qs(url.query)
                result['type'] = 'video-youtube'
                result['youtube-video-id'] = params['v']
            elif url.hostname == 'youtu.be':
                result['type'] = 'video-youtube'
                result['youtube-video-id'] = url.path.lstrip('/')

        result['full'] = {
            'width': 640,
            'height': 360
        }

        if media.thumbnail:
            result['thumb'] = self._compress_thumbnail(media.thumbnail)

        return result

    def _compress_full(self, image):
        result = {}

        ratio = image.width / float(image.height)

        if ratio >= 2.0:
            return compress_image(image, height=400, srcset=[1, 1.5], quality=95)
        else:
            return compress_image(image, width=650, height=650, srcset=[1, 1.5], quality=95)

    def _compress_thumbnail(self, image):
        return compress_image(image, width=80, height=80, crop='center', quality=95)
