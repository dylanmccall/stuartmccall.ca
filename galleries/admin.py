from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from markdownx.widgets import AdminMarkdownxWidget
from markdownx.admin import MarkdownxModelAdmin
from orderable.admin import OrderableAdmin, OrderableTabularInline

from sorl.thumbnail import get_thumbnail

from galleries import models


class PortfolioGalleryInline(OrderableTabularInline):
    model = models.PortfolioGallery
    verbose_name = _("gallery")
    verbose_name_plural = _("contents")
    extra = 0
    fields = (
        'sort_order',
        'gallery_preview',
        'portfolio',
        'gallery',
    )
    readonly_fields = (
        'gallery_preview',
    )

    def gallery_preview(self, obj):
        if obj.gallery:
            return _gallery_preview(obj.gallery)
        else:
            return None


class GalleryMediaInline(OrderableTabularInline):
    model = models.GalleryMedia
    verbose_name = _("media item")
    verbose_name_plural = _("contents")
    extra = 0
    fields = (
        'sort_order',
        'media_preview',
        'gallery',
        'media',
    )
    readonly_fields = (
        'media_preview',
    )
    raw_id_fields = (
        'gallery',
        'media',
    )

    def media_preview(self, obj):
        if obj.media:
            return _media_preview(obj.media)
        else:
            return None


@admin.register(models.Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('title', 'site')
    list_filter = (
        'site',
    )
    inlines = [
        PortfolioGalleryInline,
    ]


@admin.register(models.Gallery)
class GalleryAdmin(MarkdownxModelAdmin):
    list_display = ('name', 'gallery_preview',)
    inlines = [
        GalleryMediaInline,
    ]
    widgets = {
        'abstract': AdminMarkdownxWidget
    }

    def gallery_preview(self, obj):
        return _gallery_preview(obj)


@admin.register(models.Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('media_preview', 'title',)
    list_filter = (
        'media_type',
    )

    def media_preview(self, obj):
        return _media_preview(obj)


def _gallery_preview(gallery):
    if gallery.thumbnail:
        return _image_preview(gallery.thumbnail)
    else:
        return None


def _media_preview(media):
    if media.thumbnail:
        return _image_preview(media.thumbnail)
    elif media.image:
        return _image_preview(media.image)
    else:
        return None


def _image_preview(image, size=80):
    # TODO: Return image resized through django-compressor
    geometry = '{size}x{size}'.format(size=size)
    thumbnail = get_thumbnail(image, geometry, crop='center', quality=95)

    return format_html('<img class="admin-preview" src="{url}" width={width} height={height} style="{style}" />',
        url=thumbnail.url,
        width=thumbnail.width,
        height=thumbnail.height,
        style='height: {size}; width: auto'.format(size=size)
    )
