import json
import hmac
import hashlib

from panomena_general.utils import base64_url_decode


def parse_signed_request(signed_request, secret):
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

