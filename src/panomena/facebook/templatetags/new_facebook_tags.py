import json

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from panomena.general.utils import parse_kw_args, get_setting


register = template.Library()


@register.filter
def jsonify(value):
    """Filter that jsonfies a value."""
    return mark_safe(json.dumps(value))


@register.tag
def facebook_init(parser, token):
    """Parser function for FacebookJsNode."""
    bits = token.split_contents()
    kwargs = dict(parse_kw_args(bits[0], bits[1:]))
    return FacebookInitNode(**kwargs)


class FacebookInitNode(template.Node):
    """Template node for rendering the facebook javascript."""
    
    def __init__(self, **kwargs):
        # set the applciation id if not supplied
        if not kwargs.has_key('app_id'):
            kwargs['appId'] = get_setting('FACEBOOK_APP_ID', 'facebook_js tag')
        # convert boolean parameters
        for key, value in kwargs.items():
            if value in ['True', 'False']:
                kwargs[key] = bool(value)
        # cookie argument must be true for server to access data
        kwargs['cookie'] = True
        # set the parameters
        self.params = kwargs

    def render(self, context):
        return render_to_string('facebook/init.html', {
            'params': mark_safe(json.dumps(self.params)),
            'perms': getattr(settings, 'FACEBOOK_PERMISSIONS', None),
        })


@register.inclusion_tag('facebook/connect.html', takes_context=True)
def facebook_connect(context, image_url):
    return {
        'MEDIA_URL': context['MEDIA_URL'],
        'image_url': image_url,
    }

