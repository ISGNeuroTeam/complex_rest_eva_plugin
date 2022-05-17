from celery.schedules import crontab
from typing import Optional
from rest_framework.request import Request
import super_logger
import uuid

from rest.permissions import IsAuthenticated, AllowAny
from rest.response import Response, status
from rest.views import APIView
from ..settings import app


# from ..tasks import *

from plugins.super_scheduler.utils.task.get_tasks import get_all_tasks, get_all_periodic_task_names
from plugins.super_scheduler.utils.task.add_tasks import add_periodic_task


class TaskView(APIView):

    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    http_method_names = ['post', 'put', 'delete', 'get']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('super_scheduler')

    def post(self, request: Request) -> Response:

        dict_params = dict(request.data)

        # tmp
        add_periodic_task(1, 2)

        data = {'status': 'success'}
        return Response(data=data, status=status.HTTP_201_CREATED)

    def put(self, request: Request) -> Response:

        data = {'status': 'success'}
        return Response(data=data, status=status.HTTP_200_OK)

    def delete(self, request: Request) -> Response:

        data = {'status': 'success'}
        return Response(data=data, status=status.HTTP_200_OK)

    def get(self, request: Request) -> Response:

        data = {
            'tasks': get_all_tasks(),
            'periodic_tasks': get_all_periodic_task_names(),
        }
        return Response(data=data, status=status.HTTP_200_OK)
