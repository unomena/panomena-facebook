import json
import hmac
import urllib
import urllib2
import hashlib

from PIL import Image
from StringIO import StringIO

from django.core.files.base import ContentFile

from panomena_general.utils import base64_url_decode, SettingsFetcher

from panomena_facebook import FACEBOOK_GRAPH_URL


settings = SettingsFetcher('panomena facebbok')


def parse_signed_request(signed_request, secret):
    """Parsese the signed request for a facebook application."""
    l = signed_request.split('.', 2)
    encoded_sig = l[0]
    payload = l[1]
    sig = base64_url_decode(encoded_sig)
    data = json.loads(base64_url_decode(payload))
    if data.get('algorithm').upper() != 'HMAC-SHA256':
        return None
    else:
        expected_sig = hmac.new(secret, msg=payload, digestmod=hashlib.sha256).digest()
    if sig != expected_sig:
        return None
    else:
        return data


def build_app_url(url):
    """Builds a application specific url."""
    page_id = settings.FACEBOOK_PAGE_ID
    app_id = settings.FACEBOOK_APP_ID
    return 'http://www.facebook.com/apps/application.php?id=%s&sk=app_%s' \
        '&app_data=%s' % (page_id, app_id, urllib.quote('redirect=' + url))


def fetch_profile_image(uid):
    """Loads the user profile image and places it in a file object."""
    url = FACEBOOK_GRAPH_URL + uid + '/picture'
    response = urllib2.urlopen(url)
    # make the required conversions to the image
    img = Image.open(StringIO(response.read()))
    if img.mode != 'RGB': img = img.convert('RGB')
    buf = StringIO()
    img.save(buf, 'JPEG')
    buf.seek(0)
    # return the content file object
    return ContentFile(buf.read())

