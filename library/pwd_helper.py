import binascii
import hashlib


def hash_password(password):
    hashed = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), b'pwd', 100000)
    hashed = binascii.hexlify(hashed)
    return hashed.decode('ascii')
