import hashlib
import os

BASE_URL = os.environ["LAS_BASE_URL"]
SECRET = os.environ["LAS_SECRET"]


def get_hook_key(service, identifier):
    nonce = (service + SECRET + identifier).encode("ascii")
    return hashlib.sha256(nonce).hexdigest()


def get_hook_url(service, identifier):
    return f"{BASE_URL}hooks/{service}/{identifier}/{get_hook_key(service, identifier)}"
