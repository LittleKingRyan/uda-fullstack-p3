import hashlib

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

hashed = cookie_hash('123', 'Ryan')
print hashed

print cookie_verify(hashed)


# test for only matching user can edit post
6473924464345088