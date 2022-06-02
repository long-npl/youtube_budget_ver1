import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import json
import os
import sys

zzz = b'8Q9u6dA9QnZlhn-dEb0TFtAsI8BcpZKCg2xuGP3X9Cc='


def base_key():
    sss = "J_qkrREZf9CC_4nYmLYfA0d8GKzQY_iGzs2TU4VPnFxHvKYgyeLNn7FCrHTphmDZiNZx0K".encode("UTF-16")
    salt = "Pzs2js-0E-0lhVBqd5cDPNljphSfx7uJ-DPRXPp1IHg34KlNOokvvFpdlH-iuTnihBwz067PbjaiNLjO8".encode("UTF-16")

    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())

    zzz = base64.urlsafe_b64encode(kdf.derive(sss))

    return Fernet(zzz)


def encrypt(bb):
    """
    :param bb: binary
    :return: encrypted binary
    """

    return Fernet(zzz).encrypt(bb)  # RETURN BINARY


def decrypt(s):
    """
    :param s: string
    :return: decrypted binary
    """

    return Fernet(zzz).decrypt(s)  # RETURN BINARY


def load_cookies(file):
    if os.path.exists(file):
        with open(file, "rb") as f:
            bts = f.read()

        return json.loads(decrypt(bts).decode("UTF-16"))

    else:
        return None


def save_cookies(driver, file):
    try:
        cookies = driver.get_cookies()

        os.makedirs(os.path.split(file)[0], exist_ok=True)

        with open(file, "wb") as f:
            f.write(encrypt(json.dumps(cookies).encode("UTF-16")))
    except:
        pass


def save_cookies_by_json(file, cookies):
    try:
        os.makedirs(os.path.split(file)[0], exist_ok=True)

        with open(file, "wb") as f:
            f.write(encrypt(json.dumps(cookies).encode("UTF-16")))
    except:
        pass


def ck_path(*args):
    return os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "Ifmt", "_".join(args) + ".txt")


def ck_vnd_path(*args):
    return os.path.join(r"\\vnd\share\02_共有資料\[RPA_他]\Navigator", "_".join(args) + ".txt")
