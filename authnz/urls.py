from django.urls import path, re_path

from authnz import views as authnz_views


urlpatterns = [
    path('my_reviews/', authnz_views.MyReviewListView.as_view()),
    path('my_interviews/', authnz_views.MyInterviewListView.as_view()),
    path('check_nick_name_availablity/', authnz_views.NickNameAvailabilityView.as_view()),
    path('register_email/', authnz_views.RegisterWithEmailView.as_view()),
    path('login_email/', authnz_views.LoginEmailView.as_view()),
    path('change_my_password/', authnz_views.ChangePasswordView.as_view()),
    path('refresh_my_token/', authnz_views.RefreshTokenView.as_view()),
    path('update_profile/', authnz_views.UpdateUserProfileView.as_view()),
    path('forgot_password/', authnz_views.ForgotPasswordEmailView.as_view()),
    path('change_password_with_token/', authnz_views.ChangePasswordWithForgotTokenView.as_view()),
    path('social_login/<backend>/', authnz_views.SocialTokenView.as_view()),
    path('set_social/<backend>/', authnz_views.SetSocialTokenView.as_view()),
    re_path('^activate/(?P<uidb64>[0-9A-Za-z_\-\']+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        authnz_views.ConfirmEmailView.as_view(), name='activate'),
]
