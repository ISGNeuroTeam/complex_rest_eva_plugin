from datetime import datetime, timedelta
import logging
import uuid
import bcrypt

from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.response import Response


from eva_plugin.base_handler import BaseHandler

from eva_plugin.auth.db import db


logger = logging.getLogger('eva_plugin')


class AuthLoginHandler(BaseHandler):
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

    def initial(self, request, *args, **kwargs):
        super(BaseHandler, self).initial(request, *args, **kwargs)
        self._set_request_params(request)


    def post(self, request):
        user = db.check_user_exists(self.data.get("username"))
        if not user:
            raise ValidationError("incorrect login")

        password_equal = bcrypt.checkpw(
            self.data.get("password"),
            user.password,
        )
        if not password_equal:
            raise ValidationError(400, "incorrect password")

        user_tokens = db.get_user_tokens(user.id)
        client_token = request.COOKIES.get('eva_token', None)

        response = Response({'status': 'success'})

        if not client_token:
            payload = {'user_id': user.id, 'username': user.name, '_uuid': str(uuid.uuid4()),
                       'exp': int((datetime.now() + timedelta(hours=12)).timestamp())}
            token = self.generate_token(payload)
            expired_date = datetime.now() + timedelta(hours=12)
            db.add_session(
                token=token.decode('utf-8'),
                user_id=user.id,
                expired_date=expired_date
            )

            self.current_user = user.id

            response.set_cookie('eva_token', token, expires=expired_date)
            return response

        elif client_token not in user_tokens:
            raise AuthenticationFailed("unauthorized")
        else:
            return response


