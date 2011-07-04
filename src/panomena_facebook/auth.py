from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from panomena_facebook.models import FacebookProfile


class FacebookAuth(object):
    """Authentication backend for a Facebook profile."""
    
    def authenticate(self, uid=None, oauth_access_token=None):
        """Authenticate using the facebook user id and sets the
        open auth access token.
        
        """
        try:
            profile = FacebookProfile.objects.get(
                uid=uid,
                site=Site.objects.get_current()
            )
            profile.oauth_access_token = oauth_access_token
            profile.save()
            return profile.user
        except FacebookProfile.DoesNotExist:
            return None

    def get_user(self, user_id):
        """Required function for django admin."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
