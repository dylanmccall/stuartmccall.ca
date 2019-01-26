from django.contrib import admin
from django.core.urlresolvers import resolve
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from common.templatetags.image_tools import image_style

from galleries import models

import os


class PortfolioMediaInline(admin.TabularInline):
    model = models.PortfolioMedia
    verbose_name = _("media")
    verbose_name_plural = _("contents")
    extra = 0
    fields = (
        'sort_order',
        'media_preview',
        'media',
        'portfolio',
        'gallery',
    )
    readonly_fields = (
        'media_preview',
    )
    raw_id_fields = (
        'media',
    )

    def media_preview(self, obj):
        if obj.media:
            return _image_preview(obj.media.featured_thumbnail)
        else:
            return None
    media_preview.short_description = _("Preview")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent_object = self.get_parent_object_from_request(request)
        if self.parent_model == models.Portfolio:
            if db_field.name == 'gallery' and parent_object:
                kwargs["queryset"] = models.Gallery.objects.filter(portfolio=parent_object)
            elif db_field.name == 'gallery':
                kwargs["queryset"] = models.Gallery.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_parent_object_from_request(self, request):
        resolved = resolve(request.path_info)
        if resolved.args:
            return self.parent_model.objects.get(pk=resolved.args[0])
        else:
            return None


class PortfolioMediaInlineForGallery(admin.TabularInline):
    model = models.PortfolioMedia
    verbose_name = _("media")
    verbose_name_plural = _("contents")
    extra = 0
    fields = (
        'sort_order',
        'media_preview',
        'media',
        'portfolio_link',
        'gallery',
    )
    readonly_fields = (
        'media_preview',
        'portfolio_link',
        'gallery',
    )
    raw_id_fields = (
        'media',
    )

    def portfolio_link(self, obj):
        if obj.pk and obj.portfolio:
            return _object_link(obj.portfolio)
        else:
            return ''
    portfolio_link.short_description = _("Portfolio")

    def media_preview(self, obj):
        if obj.media:
            return _image_preview(obj.media.featured_thumbnail)
        else:
            return None
    media_preview.short_description = _("Preview")


class PortfolioMediaInlineForMedia(admin.TabularInline):
    model = models.PortfolioMedia
    verbose_name = _("gallery")
    verbose_name_plural = _("galleries")
    extra = 0
    fields = (
        'sort_order',
        'gallery',
        'portfolio_link',
    )
    readonly_fields = (
        'portfolio_link',
    )

    def portfolio_link(self, obj):
        if obj.pk and obj.portfolio:
            return _object_link(obj.portfolio)
        else:
            return ''
    portfolio_link.short_description = _("Portfolio")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        parent_object = self.get_parent_object_from_request(request)
        if self.parent_model == models.Portfolio:
            if db_field.name == 'gallery' and parent_object:
                kwargs["queryset"] = models.Gallery.objects.filter(portfolio=parent_object)
            elif db_field.name == 'gallery':
                kwargs["queryset"] = models.Gallery.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_parent_object_from_request(self, request):
        resolved = resolve(request.path_info)
        if resolved.args:
            return self.parent_model.objects.get(pk=resolved.args[0])
        else:
            return None


class GalleryInline(admin.TabularInline):
    model = models.Gallery
    verbose_name = _("gallery")
    verbose_name_plural = _("galleries")
    extra = 0
    show_change_link = True
    fields = ('sort_order', 'name', 'details_link',)
    readonly_fields = ('details_link',)

    # fieldsets = (
    #     (None, {
    #         'classes': ('smc-tabular-rows',),
    #         'fields': (('sort_order', 'name', 'thumbnail',),)
    #     }),
    #     ("Details", {
    #         'classes': ('collapse',),
    #         'fields': ('synopsis', 'abstract',)
    #     }),
    # )

    def details_link(self, obj):
        if obj.pk:
            return _object_link(obj, label=_("Gallery details"))
        else:
            return ''
    details_link.short_description = _("Change")

    def has_delete_permission(self, request, obj):
        return False


@admin.register(models.Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('title', 'site', 'modified_date',)
    list_filter = (
        'site',
        'modified_date',
    )
    prepopulated_fields = {
        'slug': ('title',)
    }
    fields = (
        'site',
        'title',
        'subtitle',
        'slug',
        'blurb',
        'theme_id',
        'created_date',
        'modified_date',
    )
    readonly_fields = (
        'created_date',
        'modified_date',
    )
    inlines = [
        GalleryInline,
        PortfolioMediaInline,
    ]


@admin.register(models.Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('gallery_preview', 'name', 'portfolio', 'modified_date',)
    list_display_links = ('gallery_preview', 'name',)
    list_filter = (
        'portfolio',
        'modified_date',
    )
    search_fields = ['slug', 'name']
    prepopulated_fields = {
        'slug': ('name',)
    }
    fields = (
        'name',
        'slug',
        'portfolio',
        'synopsis',
        'abstract',
        'thumbnail',
        'created_date',
        'modified_date',
    )
    readonly_fields = (
        'created_date',
        'modified_date',
    )
    inlines = [
        PortfolioMediaInlineForGallery,
    ]

    def gallery_preview(self, obj):
        return _image_preview(obj.featured_thumbnail)
    gallery_preview.short_description = _("Preview")


@admin.register(models.Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('media_preview', '__str__', 'image_dimensions', 'modified_date',)
    list_display_links = ('media_preview', '__str__',)
    list_filter = (
        'media_type',
        'portfoliomedia__gallery',
        'modified_date',
    )
    search_fields = ['name', 'caption', 'image', 'link', 'portfoliomedia__gallery__slug', 'portfoliomedia__gallery__name']
    fieldsets = (
        (None, {
            'fields': ('name', 'media_type', 'thumbnail',)
        }),
        ("Image", {
            'fields': ('image', 'image_dimensions',)
        }),
        ("Video", {
            'fields': ('link',)
        }),
        ("Details", {
            'fields': ('caption', 'extra', 'created_date', 'modified_date',)
        })
    )
    readonly_fields = (
        'image_dimensions',
        'created_date',
        'modified_date',
    )
    inlines = [
        PortfolioMediaInlineForMedia,
    ]

    def media_preview(self, obj):
        return _image_preview(obj.featured_thumbnail)
    media_preview.short_description = _("Preview")

    def image_dimensions(self, obj):
        if obj.media_type == 'image' and obj.image_width and obj.image_height:
            return "{}\u00D7{}".format(obj.image_width, obj.image_height)
        else:
            return None
    image_dimensions.short_description = _("Dimensions")


def _image_preview(image, size=80):
    if image:
        return format_html(
            '<img class="admin-preview" alt="" {attrs} />',
            attrs=image_style(image, 'thumb')
        )
    else:
        return None

def _object_link(obj, label=None):
    url = reverse(
        'admin:{app}_{model}_change'.format(
            app=obj._meta.app_label,
            model=obj._meta.model_name
        ),
        args=[obj.id]
    )
    return format_html(
        '<strong><a class="changelink" href="{url}">{label}</a></strong>',
        url=url,
        label=label or str(obj)
    )
