from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated, AllowAny
import uuid
import super_logger
# from django.conf import settings
import json

from complex_rest_eva_plugin.db_connector.db_connector.utils.db_connector import PostgresConnector
from ..utils.get_user import get_current_user
from ..settings import DB_POOL


class QuizsHandlerView(APIView):
    """
    That handler allows to get list of quizs with offset & limit params for pagination.
    """

    permission_classes = (IsAuthenticated,)
    # permission_classes = (AllowAny,)
    http_method_names = ['get']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('quizs')
    db = PostgresConnector(DB_POOL)

    def get(self, request):
        offset, limit = request.GET.get('offset', 0), request.GET.get('limit', 10)

        quizs = self.db.get_quizs(limit=limit, offset=offset)

        content = {'data': quizs, 'count': self.db.get_quizs_count()}
        return Response(content, status.HTTP_200_OK)


class QuizHandlerView(APIView):
    """
    There is four methods for four actions with quiz objects.
    - get:      returns quiz data by 'id' param;
    - post:     creates new quiz object in DB with data from json body;
    - put:      edit existing quiz object in DB with data from json body;
    - delete:   delete existing quiz object from DB by 'id' param;
    """

    permission_classes = (IsAuthenticated,)
    # permission_classes = (AllowAny,)
    http_method_names = ['get', 'post', 'put', 'delete']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('quizs')
    db = PostgresConnector(DB_POOL)

    def get(self, request):
        quiz_id = request.GET.get('id', None)
        if not quiz_id:
            return Response(
                json.dumps({'status': 'failed', 'error': "param 'id' is needed"}, default=str),
                status.HTTP_400_BAD_REQUEST
            )
        try:
            quiz = self.db.get_quiz(quiz_id=quiz_id)
        except Exception as err:
            return Response(
                json.dumps({'status': 'failed', 'error': str(err)}, default=str),
                status.HTTP_400_BAD_REQUEST
            )
        content = {'data': quiz}
        return Response(content, status.HTTP_200_OK)

    def post(self, request):
        quiz_name = request.GET.get('name', None)
        questions = request.GET.get('questions', None)
        if None in [quiz_name, questions]:
            return Response(
                json.dumps({'status': 'failed', 'error': "params 'name' and 'questions' is needed"}, default=str),
                status.HTTP_400_BAD_REQUEST
            )
        try:
            quiz_id = self.db.add_quiz(name=quiz_name,
                                       questions=questions)
        except Exception as err:
            return Response(
                json.dumps({'status': 'failed', 'error': str(err)}, default=str),
                status.HTTP_409_CONFLICT
            )
        content = {'data': quiz_id}
        return Response(content, status.HTTP_200_OK)

    def put(self, request):
        quiz_id = request.GET.get('id', None)
        quiz_name = request.GET.get('name', None)
        questions = request.GET.get('questions', None)
        if not quiz_id:
            return Response(
                json.dumps({'status': 'failed', 'error': "param 'id' is needed"}, default=str),
                status.HTTP_400_BAD_REQUEST
            )
        try:
            quiz_id = self.db.update_quiz(quiz_id=quiz_id,
                                          name=quiz_name,
                                          questions=questions)
        except Exception as err:
            return Response(
                json.dumps({'status': 'failed', 'error': str(err)}, default=str),
                status.HTTP_409_CONFLICT
            )
            # raise tornado.web.HTTPError(409, str(err))
        content = {'data': quiz_id}
        return Response(content, status.HTTP_200_OK)

    def delete(self, request):
        quiz_id = request.GET.get('id', None)
        if not quiz_id:
            return Response(
                json.dumps({'status': 'failed', 'error': "params 'id' is needed"}, default=str),
                status.HTTP_400_BAD_REQUEST
            )
        quiz_id = self.db.delete_quiz(quiz_id=quiz_id)
        content = {'data': quiz_id}
        return Response(content, status.HTTP_200_OK)


