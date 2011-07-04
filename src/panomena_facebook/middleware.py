import facebook

from django.conf import settings


class Facebook(object):
    """Utility object for working with facebook graph."""

    def __init__(self, user=None):
        if user is None:
            self.uid = None
        else:
            self.uid = user['uid']
            self.user = user
            self.graph = facebook.GraphAPI(user['access_token'])


class FacebookMiddleware(object):
    """Middleware object for picking up facebook data and using it if found.
    Requires django authentication middleware for automatic authentication
    and login.
    
    """

    def process_request(self, request):
        """Enables ``request.facebook`` and ``request.facebook.graph`` in
        your views once the user authenticated the  application and
        connected with facebook. 

        """
        # attempt to fetch facebook user data from the cookies
        fb_user = facebook.get_user_from_cookie(request.COOKIES,
            settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY)
        # setup the facebook object if user was found
        request.facebook = Facebook(fb_user)
        # return if user is already authenticated
        #if hasattr(request, 'user'):
        #    if request.user.is_authenticated():
        #        return None
        #    # attempt to authenticate and log user in
        #    if fb_user is not None:
        #        user = authenticate(
        #            uid=fb_user['uid'],
        #           oauth_access_token=fb_user['access_token'],
        #        )
        #        if user: login(request, user)
        return None

