from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


urlpatterns = patterns('panomena_facebook.views',
    url(r'^register/$', 'register', {}, 'facebook_register'),
    url(r'^failed/$', direct_to_template,
        {'template': 'facebook/failed.html'}, 'facebook_failed'),
    url(r'^share/$', 'share', {}, 'facebook_share'),
    url(r'^settings/$', 'facebook_settings', {}, 'facebook_settings'),
    url(r'^disable/$', 'disable', {}, 'facebook_disable'),
)
