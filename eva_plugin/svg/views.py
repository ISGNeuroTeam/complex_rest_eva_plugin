import os
import logging

from django.core.files.uploadedfile import UploadedFile
from rest_framework.response import Response

from eva_plugin.base_handler import BaseHandler
from eva_plugin.tools.svg_manager import SVGManager

from eva_plugin.settings import FILE_UPLOADER_CONF, STATIC_CONF


class SvgLoadHandler(BaseHandler):

    MAX_FILE_SIZE = 1024

    def __init__(self, *args, **kwargs):
        super(SvgLoadHandler, self).__init__(*args, **kwargs)

        self.logger = logging.getLogger('eva_plugin.svg')

        svg_path = FILE_UPLOADER_CONF.get('svg_path', os.path.join(STATIC_CONF, 'svg'))

        self.svg_manager = SVGManager(svg_path)

    def post(self, request):
        try:
            files = request.FILES
            _file: UploadedFile = files['file']

            if _file.size > self.MAX_FILE_SIZE:
                error_msg = f'File size more than 1 Mb; must be less.'
                self.logger.error(error_msg)
                response = {'status': 'failed', 'error': f'{error_msg}', 'notifications': [{'code': 4}]}
                return Response(response)
            else:
                named_as = self.svg_manager.write(_file.name, _file.read())
                response = {'status': 'ok', 'filename': named_as, 'notifications': [{'code': 3}]}
                return Response(response)
        except Exception as e:
            self.logger.error(f'Error while writing file: {e}')
            response = {'status': 'failed', 'error': f'{e}', 'notifications': [{'code': 4}]}
            return Response(response)

    def delete(self, request):
        try:
            filename = self.get_argument('filename')
            deleted = self.svg_manager.delete(filename)
            if deleted:
                return Response({'status': 'ok'})
            else:
                return Response({'status': 'failed', 'error': 'file not found'})
        except Exception as e:
            self.logger.error(f'Error while deleting file: {e}')
            return Response({'status': 'failed', 'error': f'{e}'})

