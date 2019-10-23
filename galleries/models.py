from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from simplemde.fields import SimpleMDEField

from common.utils import markdownify, generate_image_styles
from common.site_themes import SITE_THEME_OPTIONS, SITE_THEMES

from sort_order_field.fields import SortOrderField

import os


class PortfolioManager(models.Manager):
    def get_for_site(self, site):
        return self.get(site=site)


class Portfolio(models.Model):
    class Meta:
        verbose_name = _("portfolio")
        verbose_name_plural = _("portfolios")

    site = models.ForeignKey(Site, blank=True, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(max_length=50, blank=True, null=True)
    blurb = SimpleMDEField(blank=True, null=True)
    theme_id = models.CharField(max_length=50, choices=SITE_THEME_OPTIONS, verbose_name=_('theme'))
    meta_description = models.CharField(max_length=500, blank=True, null=True)
    meta_keywords = models.CharField(max_length=500, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    # Reverse reference: gallery_set (0-n)
    # Reverse reference: portfoliomedia_set (0-n)

    objects = PortfolioManager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('index')

    @cached_property
    def blurb_html(self):
        if self.blurb:
            return markdownify(self.blurb)
        else:
            return self.blurb

    def get_all_galleries(self):
        yield from self.gallery_set.all()

    def get_all_portfoliomedia(self):
        yield from self.portfoliomedia_set.select_related('media')

    def get_all_media(self):
        for portfoliomedia in self.get_all_portfoliomedia():
            yield portfoliomedia.media

    @cached_property
    def theme(self):
        return SITE_THEMES.get(self.theme_id)

    @cached_property
    def featured_gallery(self):
        return self.gallery_set.select_related('media').first()


class Gallery(models.Model):
    class Meta:
        verbose_name = _("gallery")
        verbose_name_plural = _("galleries")
        ordering = ['sort_order']

    portfolio = models.ForeignKey(Portfolio, blank=True, null=True, on_delete=models.CASCADE)
    sort_order = SortOrderField(_("Sort"))
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50, blank=True, null=True)
    synopsis = models.CharField(blank=True, null=True, max_length=200)
    abstract = SimpleMDEField(blank=True, null=True)
    thumbnail = models.ImageField(blank=True, upload_to='thumbnail')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    # Reverse reference: portfoliomedia_set (0-n)

    def __str__(self):
        if self.portfolio:
            return "{name} ({portfolio})".format(
                name=self.name,
                portfolio=self.portfolio
            )
        else:
            return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        for portfoliomedia in self.portfoliomedia_set.iterator():
            if portfoliomedia.portfolio != self.portfolio:
                portfoliomedia.portfolio = self.portfolio
                portfoliomedia.save()
        super().save(*args, **kwargs)

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
        portfoliomedia = self.portfoliomedia_set.select_related('media').first()
        return portfoliomedia.media if portfoliomedia else None


class Media(models.Model):
    class Meta:
        verbose_name = _("media")
        verbose_name_plural = _("images and videos")

    MEDIA_TYPES = (
        ('image', _("Image")),
        ('external-video', _("Video")),
    )

    name = models.CharField(blank=True, null=True, max_length=100)
    media_type = models.CharField(choices=MEDIA_TYPES, max_length=100, default='image')
    thumbnail = models.ImageField(blank=True, upload_to='thumbnail')
    image = models.ImageField(blank=True, upload_to='full', width_field='image_width', height_field='image_height')
    image_width = models.PositiveIntegerField(blank=True, null=True, editable=False)
    image_height = models.PositiveIntegerField(blank=True, null=True, editable=False)
    link = models.URLField(blank=True, null=True)
    caption = models.CharField(blank=True, null=True, max_length=200)
    extra = models.TextField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    # Reverse reference: portfoliomedia_set (0-n)

    def __str__(self):
        return "{} - {}".format(self.get_media_type_display(), self.admin_title)

    @cached_property
    def pretty_title(self):
        return self.caption or self.name or _("Untitled")

    @cached_property
    def admin_title(self):
        return self.caption or self.name or self._media_id or self.pk

    @cached_property
    def featured_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail
        elif self.image:
            return self.image
        else:
            return None

    @cached_property
    def image_ratio(self):
        if self.image_height > 0:
            return self.image_width / float(self.image_height)
        else:
            return 0

    @cached_property
    def _media_id(self):
        if self.image:
            return os.path.basename(self.image.name)
        elif self.link:
            return self.link
        else:
            return None

    def generate_image_styles(self):
        if self.image and self.image_ratio >= 2.0:
            generate_image_styles(self.image, ['full--pano'])
        elif self.image:
            generate_image_styles(self.image, ['full'])

        if self.featured_thumbnail:
            generate_image_styles(self.featured_thumbnail, ['thumb'])


class PortfolioMedia(models.Model):
    class Meta:
        verbose_name = _("portfolio media")
        verbose_name_plural = _("portfolio media")
        ordering = ['sort_order']

    portfolio = models.ForeignKey(Portfolio, blank=True, null=True, on_delete=models.CASCADE)
    sort_order = SortOrderField(_("Sort"))
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE)
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.gallery and not self.portfolio:
            self.portfolio = self.gallery.portfolio
        super().save(*args, **kwargs)


# Crudely bump modified_date for related portfolios to break their cache

@receiver(pre_save, sender=Gallery)
def _gallery_bubble_change(sender, instance, **kwargs):
    try:
        old = Gallery.objects.get(pk=instance.pk)
    except Gallery.DoesNotExist:
        old = None
    else:
        if instance.portfolio != old.portfolio and old.portfolio:
            old.portfolio.save()
    if instance.portfolio:
        instance.portfolio.save()

@receiver(pre_save, sender=Media)
def _media_bubble_change(sender, instance, **kwargs):
    all_portfoliomedia_set = set()
    try:
        old = Media.objects.get(pk=instance.pk)
    except Media.DoesNotExist:
        old = None
    else:
        all_portfoliomedia_set.update(old.portfoliomedia_set.iterator())
    all_portfoliomedia_set.update(instance.portfoliomedia_set.iterator())
    for portfoliomedia in all_portfoliomedia_set:
        portfoliomedia.save()

@receiver(pre_save, sender=PortfolioMedia)
def _portfoliomedia_bubble_change(sender, instance, **kwargs):
    try:
        old = PortfolioMedia.objects.get(pk=instance.pk)
    except PortfolioMedia.DoesNotExist:
        old = None
    else:
        if instance.portfolio != old.portfolio and old.portfolio:
            old.portfolio.save()
    if instance.portfolio:
        instance.portfolio.save()

@receiver(post_save, sender=Media)
def _media_generate_image_styles(sender, instance, **kwargs):
    instance.generate_image_styles()
