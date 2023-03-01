import random
import string

from db.invoices import Invoice

def verify_unique(uid: str) -> bool:
    return not Invoice.get(uid)

def gen_uuid(string_length: int) -> str:
    while True:
        charset = string.digits + ''.join(c for c in string.ascii_uppercase if c not in 'AEIOU')
        uuid = ''.join(random.choice(charset) for _ in range(string_length))
        if verify_unique(uuid):
            return uuid
        