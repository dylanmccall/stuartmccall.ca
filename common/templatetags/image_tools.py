from django.template import Library
from django.utils.html import format_html_join

from common.utils import get_image_style

register = Library()

@register.filter
def image_style(image, style_str):
    image_dict = get_image_style(image, style_str)

    if image_dict:
        image_default = image_dict.get('default', {})
        srcset = []

        for image_variant in image_dict.get('sizes'):
            srcset.append('{src} {x}'.format(
                src=image_variant.get('src'),
                x=image_variant.get('x')
            ))

        attrs = {
            'src': image_default.get('src'),
            'width': image_default.get('width'),
            'height': image_default.get('height'),
            'srcset': str(', ').join(srcset)
        }

        return format_html_join(' ', '{}="{}"', attrs.items())
    else:
        return ''

@register.filter
def image_src(image, style_str):
    image_dict = get_image_style(image, style_str)

    if image_dict:
        image_default = image_dict.get('default', {})
        return image_default.get('src')
    else:
        return None
