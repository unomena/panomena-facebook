import json
import hmac
import urllib
import hashlib

from panomena_general.utils import base64_url_decode, SettingsFetcher


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
