from django.db import models

from django.contrib.auth.models import User
from django.contrib.sites.models import Site


class FacebookProfile(models.Model):
    """Facebook profile detail for a user."""
    user = models.OneToOneField(User, related_name='facebook_profile')
    site = models.ForeignKey(Site, default=Site.objects.get_current, related_name='facebook_profiles')
    uid = models.CharField(max_length=255, blank=False, null=False)
    oauth_access_token = models.CharField(max_length=255, blank=False, null=False)
    
    def __unicode__(self):
        return u'%s: %s' % (self.user, self.uid)

