from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from orderable.admin import OrderableAdmin, OrderableTabularInline

from galleries import models


class MediaInline(OrderableTabularInline):
    model = models.Media
    show_change_link = True
    extra = 1
    fields = ('sort_order', 'title', 'image')


@admin.register(models.Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    inlines = [
        MediaInline,
    ]


@admin.register(models.Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('media_preview', '__str__',)
    list_filter = (
        'gallery',
    )
    readonly_fields = (
        'sort_order',
    )

    def media_preview(self, obj):
        if obj.thumbnail:
            url = obj.thumbnail.url
        elif obj.image:
            url = obj.image.url
        else:
            url = None

        if url:
            # TODO: Return image resized through django-compressor
            return format_html('<img class="admin-preview" src="{url}" style="height: 100px; width: auto" />', url=url)
        else:
            return None
