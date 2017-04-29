from django.conf.urls import include, url
from django.views.generic.base import RedirectView

from common import views

urlpatterns = [
    url(r'^$', views.PortfolioView.as_view(), name="index"),
    url(r'gallery-data.js$', views.PortfolioDataView.as_view(), name="gallery_data_json"),
    url(r'(?P<gallery_slug>[\w-]+)/$', views.PortfolioView.as_view(), name="gallery")
]
