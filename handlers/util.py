""" This module provides global helper functions """

import hashlib
import hmac
import random
import string

from google.appengine.ext import ndb
from handlers.secret import SECRET

# Make secure uid|hash for cookie
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(SECRET, val).hexdigest())

# Check uid|hash for validity
def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


# functions for hashing and checking hashed user info
def make_salt(length=5):
    return ''.join(random.choice(letters) for x in xrange(length))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)


def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

# Keys for User and Post model for potential future expansion
def users_key(group='default'):
    return ndb.Key('users', group)


def blog_key(name='default'):
    return ndb.Key('blogs', name)
