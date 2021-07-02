from django.urls import path
from django.conf import settings
from utilities import views as util_views


urlpatterns = [
    path('upload_file/', util_views.FileUploadView.as_view()),
    path('merge_company/', util_views.MergeCompanyView.as_view()),
]

if settings.DEBUG:
    urlpatterns += [
        path('create_initial_data/', util_views.CreateDataTestView.as_view()),
    ]
