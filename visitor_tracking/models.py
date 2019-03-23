from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _

class GoogleAnalytics(models.Model):
    class Meta:
        verbose_name = _("google analytics tracking code")
        verbose_name_plural = _("google analytics tracking codes")

    site = models.OneToOneField(Site, related_name='+', on_delete=models.CASCADE)
    tracking_code = models.CharField(max_length=100)
