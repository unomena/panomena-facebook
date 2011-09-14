from panomena_accounts.forms import BaseProfileForm

from panomena_facebook.models import FacebookProfile


class BaseFacebookRegisterForm(BaseProfileForm):

    def __init__(self, request, facebook_data, facebook_user_data, *args, **kwargs):
        self.facebook_data = facebook_data
        self.facebook_user_data = facebook_user_data
        super(BaseFacebookRegisterForm, self).__init__(request, *args, **kwargs)
        # fill fields with facebook data
        self.initial.update(self.get_field_values(facebook_user_data))

    def save(self):
        """Creates and attaches a facebook profile to the user object if
        one is not found.
        
        """
        user = super(BaseFacebookRegisterForm, self).save()
        try:
            user.facebook_profile
        except FacebookProfile.DoesNotExist:
            fbdata = self.facebook_data
            fbuserdata = self.facebook_user_data
            access_token = fbdata.get('oauth_token') \
                or fbdata.get('access_token')
            FacebookProfile.objects.create(
                user=user,
                uid=fbuserdata['id'],
                oauth_access_token=access_token,
            )
        return user

