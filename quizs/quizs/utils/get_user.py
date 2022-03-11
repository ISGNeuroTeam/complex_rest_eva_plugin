import jwt


SECRET_KEY = '8b62abb2-bbf6-4e0e-a7c1-2e4734bebbd9'


def decode_token(token):
    return jwt.decode(token, SECRET_KEY, algorithms='HS256')


def get_current_user(request):
    # TODO: need check
    client_token = request.COOKIES.get('eva_token')
    current_user = None
    if client_token:
        try:
            token_data = decode_token(client_token)
            user_id = token_data['user_id']
            # permissions = self.db.get_permissions_data(user_id=user_id, names_only=True)
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            pass
        else:
            current_user = user_id
    return current_user