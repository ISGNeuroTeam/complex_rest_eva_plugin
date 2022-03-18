import os
from ..utils.helper_functions import make_unique_name
import tarfile
import tempfile
from datetime import datetime
import uuid
import json
from ..utils.ds_wrapper import dswrapper
from hashlib import blake2b


class DataUploader:
    """
    For now a layer to work with fs
    """

    static_dir_name = 'storage'
    log_dir_name = 'cli_logs'

    def save_logs(self, token, user_id, logs_path, logs_text):
        token = token[token.find(' ') + 1:]  # remove 'Bearer ' from token
        base_logs_dir = os.path.join(logs_path, self.log_dir_name)
        if not os.path.exists(base_logs_dir):
            os.makedirs(base_logs_dir)
        h = blake2b(digest_size=4)
        h.update(token.encode())
        client_id = str(user_id) + '_' + h.hexdigest()

        log_file_path = os.path.join(base_logs_dir, client_id)
        with open(f'{log_file_path}.log', 'a+') as f:
            f.write(logs_text)

    @staticmethod
    def save_binary(files, svg_path):
        _file = dict(files)['file'][0]
        saving_full_path = os.path.join(svg_path, _file.name)
        if not os.path.exists(saving_full_path):
            with open(saving_full_path, 'wb') as f:
                f.write(_file.read())

    @staticmethod
    def _add_group_metadata(path_template, gid, archive):
        meta_filemath = path_template.format('_META')
        with open(meta_filemath, 'w+') as f:
            group_metadata = dswrapper.get_group(gid)
            f.write(json.dumps(group_metadata))
        archive.add(meta_filemath, os.path.join(str(gid), '_META'))

    @staticmethod
    def dash_import(files, group):
        tar_file = dict(files)['body'][0]

        # wraps bytes to work with it like with file
        file_like_object = tar_file.file
        with tarfile.open(mode='r:gz', fileobj=file_like_object) as tar:
            dtn = datetime.now().strftime('%Y%m%d%H%M%S')
            for dash in tar.getmembers():
                dash_data = tar.extractfile(dash)
                dswrapper.add_dashboard(name=f'{dash.name}_imported_{dtn}',
                                        body=dash_data.read().decode(),
                                        groups=[group[0].decode()])

    @staticmethod
    def group_import(files):
        """adds dashboards to db"""
        tar_file = dict(files)['body'][0]

        # wraps bytes to work with it like with file
        file_like_object = tar_file.file
        with tarfile.open(mode='r:gz', fileobj=file_like_object) as tar:
            inner_objects = tar.getnames()
            meta_list = [s for s in inner_objects if '_META' in s]
            dtn = datetime.now().strftime('%Y%m%d%H%M%S')

            for meta in meta_list:
                meta_data = tar.extractfile(meta)
                meta_dict = json.loads(meta_data.read())
                group_name = f"{meta_dict['name']}_imported_{dtn}"
                dswrapper.add_group(name=group_name,
                                    color=meta_dict['color'])
                dashes = [s for s in inner_objects if s.startswith(f"{meta_dict['id']}/")
                          and '_META' not in s]
                for dash in dashes:
                    dash_name = dash.split('/', 1)[-1]
                    dash_data = tar.extractfile(dash)
                    dswrapper.add_dashboard(name=f'{dash_name}_imported_{dtn}',
                                                 body=dash_data.read().decode(),
                                                 groups=[group_name])

    def dash_export(self, dash_ids, static_conf):
        dash_ids = dash_ids.split(',')
        dash_ids = [int(_) for _ in dash_ids]

        with tempfile.TemporaryDirectory() as tmp_dir:
            archive_name = f"{datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')}.eva.dash"
            _dirname = str(uuid.uuid4())
            _base_path = os.path.join(static_conf['static_path'], self.static_dir_name, _dirname)
            if not os.path.exists(_base_path):
                os.makedirs(_base_path)

            archive_path = os.path.join(_base_path, archive_name)
            with tarfile.open(archive_path, mode='x:gz') as archive:
                for did in dash_ids:
                    dash_data = dswrapper.get_dashboard(dash_id=did)
                    path_template = os.path.join(tmp_dir, '{}.json')
                    filename = make_unique_name(path_template, dash_data['name'])
                    filepath = path_template.format(filename)

                    if not os.path.exists(filepath):
                        with open(filepath, 'w+') as f:
                            f.write(dash_data['body'])

                    archive.add(filepath, filename)
        return _dirname, archive_name

    def group_export(self, group_ids, static_conf):

        group_ids = group_ids.split(',')
        group_ids = [int(_) for _ in group_ids]

        with tempfile.TemporaryDirectory() as tmp_dir:
            archive_name = f"{datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')}.eva.group"
            _dirname = str(uuid.uuid4())
            _base_path = os.path.join(static_conf, self.static_dir_name, _dirname)
            if not os.path.exists(_base_path):
                os.makedirs(_base_path)

            archive_path = os.path.join(_base_path, archive_name)
            with tarfile.open(archive_path, mode='x:gz') as archive:
                for gid in group_ids:
                    dashes_data = dswrapper.get_dashboards(group_id=gid)
                    group_dir = os.path.join(tmp_dir, str(gid))
                    if not os.path.exists(group_dir):
                        os.makedirs(group_dir)
                    path_template = os.path.join(group_dir, '{}.json')

                    for dash in dashes_data:
                        filename = make_unique_name(path_template, dash['name'])
                        filepath = path_template.format(filename)

                        if not os.path.exists(filepath):
                            with open(filepath, 'w+') as f:
                                f.write(dash['body'])
                        archive.add(filepath, os.path.join(str(gid), filename))
                    # adds group metadata for future import
                    self._add_group_metadata(path_template, gid, archive)
        return _dirname, archive_name


data_uploader = DataUploader()
