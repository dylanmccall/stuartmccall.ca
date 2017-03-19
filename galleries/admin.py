from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from orderable.admin import OrderableAdmin, OrderableTabularInline
from sorl.thumbnail import get_thumbnail

from galleries import models


class MediaInline(OrderableTabularInline):
    model = models.Media
    show_change_link = True
    extra = 0
    fields = ('sort_order', 'media_preview', 'title',)
    readonly_fields = ('media_preview', 'title')

    def media_preview(self, obj):
        if obj.thumbnail:
            return _image_preview(obj.thumbnail, 50)
        elif obj.image:
            return _image_preview(obj.image, 50)
        else:
            return None


@admin.register(models.Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'gallery_preview')
    inlines = [
        MediaInline,
    ]

    def gallery_preview(self, obj):
        if obj.thumbnail:
            return _image_preview(obj.thumbnail)
        else:
            return None


@admin.register(models.Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('media_preview', '__str__', 'gallery',)
    list_filter = (
        'gallery',
    )
    readonly_fields = (
        'sort_order',
    )

    def media_preview(self, obj):
        if obj.thumbnail:
            return _image_preview(obj.thumbnail)
        elif obj.image:
            return _image_preview(obj.image)
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
