import string
#from jeopardy.final_jeopardy import music as the_bae
from validate_email import validate_email
from werkzeug.security import generate_password_hash, check_password_hash

PASSWORD_VALID_CHARS = string.ascii_letters + string.digits + string.punctuation

def is_valid_email(email):
    # TODO verify that email is not already in the database
    return validate_email(email)

def is_valid_password(password):
    global PASSWORD_VALID_CHARS
    for char in password:
        if char not in PASSWORD_VALID_CHARS:
            return False
    return 8 < len(password) < 50
    
def hash_password(s):
    return generate_password_hash(s)
