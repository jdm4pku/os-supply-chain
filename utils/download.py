import re
import zlib
import hashlib


def hash_url(url):
    """Return a hash of the url"""
    return hashlib.md5(url.encode('utf-8')).hexdigest()


def dir_name(url):
    """Return a hash of the url"""
    _url = re.sub(r'https?://[a-zA-Z\-\.]+/', '', url)
    return re.sub(r'[^a-zA-Z0-9]', '_', _url).strip('_')


def decompress_stream(stream):
    o = zlib.decompressobj(16 + zlib.MAX_WBITS)
    for chunk in stream:
        yield o.decompress(chunk)
    yield o.flush()