import binascii
import hashlib
import os


def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    hashed = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    hashed = binascii.hexlify(hashed)
    return (salt + hashed).decode('ascii')


def verify_password(stored_password, provided_password):
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    hashed = hashlib.pbkdf2_hmac('sha512',
                                 provided_password.encode('utf-8'),
                                 salt.encode('ascii'),
                                 100000)
    hashed = binascii.hexlify(hashed).decode('ascii')
    return hashed == stored_password
