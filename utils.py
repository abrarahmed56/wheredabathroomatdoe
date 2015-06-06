def deflate_uuid(uuid):
    return uuid.replace('-', '')

def inflate_uuid(uuid):
    if len(uuid) == 32:
        return uuid[0:8] + '-' + uuid[8:12] + '-' + uuid[12:16] + '-' + uuid[16:20] + '-' + uuid[20:32]
    else:
        return None
