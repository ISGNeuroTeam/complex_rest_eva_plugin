from rest_framework.request import Request
import super_logger
import uuid

from rest.permissions import IsAuthenticated, AllowAny
from rest.response import Response, status
from rest.views import APIView

from plugins.super_scheduler.utils.task.get_task import get_all_task_names, get_all_periodic_task_names
from plugins.super_scheduler.utils.task.add_task import AddPeriodicTask
from plugins.super_scheduler.utils.task.del_task import DelPeriodicTask
from plugins.super_scheduler.utils.schedule.add_schedule import AddSchedule


class TaskView(APIView):

    # permission_classes = (IsAuthenticated,)
    permission_classes = (AllowAny,)
    http_method_names = ['post', 'put', 'delete', 'get']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('super_scheduler')

    def post(self, request: Request) -> Response:

        req_params = dict(request.data)

        if 'schedule' not in req_params or 'task' not in req_params:
            msg_error = "Not valid format; " \
                        "waited: {'task': {...}, 'schedule': {...}}; " \
                        f"got: {req_params}"
            return Response(data=msg_error, status=status.HTTP_400_BAD_REQUEST)

        schedule, msg_error = AddSchedule.create(req_params['schedule'])
        if schedule is None:
            return Response(data=msg_error, status=status.HTTP_400_BAD_REQUEST)

        status_task, msg_error = AddPeriodicTask.create(schedule=schedule, task_kwargs=req_params['task'])
        if status_task is False:
            return Response(data=msg_error, status=status.HTTP_400_BAD_REQUEST)

        data = {'status': 'success'}
        return Response(data=data, status=status.HTTP_201_CREATED)

    def put(self, request: Request) -> Response:

        data = {'status': 'success'}
        return Response(data=data, status=status.HTTP_200_OK)

    def delete(self, request: Request) -> Response:
        """
        request example: {'task': {'name': 'taskname', ...}, ...}
        """

        req_params = dict(request.data)

        if 'task' not in req_params or 'name' not in req_params['task']:
            msg_error = "Not valid format; " \
                        "waited: {'task': {'name': 'taskname', ...}, ...}; "\
                        f"got: {req_params}"
            return Response(data=msg_error, status=status.HTTP_400_BAD_REQUEST)

        status_task, msg_error = DelPeriodicTask.delete(req_params['task'])
        if status_task is False:
            return Response(data=msg_error, status=status.HTTP_400_BAD_REQUEST)

        data = {'status': 'success'}
        return Response(data=data, status=status.HTTP_200_OK)

    def get(self, request: Request) -> Response:
        data = {
            'tasks': get_all_task_names(),
            'periodic_tasks': get_all_periodic_task_names(),
        }
        return Response(data=data, status=status.HTTP_200_OK)
