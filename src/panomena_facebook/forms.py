from panomena.accounts.forms import BaseProfileForm

from models import FacebookProfile


class BaseFacebookRegisterForm(BaseProfileForm):

    def __init__(self, facebook_data, *args, **kwargs):
        self.facebook_data = facebook_data
        super(BaseFacebookRegisterForm, self).__init__(*args, **kwargs)

    def save(self):
        """Creates and attaches a facebook profile to the user object if
        one is not found.
        
        """
        user = super(BaseFacebookRegisterForm, self).save()
        try:
            user.facebook_profile
        except FacebookProfile.DoesNotExist:
            fbdata = self.facebook_data
            FacebookProfile.objects.create(
                user=user,
                uid=fbdata['uid'],
                oauth_access_token=fbdata['access_token'],
            )
        return user

