import os

from django.utils.translation import ugettext_lazy as _


class SiteTheme(object):
    def __init__(self, templates_dir):
        self.templates_dir = templates_dir

    def get_themed_template_name(self, template_name):
        return os.path.join(self.templates_dir, template_name)


SITE_THEME_OPTIONS = [
    ('stuartmccall_ca', 'stuartmccall.ca'),
    ('northlightimages_com', 'northlightimages.com')
]

SITE_THEMES = {
    'stuartmccall_ca': SiteTheme(
        templates_dir=os.path.join('sitetheme_stuartmccall_ca')
    ),
    'northlightimages_com': SiteTheme(
        templates_dir=os.path.join('sitetheme_northlightimages_com')
    )
}
