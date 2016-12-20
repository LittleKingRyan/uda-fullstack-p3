import re
import random
import string
import hashlib


# #############################################################################
# the first three functions are used to hash and verify passwords with salts
def make_salt():
    return ''.join(random.choice(string.letters) for x in range(5))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return "%s,%s" % (h, salt)


def valid_pw_hash(name, pw, h):
    try:
        salt = h.split(',')[1]
        return h == make_pw_hash(name, pw, salt)
    except IndexError:
        return False

# #############################################################################
# the newxt two functions are used to hash user's id to set more secure cookies
COOKIE_KEY = 'f9bf78b9a18ce6d46a0cd2b0b86df9da'


def cookie_hash(string, username):
    # s: string to hashed
    # h: hashed string
    # returns "s,h"
    return "{}|{}|{}".format(string,
                             hashlib.md5(string+COOKIE_KEY).hexdigest(),
                             username)


def cookie_verify(id_hash_user):
    # sh: hashed string "s,h" where s is the original string and
    # h is the hashed string
    id_hash_user_list = id_hash_user.split("|")
    id = id_hash_user_list[0]
    username = id_hash_user_list[2]
    return cookie_hash(id, username) == id_hash_user

# #############################################################################
# the following codes are used to verify users' sign up inputs
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{6,20}$")
EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


def input_valid_username(username):
    return username and USER_RE.match(username)


def input_valid_password(password):
    return password and PASS_RE.match(password)


def input_valid_email(email):
    return not email or EMAIL_RE.match(email)
