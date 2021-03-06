import facebook

from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from panomena_general.utils import class_from_string, SettingsFetcher, \
    json_response, ajax_redirect, is_ajax_request

from models import FacebookProfile


settings = SettingsFetcher('facebook')


class RegisterView(object):
    """Handles the registration of a user that is already
    logged in to facebook.
    
    """

    def authenticate(self, fbdata):
        """Authenticate and return the user."""
        user = authenticate(
            uid=fbdata['uid'],
            oauth_access_token=fbdata['access_token'],
        )
        return user

    def valid(self, request, form, fbdata):
        """Process a valid registration form."""
        user = form.save()
        user = self.authenticate(fbdata)
        login(request, user)
        # redirect appropriately
        url = form.cleaned_data.get('next') or settings.LOGIN_REDIRECT_URL
        response = ajax_redirect(request, url)
        # return the response
        return response

    def form(self):
        """Return the form class to use in the view."""
        return class_from_string(settings.FACEBOOK_REGISTER_FORM)

    def __call__(self, request):
        """Override to check for facebook data and react accordingly."""
        user = request.user
        context = RequestContext(request)
        # retrieve facebook data from cookie
        app_id = settings.FACEBOOK_APP_ID
        secret_key = settings.FACEBOOK_SECRET_KEY
        fbdata = facebook.get_user_from_cookie(
            request.COOKIES, app_id, secret_key
        )
        if fbdata is None:
            context['message'] = _(u'No Facebook data found in cookie. You ' \
                'have either denied the Facebook application access to your ' \
                'account, have not logged in properly or have cookies ' \
                'disabled on your browser.')
            return render_to_response('facebook/failed.html', context)
        # get facebook user data
        try:
            graph = facebook.GraphAPI(fbdata['access_token'])
            fb_user_data = graph.get_object('me')
        except facebook.GraphAPIError, e:
            context['message'] = e.message
            return render_to_response('facebook/failed.html', context)
        # take specific action on unauthentcated users
        if not user.is_authenticated():
            # attempt to authenticate the user with uid and access token
            user = authenticate(
                uid=fbdata['uid'],
                oauth_access_token=fbdata['access_token']
            )
            # redirect existing user appropriately
            if user:
                login(request, user)
                url = request.REQUEST.get('next') or \
                    settings.LOGIN_REDIRECT_URL
                return ajax_redirect(request, url)
        # handle the form post
        form_class = self.form()
        if request.method == 'POST':
            form = form_class(
                request, fbdata, fb_user_data, request.POST, user=user
            )
            if form.is_valid():
                return self.valid(request, form, fbdata)
        else:
            form = form_class(request, fbdata, fb_user_data, user=user)
        context.update({
            'form': form,
            'fb_user_data': fb_user_data,
        })
        return render_to_response('facebook/register.html', context)


register = RegisterView()


@login_required
def share(request):
    """Shares content on facebook using the logged in users account."""
    fb = request.facebook
    connected = (fb.uid is not None)
    # get the url to redirect to
    next_url = request.REQUEST.get('next', None)
    if next_url is None:
        next_url = request.META.get('HTTP_REFERER', '/')
    # redirect to facebook settings page if not connected
    if not connected:
        url = reverse('facebook_register') + '?next=' + next_url
        return redirect(url)
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
    # response appropriately to the request
    ajax = is_ajax_request(request)
    if ajax:
        return json_response({'success': success})
    else:
        return redirect(next_url)


@login_required
def facebook_settings(request):
    """View for configuring facebook integration and listing friends
    in common between the site and facebook.
    
    """
    settings_form = settings.FACEBOOK_SETTINGS_FORM
    settings_form = class_from_string(settings_form)
    context = RequestContext(request, {})
    user = request.user
    fb = request.facebook
    friends = None
    if request.method == 'POST':
        form = settings_form(request, request.POST, user=user)
        if form.is_valid(): form.save()
    else:
        form = settings_form(request, user=user)
    # collect friends matched between facebook and site
    try:
        connected = (fb.uid is not None)
        if connected:
            fb_friends = fb.graph.get_connections('me', 'friends')
            fb_ids = [f['id'] for f in fb_friends['data']]
            friends = User.objects.filter(facebook_profile__uid__in=fb_ids)
    except facebook.GraphAPIError, e:
        context['message'] = e.message
        return render_to_response('facebook/failed.html', context)
    context.update({
        'form': form,
        'connected': connected,
        'friends': friends,
    })
    return render_to_response('facebook/settings.html', context)


def disable(request):
    """Removes the facebook profile to disable integration."""
    # redirect appropriately
    next = request.REQUEST.get('next', request.META.get('HTTP_REFERER', '/'))
    response = redirect(next)
    # remove cookie
    app_id = settings.FACEBOOK_APP_ID
    response.delete_cookie('fbs_%s' % app_id)
    # delete the profile
    try: request.user.facebook_profile.delete()
    except FacebookProfile.DoesNotExist: pass
    # return the response
    return response
