from django.contrib import admin

from visitor_tracking import models

@admin.register(models.GoogleAnalytics)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('site', 'tracking_code',)
    fields = (
        'site',
        'tracking_code',
    )