class QuizFilledHandlerView(APIView):
    """
    Handling actions with filled quiz object.
    It's allows two actions:
    - get:      gets filled quiz object from DB by 'id' param and limit/offset params for pagination;
    - post:     adds new fille quiz object to DB with data from json body;
    """

    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    http_method_names = ['get', 'post']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('quizs')
    db = PostgresConnector(DB_POOL)

    def get(self, request):
        quiz_type_id = request.GET.get('id', None)
        offset = request.GET.get('offset', 0)
        limit = request.GET.get('limit', 10)

        try:
            filled_quizs = self.db.get_filled_quiz(quiz_id=quiz_type_id,
                                                   offset=offset,
                                                   limit=limit)
        except Exception as err:
            return Response(
                json.dumps({'status': 'failed', 'error': str(err)}, default=str),
                status.HTTP_409_CONFLICT
            )
        count = self.db.get_filled_quizs_count(quiz_type_id) if quiz_type_id else len(filled_quizs)

        content = {'data': filled_quizs, 'count': count}
        return Response(content, status.HTTP_200_OK)

    def post(self, request):
        filled_ids = list()
        data = json.loads(request.body) if request.body else dict()
        for quiz in data:  # !!! CHECK !!!
            quiz_type_id = request.GET.get('id', None)
            questions = request.GET.get('questions', None)

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
                self.db.save_filled_quiz(user_id=current_user,
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


class QuizQuestionsHandlerView(APIView):
    """
    If is need a question list for one or more quiz, this handler for it.
    Input param is 'ids', like '?ids=1,2,3'.
    """

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('quizs')
    db = PostgresConnector(DB_POOL)

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
            # logger.debug(quiz_ids)
            questions = self.db.get_quiz_questions(quiz_ids=quiz_ids)
        except Exception as err:
            return Response(
                json.dumps({'status': 'failed', 'error': str(err)}, default=str),
                status.HTTP_409_CONFLICT
            )

        content = {'data': questions}
        return Response(content, status.HTTP_200_OK)


# class FilledQuizExportHandlerView(APIView):
#     """
#     This handler allows export filled quiz object into '.xlsx' format file.
#     Input param is 'id' which quiz.id in DB.
#     """
#
#     permission_classes = (IsAuthenticated,)
#     http_method_names = ['get']
#     handler_id = str(uuid.uuid4())
#     logger = super_logger.getLogger('quizs')
#     db = PostgresConnector(settings.DB_POOL)
#
#     # def initialize(self, **kwargs):
#     #     super().initialize(kwargs['db_conn_pool'])
#     #     self.static_conf = kwargs['static_conf']
#
#     async def get(self, request):
#         quiz_id = request.GET.get('id', None)
#         if not quiz_id:
#             return Response(
#                 json.dumps({'status': 'failed', 'error': "param 'id' is needed"}, default=str),
#                 status.HTTP_400_BAD_REQUEST
#             )
#         quiz_id = int(quiz_id)
#         try:
#             quiz_data = self.db.get_filled_quiz(quiz_id=quiz_id, current=True)
#             quiz_data = quiz_data[0] if quiz_data else None
#             if not quiz_data:
#                 return Response(
#                 json.dumps({'status': 'failed', 'error': f'No quiz with id={quiz_id}'}, default=str),
#                 status.HTTP_404_NOT_FOUND
#                 )
#         except Exception as err:
#             return Response(
#                 json.dumps({'status': 'failed', 'error': str(err)}, default=str),
#                 status.HTTP_409_CONFLICT
#             )
#
#         questions = quiz_data['questions']
#         quiz_name = quiz_data['name'].replace('«', '"').replace('»', '"')
#         quiz_name = quiz_name.replace(' ', '_')
#         filled = quiz_data['fill_date'].replace(' ', '').replace(':', '')
#
#         filename = f'{quiz_name}_{filled}.xlsx'
#         filepath = os.path.join(self.static_conf['static_path'], 'xlsx', filename)
#         if os.path.exists(filepath):
#             return self.write(f'/xlsx/{filename}')
#
#         wb = Workbook()
#         ws = wb.active
#         ws.title = 'чек-лист'
#         cell_range = ws['A1':'F1']
#         col_range = ['№', 'Вопрос', 'Ответ', 'Пояснение', 'Ключевой', 'Метка']
#         logger.debug(col_range)
#         for c, v in zip(*cell_range, col_range):
#             c.value = v
#
#         for i, q in enumerate(questions, 2):
#             cell_range = ws[f'A{i}':f'F{i}']
#             col_range = [q['sid'], q['text'], q['answer']['value'], q['answer']['description'],
#                          q['is_sign'], q['label']]
#             logger.info(col_range)
#             for c, v in zip(*cell_range, col_range):
#                 c.value = v
#
#         wb.save(filepath)
#         self.write(f'/xlsx/{filename}')

