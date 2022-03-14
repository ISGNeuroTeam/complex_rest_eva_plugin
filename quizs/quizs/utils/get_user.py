from complex_rest.rest_auth.authentication import JWTAuthentication


def get_current_user(request):
    # request.user.username
    res = JWTAuthentication().authenticate(request)
    return str(res[0]) if res else None
