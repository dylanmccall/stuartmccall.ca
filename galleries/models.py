from __future__ import unicode_literals

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from orderable.models import Orderable
from markdownx.models import MarkdownxField

from markdownx.utils import markdownify


class PortfolioManager(models.Manager):
    def get_for_site(self, site):
        return self.get(site=site)


class Portfolio(models.Model):
    class Meta:
        verbose_name = _("portfolio")
        verbose_name_plural = _("portfolios")

    site = models.ForeignKey(Site, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=100)
    blurb = MarkdownxField(blank=True, null=True)

    # Reverse reference: portfoliogallery_set (0-n)

    objects = PortfolioManager()

    @cached_property
    def blurb_html(self):
        if self.blurb:
            return markdownify(self.blurb)
        else:
            return self.blurb

    def get_all_galleries(self):
        for portfoliogallery in self.portfoliogallery_set.select_related('gallery'):
            yield portfoliogallery.gallery

    @cached_property
    def featured_gallery(self):
        portfoliogallery = self.portfoliogallery_set.select_related('media').first()
        if portfoliogallery:
            portfoliogallery.gallery


class Gallery(models.Model):
    class Meta:
        verbose_name = _("gallery")
        verbose_name_plural = _("galleries")

    slug = models.CharField(max_length=30)
    name = models.CharField(max_length=100)
    synopsis = models.TextField(blank=True, null=True)
    abstract = MarkdownxField(blank=True, null=True)
    thumbnail = models.ImageField(blank=True, upload_to='thumbnail')

    # Reverse reference: portfoliogallery_set (0-n)
    # Reverse reference: gallerymedia_set (0-n)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gallery', kwargs={'gallery_slug': self.slug})

    @cached_property
    def abstract_html(self):
        if self.abstract:
            return markdownify(self.abstract)
        else:
            return self.abstract

    @cached_property
    def featured_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail
        elif self.featured_media:
            return self.featured_media.featured_thumbnail
        else:
            return None

    @cached_property
    def featured_media(self):
        gallerymedia = self.gallerymedia_set.select_related('media').first()
        return gallerymedia.media if gallerymedia else None

    def get_all_media(self):
        for gallerymedia in self.gallerymedia_set.select_related('media'):
            yield gallerymedia.media


class Media(models.Model):
    class Meta:
        verbose_name = _("media")
        verbose_name_plural = _("media items")

    MEDIA_TYPES = (
        ('image', _("Image")),
        ('external-video', _("Video")),
    )

    title = models.CharField(max_length=100)
    media_type = models.CharField(choices=MEDIA_TYPES, max_length=100, default='image')
    thumbnail = models.ImageField(blank=True, upload_to='thumbnail')
    image = models.ImageField(blank=True, upload_to='full')
    link = models.URLField(blank=True, null=True)
    caption = models.TextField(max_length=200, blank=True, null=True)
    extra = models.TextField(blank=True, null=True)

    # Reverse reference: gallerymedia_set (0-n)

    def __str__(self):
        return "{} - {}".format(self.get_media_type_display(), self.title)

    @cached_property
    def featured_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail
        elif self.image:
            return self.image
        else:
            return None


class PortfolioGallery(Orderable):
    class Meta(Orderable.Meta):
        verbose_name = _("portfolio gallery")
        verbose_name_plural = _("portfolio galleries")

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE)


class GalleryMedia(Orderable):
    class Meta(Orderable.Meta):
        verbose_name = _("gallery media")
        verbose_name_plural = _("gallery media")

    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE)
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
