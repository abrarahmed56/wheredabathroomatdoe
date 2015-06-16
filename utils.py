def deflate_uuid(uuid):
    return uuid.replace('-', '')

def inflate_uuid(uuid):
    if len(uuid) == 32:
        return uuid[0:8] + '-' + uuid[8:12] + '-' + uuid[12:16] + '-' + uuid[16:20] + '-' + uuid[20:32]
    else:
        return None

def is_valid_request(form, required_keys):
    for key in required_keys:
        if not form.has_key(key):
            return False
    return True

def clear_session_login_data(session):
    if session.has_key('email'):
        del session['email']
    if session.has_key('uid'):
        del session['uid']

