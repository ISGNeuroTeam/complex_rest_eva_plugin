# from celery.schedules import crontab
# from typing import Optional
# from rest_framework.request import Request
# import super_logger
# import uuid
#
# from rest.permissions import IsAuthenticated, AllowAny
# from rest.response import Response, status
# from rest.views import APIView
# from ..settings import app
#
#
# # from ..tasks import *
# # from ..utils.task import add_periodic_task_v2, get_all_periodic_tasks, get_all_tasks
#
#
# class AddTask(APIView):
#
#     # permission_classes = (IsAuthenticated,)
#     permission_classes = (AllowAny,)
#     http_method_names = ['post']
#     handler_id = str(uuid.uuid4())
#     logger = super_logger.getLogger('super_scheduler')
#
#     # def _create_job_conf(self) -> dict:
#     #
#     #     ### EXAMPLE!
#     #     # job = {
#     #     #     'schedule': crontab(minute="*/1"),  # crontab schedule ; OR timedelta(seconds=15),
#     #     #     'func': test_logger,  # Name of a predefined function
#     #     #     'func_args': None,
#     #     #     'name': None,
#     #     #     'kwargs': {},
#     #     #     'expires': None
#     #     # }
#     #
#     #     job = {
#     #         'schedule': 20.0,  # every 10 seconds.
#     #         'func': test_logger,  # Name of a predefined function
#     #         'func_args': None,
#     #         'name': None,
#     #         'kwargs': {},
#     #         'expires': None
#     #     }
#     #
#     #     return job
#
#     def post(self, request: Request):
#
#         dict_params = dict(request.data)
#
#         # job = self._create_job_conf()
#         # add_periodic_task_v2(
#         #     schedule=job['schedule'],
#         #     func=job['func'],
#         #     func_args=job['func_args'],
#         #     name=job['name'],
#         # )
#         #
#         # log.info('Create periodic task!')
#         # log.info(str(get_all_periodic_tasks()))
#         # log.info(str(get_all_tasks()))
#         # self.logger.info()
#
#         return Response({'status': 'success'}, status.HTTP_200_OK)
