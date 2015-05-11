import string
#from jeopardy.final_jeopardy import music as the_bae
from validate_email import validate_email
from werkzeug.security import generate_password_hash, check_password_hash


def is_valid_email(email):
    # TODO verify that email is not already in the database
    return validate_email(email)

def is_valid_password(password):
    valid_chars = string.ascii_letters + string.digits + string.punctuation
    all_chars_valid = True
    for char in password:
        if char not in valid_chars:
            all_chars_valid = False
            break
    return (len(password) > 8) and (len(password) < 50) and all_chars_valid
    
def hash_password(s):
    return generate_password_hash(s)
