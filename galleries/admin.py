from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from orderable.admin import OrderableAdmin, OrderableTabularInline

from common.templatetags.image_tools import image_style

from galleries import models

import os


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
            return _image_preview(obj.gallery.featured_thumbnail)
        else:
            return None
    gallery_preview.short_description = _("Preview")


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
            return _image_preview(obj.media.featured_thumbnail)
        else:
            return None
    media_preview.short_description = _("Preview")


@admin.register(models.Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('title', 'site')
    list_filter = (
        'site',
    )
    readonly_fields = (
        'created_date',
        'modified_date',
    )
    inlines = [
        PortfolioGalleryInline,
    ]


@admin.register(models.Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('gallery_preview', 'name',)
    list_display_links = ('gallery_preview', 'name',)
    list_filter = (
        'portfoliogallery__portfolio',
    )
    inlines = [
        GalleryMediaInline,
    ]

    def gallery_preview(self, obj):
        return _image_preview(obj.featured_thumbnail)
    gallery_preview.short_description = _("Preview")


@admin.register(models.Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('media_preview', 'title', 'media_id',)
    list_display_links = ('media_preview', 'title',)
    list_filter = (
        'media_type',
        'gallerymedia__gallery'
    )
    fieldsets = (
        (None, {
            'fields': ('title', 'media_type', 'thumbnail',)
        }),
        ("Image", {
            'fields': ('image',)
        }),
        ("Video", {
            'fields': ('link',)
        }),
        ("Details", {
            'fields': ('caption', 'extra', 'created_date', 'modified_date',)
        })
    )
    readonly_fields = ('created_date', 'modified_date',)

    def media_preview(self, obj):
        return _image_preview(obj.featured_thumbnail)
    media_preview.short_description = _("Preview")

    def media_id(self, obj):
        if obj.image:
            return os.path.basename(obj.image.name)
        elif obj.link:
            return obj.link
        else:
            return None
    media_id.short_description = _("ID")


def _image_preview(image, size=80):
    if image:
        return format_html(
            '<img class="admin-preview" alt="" {attrs} />',
            attrs=image_style(image, 'thumb')
        )
    else:
        return None
