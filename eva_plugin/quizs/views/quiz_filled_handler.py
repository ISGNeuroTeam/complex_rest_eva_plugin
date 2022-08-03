from rest.permissions import IsAuthenticated
from rest.response import Response, status
from rest.views import APIView
import logging
import uuid
import json

from ..settings import DB_CONN
from ..utils.get_user import get_current_user


class QuizFilledHandlerView(APIView):
    """
    Handling actions with filled quiz object.
    It's allows two actions:
    - get:      gets filled quiz object from DB by 'id' param and limit/offset params for pagination;
    - post:     adds new fille quiz object to DB with data from json body;
    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post']
    handler_id = str(uuid.uuid4())
    logger = logging.getLogger('quizs')

    def get(self, request):

        quiz_type_id = request.GET.get('id', None)
        offset = request.GET.get('offset', 0)
        limit = request.GET.get('limit', 10)

        try:
            filled_quizs = DB_CONN.get_filled_quiz(quiz_id=quiz_type_id,
                                                   offset=offset,
                                                   limit=limit)
            print(filled_quizs)
        except Exception as err:
            return Response(
                json.dumps({'status': 'failed', 'error': str(err)}, default=str),
                status.HTTP_409_CONFLICT
            )

        count = DB_CONN.get_filled_quizs_count(quiz_type_id) if quiz_type_id else len(filled_quizs)

        content = {'data': filled_quizs, 'count': count}
        return Response(content, status.HTTP_200_OK)

    @staticmethod
    def _iterate_quizs(request, data, filled_ids):
        for quiz_data in data:

            quiz_type_id = quiz_data.get('id', None)
            questions = quiz_data.get('questions', None)

            if None in [quiz_type_id, questions]:
                return Response(
                    json.dumps({'status': 'failed', 'error': "params 'id' and 'questions' is needed"}, default=str),
                    status.HTTP_400_BAD_REQUEST
                )

            try:
                current_user = get_current_user(request)
                if not current_user:
                    return Response(
                        json.dumps({'status': 'failed', 'error': "unauthorized"}, default=str),
                        status.HTTP_401_UNAUTHORIZED
                    )
                DB_CONN.save_filled_quiz(user_id=None,
                                         user=current_user,
                                         quiz_id=quiz_type_id,
                                         questions=questions)
                filled_ids.append(quiz_type_id)
            except Exception as err:
                return Response(
                    json.dumps({'status': 'failed', 'error': str(err)}, default=str),
                    status.HTTP_409_CONFLICT
                )

        content = {'ids': filled_ids}
        return Response(content, status.HTTP_200_OK)

    def post(self, request):

        filled_ids = list()

        return self._iterate_quizs(request, request.data, filled_ids)
