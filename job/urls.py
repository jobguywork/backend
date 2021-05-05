from django.urls import path

from job import views

urlpatterns = [
    # Job
    path('job/create/', views.JobCreateView.as_view()),
    path('job/list/', views.JobListView.as_view()),
    path('public/job/list/', views.UserJobListView.as_view()),
    path('job/<int:id>/update/', views.JobUpdateView.as_view()),
    path('job/<int:id>/delete/', views.JobDeleteView.as_view()),
    ]
