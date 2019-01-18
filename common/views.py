from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.core.urlresolvers import reverse
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, TemplateView

from galleries import models

from common.utils import get_image_style

from collections import OrderedDict
import json
import re

try:
    from urlparse import urlparse, parse_qs
except ImportError:
    from urllib.parse import urlparse, parse_qs


RENDER_VERSION = '2019-01-18.1'


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

    def get(self, request, *args, **kwargs):
        self.portfolio = self.get_portfolio()

        context = self.get_context_data(portfolio=self.portfolio, **kwargs)

        if kwargs.get('gallery_slug') and not context.get('selected_gallery'):
            index_url = reverse('index')
            return HttpResponseRedirect(index_url)
        else:
            return self.render_to_response(context)

    def get_portfolio(self):
        site = get_current_site(self.request)

        try:
            portfolio = models.Portfolio.objects.get_for_site(site)
        except models.Portfolio.DoesNotExist:
            raise Http404(_("There is no portfolio for this site"))
        else:
            return portfolio

    def get_context_data(self, portfolio=None, **kwargs):
        context = super(PortfolioView, self).get_context_data(**kwargs)

        all_galleries = list(portfolio.get_all_galleries())
        all_portfoliomedia = list(portfolio.get_all_portfoliomedia())

        gallery_slug = kwargs.get('gallery_slug')

        if gallery_slug:
            selected_gallery = next((x for x in all_galleries if x.slug == gallery_slug), None)
        else:
            selected_gallery = None

        key = make_template_fragment_key('galleries_js_str', [portfolio.pk, portfolio.modified_date, RENDER_VERSION])
        galleries_js_str = cache.get_or_set(
            key,
            lambda: self._build_galleries_js_str(all_galleries),
            None
        )

        key = make_template_fragment_key('portfoliomedia_js_str', [portfolio.pk, portfolio.modified_date, RENDER_VERSION])
        portfoliomedia_js_str = cache.get_or_set(
            key,
            lambda: self._build_portfoliomedia_js_str(all_portfoliomedia),
            None
        )

        context['portfolio'] = portfolio
        context['all_galleries'] = all_galleries
        context['selected_gallery'] = selected_gallery
        context['galleries_js_str'] = galleries_js_str
        context['portfoliomedia_js_str'] = portfoliomedia_js_str

        return context

    def get_template_names(self):
        if self.portfolio.theme:
            return [
                self.portfolio.theme.get_themed_template_name('artsite/index.html'),
                self.template_name
            ]
        else:
            return super(PortfolioView, self).get_template_names()

    def _build_galleries_js_str(self, gallery_list):
        galleries_js_dict = self._build_galleries_js_dict(gallery_list)
        return json.dumps(galleries_js_dict)

    def _build_galleries_js_dict(self, gallery_list):
        result = OrderedDict()

        for gallery in gallery_list:
            key = make_template_fragment_key('gallery_js_dict', [gallery.pk, gallery.modified_date, RENDER_VERSION])
            result[gallery.slug] = cache.get_or_set(
                key,
                lambda: self._build_galleries_js_dict_item(gallery),
                None
            )

        return result

    def _build_galleries_js_dict_item(self, gallery):
        return {
            'synopsis': gallery.synopsis,
            'abstractId': 'abstract-{slug}'.format(slug=gallery.slug)
        }

    def _build_portfoliomedia_js_str(self, portfoliomedia_list):
        portfoliomedia_js_dict = self._build_portfoliomedia_js_dict(portfoliomedia_list)
        return json.dumps(portfoliomedia_js_dict)

    def _build_portfoliomedia_js_dict(self, portfoliomedia_list):
        result = list()

        for portfoliomedia in portfoliomedia_list:
            key = make_template_fragment_key('portfoliomedia_js_dict', [portfoliomedia.pk, portfoliomedia.modified_date, RENDER_VERSION])
            result.append(cache.get_or_set(
                key,
                lambda: self._build_portfoliomedia_js_dict_item(portfoliomedia),
                None
            ))

        return result

    def _build_portfoliomedia_js_dict_item(self, portfoliomedia):
        media_obj = self._build_media_obj(portfoliomedia.media)

        return {
            'gallery': portfoliomedia.gallery.slug,
            **media_obj
        }

    def _build_media_obj(self, media):
        if media.media_type == 'image':
            media_obj_inner = self._build_media_obj_image(media)
        elif media.media_type == 'external-video':
            media_obj_inner = self._build_media_obj_external_video(media)
        else:
            media_obj_inner = dict()

        return {
            'caption': media.caption,
            'extraHtml': _format_extra_dimensions(media.extra),
            **media_obj_inner
        }


    def _build_media_obj_image(self, media):
        result = dict()

        result['type'] = 'picture'

        if media.image:
            if media.image_ratio >= 2.0:
                result['full'] = get_image_style(media.image, 'full--pano')
            else:
                result['full'] = get_image_style(media.image, 'full')

        if media.featured_thumbnail:
            result['thumb'] = get_image_style(media.featured_thumbnail, 'thumb')

        return result

    def _build_media_obj_external_video(self, media):
        result = dict()

        if media.featured_thumbnail:
            result['thumb'] = get_image_style(media.featured_thumbnail, 'thumb')

        if media.link:
            url = urlparse(media.link)

            if url.hostname in ('youtube.com', 'www.youtube.com'):
                params = parse_qs(url.query)
                video_type = 'video-youtube'
                video_id = params['v']
            elif url.hostname in ('youtu.be', 'www.youtu.be'):
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


DIMENSION_PATTERN = re.compile(r'(\d+)[\"\u201d\u2033]?\s?[xX*\u00d7]\s?(\d+)[\"\u201d\u2033]?')

def _format_extra_dimensions(text):
    if text:
        return DIMENSION_PATTERN.sub(_dimension_re_replace, text)
    else:
        return text

def _dimension_re_replace(match):
    n1, n2 = match.groups()
    return "{}\u2033 \u00d7 {}\u2033".format(n1, n2)
