from django.urls import path

from donate import views

urlpatterns = [
    # Donate
    path('donate/', views.DonateCreateView.as_view()),
]
