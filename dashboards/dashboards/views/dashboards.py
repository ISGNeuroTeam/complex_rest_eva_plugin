from rest.views import APIView
from rest.response import Response, status
from rest.permissions import IsAuthenticated
import uuid
import super_logger
import json


class DashboardsView(APIView):

    permission_classes = (IsAuthenticated,)
    http_method_names = ['get']
    handler_id = str(uuid.uuid4())
    logger = super_logger.getLogger('dashboards')

    def get(self, request):
        kwargs = {}
        target_group_id = self.get_argument('id', None)
        if target_group_id:
            kwargs['group_id'] = target_group_id
        names_only = self.get_argument('names_only', None)
        if names_only:
            kwargs['names_only'] = names_only
        dashs = self.db.get_dashs_data(**kwargs)
        return Response(
            {'data': dashs},
            status.HTTP_200_OK
        )

class DashboardsHandler(BaseHandler):
    async def get(self):
        kwargs = {}

        if 'list_dashs' in self.permissions or 'admin_all' in self.permissions:
            target_group_id = self.get_argument('id', None)
            if target_group_id:
                kwargs['group_id'] = target_group_id
            names_only = self.get_argument('names_only', None)
            if names_only:
                kwargs['names_only'] = names_only
        else:
            raise tornado.web.HTTPError(403, "no permission for list dashs")

        dashs = self.db.get_dashs_data(**kwargs)
        self.write({'data': dashs})