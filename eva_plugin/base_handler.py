import logging
import uuid
import jwt

from rest.permissions import AllowAny

from rest_framework.views import APIView
from rest_framework.exceptions import NotAuthenticated

from eva_plugin.auth.db import db

SECRET_KEY = '8b62abb2-bbf6-4e0e-a7c1-2e4734bebbd9'


class RestUser:

    def __init__(self, name: str, _id: int):
        self.name = name
        self.id = _id

    def __str__(self):
        return f'user name={self.name} with ID={self.id}'


class BaseHandler(APIView):

    permission_classes = (AllowAny,)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
        Gets config and init logger.

        :param db_conn_pool: Postgres DB connection pool object.
        :return:
        """
        self.handler_id = str(uuid.uuid4())
        self.logger = logging.getLogger('eva_plugin')
        self.permissions = None
        self.data = None
        self.token = None
        self.GET = None
        self.cookie = None
        self.current_user = None

    def decode_token(self, token):
        return jwt.decode(token, SECRET_KEY, algorithms='HS256')

    def generate_token(self, payload):
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    def get_cookie(self, name):
        return self.cookie.get(name)

    def _set_request_params(self, request):
        if hasattr(request, 'data'):
            self.data = request.data
        else:
            self.data = None
        if hasattr(request, 'GET'):
            self.GET = request.GET

        self.cookie = request.COOKIES

    def get_argument(self, arg_name, default_value=None):
        return self.GET.get(arg_name, default_value)

    def initial(self, request, *args, **kwargs):
        super(BaseHandler, self).initial(request, *args, **kwargs)

        self._set_request_params(request)

        client_token = self.get_cookie('eva_token')

        if client_token:
            self.token = client_token
            try:
                token_data = self.decode_token(client_token)
                user_id = token_data['user_id']
                user_name = token_data['username']
                # self.request.user = RestUser(name=user_name, _id=user_id)
                self.permissions = db.get_permissions_data(user_id=user_id, names_only=True)
            except (jwt.ExpiredSignatureError, jwt.DecodeError):
                pass
            else:
                self.current_user = user_id

        if not self.current_user:
            raise NotAuthenticated("unauthorized")

