from ..settings import DB_CONN


class DataSourceWrapper:
    """
    For now a layer to work with db
    """

    @staticmethod
    def get_dashboards(target_group_id=None, names_only=None, **kwargs):
        if target_group_id:
            kwargs['group_id'] = target_group_id
        if names_only:
            kwargs['names_only'] = names_only
        return DB_CONN.get_dashs_data(**kwargs)

    @staticmethod
    def get_dashboard(dash_id):
        return DB_CONN.get_dash_data(dash_id=dash_id)

    @staticmethod
    def get_dashboard_by_name(dash_name, dash_group):
        dash_name = dash_name.replace('"', '')
        # FIXME need remove double quote replacement
        return DB_CONN.get_dash_data_by_name(dash_name=dash_name, dash_group=dash_group)

    @staticmethod
    def get_group(group_id):
        return DB_CONN.get_group_data(group_id=group_id)

    @staticmethod
    def add_dashboard(name, body, groups):
        return DB_CONN.add_dash(name=name, body=body, groups=groups)

    @staticmethod
    def add_group(name, color):
        return DB_CONN.add_group(name=name, color=color)

    @staticmethod
    def get_group(group_id):
        return DB_CONN.get_group_data(group_id=group_id)

    @staticmethod
    def update_dashboard(dash_id, name, body, groups):
        return DB_CONN.update_dash(dash_id=dash_id, name=name, body=body, groups=groups)

    @staticmethod
    def delete_dashboard(dash_id):
        return DB_CONN.delete_dash(dash_id=dash_id)

    @staticmethod
    def get_all_groups(names_only):
        return DB_CONN.get_groups_data(names_only=names_only)


dswrapper = DataSourceWrapper()
