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

        galleries_js_dict = self._get_galleries_js_dict(all_galleries)

        context['portfolio'] = portfolio
        context['all_galleries'] = all_galleries
        context['selected_gallery'] = selected_gallery
        context['galleries_js_dict'] = galleries_js_dict

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if kwargs.get('gallery_slug') and not context.get('selected_gallery'):
            index_url = reverse('index')
            return HttpResponseRedirect(index_url)
        else:
            return self.render_to_response(context)

    def _get_galleries_js_dict(self, galleries_list):
        result = OrderedDict()

        for gallery in galleries_list:
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

            result[gallery.slug] = {
                'synopsis': gallery.synopsis,
                'abstractId': 'abstract-{slug}'.format(slug=gallery.slug),
                'media': media_list
            }

        return result

    def _media_obj_image(self, media):
        result = {
            'title': media.title,
            'captionHtml': media.caption,
            'extraHtml': media.extra,
        }

        result['type'] = 'picture'

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

        if media.thumbnail:
            result['thumb'] = self._compress_thumbnail(media.thumbnail)

        if media.link:
            url = urlparse(media.link)

            if url.hostname == 'youtube.com':
                params = parse_qs(url.query)
                video_type = 'video-youtube'
                video_id = params['v']
            elif url.hostname == 'youtu.be':
                video_type = 'video-youtube'
                video_id = url.path.lstrip('/')
            else:
                video_id = None

            if video_id:
                result['type'] = video_type
                result['full'] = {
                    'default': {
                        'videoId': video_id,
                        'width': 640,
                        'height': 360
                    }
                }

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
