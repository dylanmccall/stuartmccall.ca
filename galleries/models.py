from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from orderable.models import Orderable


class Gallery(models.Model):
    class Meta:
        verbose_name = 'Gallery'
        verbose_name_plural = 'Galleries'

    slug = models.CharField(max_length=30)
    name = models.CharField(max_length=100)
    synopsis = models.TextField(blank=True, null=True)
    abstract = models.TextField(blank=True, null=True)
    thumbnail = models.ImageField(blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('gallery', kwargs={'gallery_slug': self.slug})


class Media(Orderable):
    class Meta:
        verbose_name = 'Media'
        verbose_name_plural = 'Media items'

    MEDIA_TYPES = (
        ('image', _("Image")),
        ('external-video', _("Video")),
    )

    gallery = models.ForeignKey(Gallery)
    title = models.CharField(max_length=100)
    media_type = models.CharField(choices=MEDIA_TYPES, max_length=100, default='image')
    thumbnail = models.ImageField(blank=True)
    image = models.ImageField(blank=True)
    link = models.URLField(blank=True, null=True)
    caption = models.TextField(max_length=200, blank=True, null=True)
    extra = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{} in {}".format(self.title, self.gallery)
