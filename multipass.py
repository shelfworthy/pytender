"""Library for implementing Multipass for Tenderapp.
(c) http://bitbucket.org/mtrichardson/tender-multipass/
"""

import base64
import hashlib
from itertools import izip, cycle

try:
    import json
except ImportError:
    import simplejson as json

from M2Crypto import EVP


class MultiPass(object):

    def __init__(self, site_key, api_key):
        secret = hashlib.sha1(api_key + site_key).digest()[:16]
        # Yes, really.
        self.iv = "OpenSSL for Ruby"
        self.aes = EVP.Cipher("aes_128_cbc", key=secret,
            iv=self.iv, op=1)

    def handle_xor(self, raw_string):
        """Double XOR the first block"""
        data = list(raw_string)
        new_data = [chr(ord(x) ^ ord(y)) for (x, y)
            in izip(raw_string[:16], cycle(self.iv))]
        data[:16] = new_data
        return ''.join(data)

    def encode(self, data):
        """Turns a dictionary into urlquoted base64'd encrypted JSON data.

        >>> import datetime
        >>> import tender_multipass
        >>> multipass = tender_multipass.MultiPass("some_site", "some_key")
        >>> expires = datetime.datetime(2009, 10, 19, 20, 07) + datetime.timedelta(days=14)
        >>> data = {"name": "Michael", "email": "michael@mtrichardson.com", "expires": expires.strftime("%Y-%m-%dT%H:%M")}
        >>> multipass.encode(data)
        '4rdsKqcXzJVqbltYJdayy6lIkwtl7vAivlgyDkWCfORWze5HrvfuarBh8Yvkush8cOywmDG4y4M9%0A6vuIyAIWskXOpUaCT/%2BzQ%2BJU8Jf0u0X7%2BbTwjdWyzub6srayFyKn%0A'

        """
        raw_string = json.dumps(data)
        raw_string = self.handle_xor(raw_string)
        v = self.aes.update(raw_string)
        v += self.aes.final()
        return base64.urlsafe_b64encode(v)