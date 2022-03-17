from rest.permissions import IsAuthenticated
from rest.response import Response, status
from rest.views import APIView
import super_logger
import uuid
import json

from plugins.db_connector.connector_singleton import db


class QuizsHandlerView(APIView):
    """
    That handler allows to get list of quizs with offset & limit params for pagination.
    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('quizs')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._limit = None
        self._offset = None

    @property
    def quizs(self):
        return db.get_quizs(limit=self._limit, offset=self._offset)

    @property
    def quizs_count(self):
        return db.get_quizs_count()

    def get(self, request):

        self._offset, self._limit = request.GET.get('offset', 0), request.GET.get('limit', 10)

        content = {'data': self.quizs, 'count': self.quizs_count}
        return Response(content, status.HTTP_200_OK)


class QuizHandlerView(APIView):
    """
    There is four methods for four actions with quiz objects.
    - get:      returns quiz data by 'id' param;
    - post:     creates new quiz object in DB with data from json body;
    - put:      edit existing quiz object in DB with data from json body by id;
    - delete:   delete existing quiz object from DB by 'id' param;
    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get', 'post', 'put', 'delete']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('quizs')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._quiz_id = None

    def get(self, request):

        self._quiz_id = request.GET.get('id', None)

        if not self._quiz_id:
            return Response(
                json.dumps({'status': 'failed', 'error': "param 'id' is needed"}, default=str),
                status.HTTP_400_BAD_REQUEST
            )

        try:
            quiz = db.get_quiz(quiz_id=self._quiz_id)
        except Exception as err:
            return Response(
                json.dumps({'status': 'failed', 'error': str(err)}, default=str),
                status.HTTP_400_BAD_REQUEST
            )

        content = {'data': quiz}
        return Response(content, status.HTTP_200_OK)

    def post(self, request):

        data = request.data
        quiz_name = data.get('name', None)
        questions = data.get('questions', None)

        if None in [quiz_name, questions]:
            return Response(
                json.dumps({'status': 'failed', 'error': "params 'name' and 'questions' is needed"}, default=str),
                status.HTTP_400_BAD_REQUEST
            )
        try:
            quiz_id = db.add_quiz(name=quiz_name,
                                  questions=questions)
        except Exception as err:
            return Response(
                json.dumps({'status': 'failed', 'error': str(err)}, default=str),
                status.HTTP_409_CONFLICT
            )
        content = {'data': quiz_id}
        return Response(content, status.HTTP_200_OK)

    def put(self, request):

        data = request.data
        quiz_id = data.get('id', None)
        quiz_name = data.get('name', None)
        questions = data.get('questions', None)

        if not quiz_id:
            return Response(
                json.dumps({'status': 'failed', 'error': "param 'id' is needed"}, default=str),
                status.HTTP_400_BAD_REQUEST
            )

        try:
            quiz_id = db.update_quiz(quiz_id=quiz_id,
                                          name=quiz_name,
                                          questions=questions)
        except Exception as err:
            return Response(
                json.dumps({'status': 'failed', 'error': str(err)}, default=str),
                status.HTTP_409_CONFLICT
            )
        content = {'data': quiz_id}
        return Response(content, status.HTTP_200_OK)

    def delete(self, request):

        quiz_id = request.GET.get('id', None)

        if not quiz_id:
            return Response(
                json.dumps({'status': 'failed', 'error': "params 'id' is needed"}, default=str),
                status.HTTP_400_BAD_REQUEST
            )

        quiz_id = db.delete_quiz(quiz_id=quiz_id)

        content = {'data': quiz_id}
        return Response(content, status.HTTP_200_OK)
