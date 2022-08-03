from rest.permissions import IsAuthenticated
from rest.response import Response, status
from rest.views import APIView
import logging
import uuid
import json

from ..settings import DB_CONN


class QuizQuestionsHandlerView(APIView):
    """
    If is need a question list for one or more quiz, this handler for it.
    Input param is 'ids', like '?ids=1,2,3'.
    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    handler_id = str(uuid.uuid4())
    logger = logging.getLogger('quizs')

    def get(self, request):

        quiz_ids = request.GET.get('ids', None)

        if not quiz_ids:
            return Response(
                json.dumps({'status': 'failed', 'error': "params 'ids' is needed"}, default=str),
                status.HTTP_400_BAD_REQUEST
            )

        quiz_ids = quiz_ids.split(',')
        quiz_ids = [int(i) for i in quiz_ids if i]

        try:
            questions = DB_CONN.get_quiz_questions(quiz_ids=quiz_ids)
        except Exception as err:
            return Response(
                json.dumps({'status': 'failed', 'error': str(err)}, default=str),
                status.HTTP_409_CONFLICT
            )

        content = {'data': questions}
        return Response(content, status.HTTP_200_OK)
