from django.urls import path, re_path

from question import views

urlpatterns = [
    # question
    re_path(r'question/(?P<question_slug>[\w-]+)/add_vote/$', views.AddVoteQuestionView.as_view()),
    re_path(r'question/(?P<question_slug>[\w-]+)/remove_vote/$', views.RemoveVoteQuestionView.as_view()),
    re_path(r'question/(?P<question_slug>[\w-]+)/add_down_vote/$', views.AddDownVoteQuestionView.as_view()),
    re_path(r'question/(?P<question_slug>[\w-]+)/remove_down_vote/$', views.RemoveDownVoteQuestionView.as_view()),
    path('question/create/', views.QuestionCreateView.as_view()),
    path('question/list/', views.QuestionListView.as_view()),
    # path('public/question/list/', views.UserQuestionListView.as_view()),
    path('question/<int:id>/update/', views.QuestionUpdateView.as_view()),
    path('question/<int:id>/delete/', views.QuestionDeleteView.as_view()),
    path('public/question/<slug:question_slug>/answers/', views.UserQuestionAnswersListView.as_view()),
    # answer
    path('answer/create/', views.AnswerCreateView.as_view()),
    path('answer/list/', views.AnswerListView.as_view()),
    path('answer/<int:id>/update/', views.AnswerUpdateView.as_view()),
    path('answer/<int:id>/delete/', views.AnswerDeleteView.as_view()),
    path('answer/<int:id>/add_vote/', views.AddVoteAnswerView.as_view()),
    path('answer/<int:id>/remove_vote/', views.RemoveVoteAnswerView.as_view()),
    path('answer/<int:id>/add_down_vote/', views.AddDownVoteAnswerView.as_view()),
    path('answer/<int:id>/remove_down_vote/', views.RemoveDownVoteAnswerView.as_view()),
    ]
