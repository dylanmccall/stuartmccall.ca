from django.utils.html import format_html

from markdown import markdown
from sorl.thumbnail import get_thumbnail

def markdownify(content):
    return markdown(
        text=content,
        extensions=[],
        extension_configs=[]
    )

def compress_image(image, width=None, height=None, srcset=[1, 1.5, 2], **kwargs):
    sizes = []

    for density in srcset:
        density_width = int(density * width) if width else None
        density_height = int(density * height) if height else None

        if density_width and density_height:
            geometry = '{w}x{h}'.format(w=density_width, h=density_height)
        elif density_width:
            geometry = '{w}'.format(w=density_width)
        elif density_height:
            geometry = 'x{h}'.format(h=density_height)
        else:
            geometry = None

        image_variant = get_thumbnail(image, geometry, upscale=False, **kwargs)

        if image_variant.exists():
            sizes.append({
                'x': '{d}x'.format(d=density),
                'src': image_variant.url,
                'width': image_variant.width,
                'height': image_variant.height
            })

    if len(sizes) > 0:
        return {
            'default': sizes[0] if len(sizes) > 0 else None,
            'sizes': sizes
        }
    else:
        return None
