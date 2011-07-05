import facebook

from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from panomena_general.utils import class_from_string, SettingsFetcher, \
    json_response, is_ajax_request


settings = SettingsFetcher('facebook')


def register(request):
    """Handles the registration of a user that is already
    logged in to facebook.
    
    """
    context = RequestContext(request)
    # retrieve facebook data from cookie
    app_id = settings.FACEBOOK_APP_ID
    secret_key = settings.FACEBOOK_SECRET_KEY
    fbdata = facebook.get_user_from_cookie(request.COOKIES, app_id, secret_key)
    if fbdata is None:
        context['message'] = _('No Facebook data found in cookie. You have ' \
            'porbably denied the Facebook application access to you account ' \
            'or have not logged in.')
        return render_to_response('facebook/failed.html', context)
    # get some user data
    try:
        graph = facebook.GraphAPI(fbdata['access_token'])
        fb_user_data = graph.get_object('me')
    except facebook.GraphAPIError, e:
        context['message'] = e.message
        return render_to_response('facebook/failed.html', context)
    # attempt to authenticate the user with uid and access token
    user = authenticate(
        uid=fbdata['uid'],
        oauth_access_token=fbdata['access_token']
    )
    # redirect existing user
    if user:
        login(request, user)
        return redirect(settings.LOGIN_REDIRECT_URL)
    # retrieve the form class to use from settings
    form_class = settings.FACEBOOK_REGISTER_FORM
    form_class = class_from_string(form_class)
    # handle the form post
    if request.method == 'POST':
        form = form_class(fbdata, fb_user_data, request.POST, user=user)
        if form.is_valid():
            user = form.save()
            user = authenticate(
                uid=fbdata['uid'],
                oauth_access_token=fbdata['access_token'],
            )
            login(request, user)
            url = settings.LOGIN_REDIRECT_URL
            return redirect(url)
    else:
        form = form_class(fbdata, fb_user_data, user=user)
    context.update({
        'form': form,
        'fb_user_data': fb_user_data,
    })
    return render_to_response('facebook/register.html', context)


@login_required
def share(request):
    """Shares content on facebook using the logged in users account."""
    fb = request.facebook
    connected = (fb.uid is not None)
    # get the url to redirect to
    next_url = request.REQUEST.get('next', None)
    if next_url is None:
        next_url = request.META.get('HTTP_REFERER', '/')
    # attempt to create the post
    success = False
    try:
        link_url = request.REQUEST.get('url', None)
        if link_url:
            link_url = request.build_absolute_uri(link_url)
            fb.graph.put_object('me', 'links', link=link_url)
            success = True
    except facebook.GraphAPIError:
        pass
    # redirect to facebook settings page if not connected
    if not connected:
        url = reverse('facebook_register') + '?next=' + next_url
        return redirect(url)
    # response appropriately to the request
    ajax = is_ajax_request(request)
    if ajax:
        return json_response({'success': success})
    else:
        return redirect(next_url)
