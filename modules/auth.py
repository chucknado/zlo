from YamJam import yamjam


def get_auth():
    # return '{}/token'.format('jdoe@example.com'), '9a8b7c6d5e4f3g2h1'
    return '{}/token'.format(yamjam()['ZEN_USER']), yamjam()['ZEN_API_TOKEN']


# def get_aws_access_key():
#     return yamjam()['AWS_ACCESS_KEY']


# def get_aws_secret_access_key():
#     return yamjam()['AWS_SECRET_ACCESS_KEY']

