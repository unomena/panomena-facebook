import json

from django import template
from django.conf import settings
from django.utils.http import urlquote
from django.utils.safestring import mark_safe
from django.template import TemplateSyntaxError
from django.template.loader import render_to_string

from panomena_general.utils import parse_kw_args, get_setting
from panomena_general.exceptions import RequestContextRequiredException

from panomena_facebook.utils import build_app_url
from panomena_facebook.exceptions import FacebookMiddlewareRequiredException


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
    """Facebook connect button tag."""
    return {
        'MEDIA_URL': context['MEDIA_URL'],
        'image_url': image_url,
    }


@register.inclusion_tag('facebook/share.html', takes_context=True)
def facebook_share(context, cls, url):
    """Facebook share button tag."""
    # get the request
    request = context.get('request')
    if request is None:
        raise RequestContextRequiredException('facebook share tag')
    # get the facebook middleware object
    fb = getattr(request, 'facebook')
    if fb is None:
        raise FacebookMiddlewareRequiredException('facebook share tag')
    connected = (fb.uid is not None)
    # return the context
    return {
        'cls': cls,
        'url': urlquote(url),
        'current_url': urlquote(request.get_full_path()),
        'connected': connected,
    }


class AppUrlNode(template.Node):
    """Facebook application url tag node."""

    def __init__(self, url, asvar):
        self.url = url
        self.asvar = asvar

    def render(self, context):
        url = self.url.resolve(context)
        asvar = self.asvar
        # build the url
        app_url = build_app_url(url)
        # take appropriate action
        if asvar:
            context[asvar] = app_url
            return ''
        else:
            return app_url


@register.tag
def facebook_app_url(parser, token):
    """Parsing method for facebook application url build node."""
    bits = token.split_contents()
    # check minimum argument count
    if len(bits) < 2:
        raise TemplateSyntaxError('%r takes at least 1 argument.' % bits[0])
    # determine var name if given
    asvar = None
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]
    # return the node
    url = parser.compile_filter(bits[1])
    return AppUrlNode(url, asvar)
