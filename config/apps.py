from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class ConfigConfig(AppConfig):
    name = 'config'


# class MyAdminConfig(AdminConfig):
#     def __init__(self, *args, **kwargs):
#         super(MyAdminConfig, self).__init__(*args, **kwargs)
#         # self.module = 'config.admin.MyAdminSite'
