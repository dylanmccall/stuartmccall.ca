from django.contrib.sites.shortcuts import get_current_site
from django.template import Library

from visitor_tracking import models

register = Library()

@register.filter
def site_google_analytics_id(request):
    current_site = get_current_site(request)
    try:
        google_analytics = models.GoogleAnalytics.objects.get(site=current_site)
    except models.GoogleAnalytics.DoesNotExist:
        return None
    else:
        return google_analytics.tracking_code
