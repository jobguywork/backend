from django.urls import path

from review import views

urlpatterns = [
    # Pros
    path('pros/create/', views.ProsCreateView.as_view()),
    path('pros/list/', views.ProsListView.as_view()),
    path('public/pros/list/', views.UserProsListView.as_view()),
    path('pros/<int:id>/update/', views.ProsUpdateView.as_view()),
    path('pros/<int:id>/delete/', views.ProsDeleteView.as_view()),
    # Cons
    path('cons/create/', views.ConsCreateView.as_view()),
    path('cons/list/', views.ConsListView.as_view()),
    path('public/cons/list/', views.UserConsListView.as_view()),
    path('cons/<int:id>/update/', views.ConsUpdateView.as_view()),
    path('cons/<int:id>/delete/', views.ConsDeleteView.as_view()),
    # Company Review
    path('company_review/create/', views.CompanyReviewCreateView.as_view()),
    path('company_review/list/', views.CompanyReviewListView.as_view()),
    path('company_review/<int:id>/update/', views.CompanyReviewUpdateView.as_view()),
    path('company_review/<int:id>/reply/', views.CompanyReviewReplyView.as_view()),
    path('company_review/<int:id>/delete/', views.CompanyReviewDeleteView.as_view()),
    path('company_review/<int:id>/add_vote/', views.AddVoteCompanyReviewView.as_view()),
    path('company_review/<int:id>/remove_vote/', views.RemoveVoteCompanyReviewView.as_view()),
    path('company_review/<int:id>/add_down_vote/', views.AddDownVoteCompanyReviewView.as_view()),
    path('company_review/<int:id>/remove_down_vote/', views.RemoveDownVoteCompanyReviewView.as_view()),
    path('public/company_review/<int:id>/', views.UserCompanyReviewRetrieveView.as_view()),
    path('admin/company_review/<int:id>/', views.AdminCompanyReviewRetrieveView.as_view()),
    path('public/company_review/<int:id>/comment_list/', views.ReviewCommentListView.as_view()),
    path('admin/company_review/<int:id>/comment_list/', views.AdminReviewCommentListView.as_view()),
    # review comment
    path('review_comment/create/', views.ReviewCommentCreateView.as_view()),
    path('review_comment/<int:id>/update/', views.ReviewCommentUpdateView.as_view()),
    path('review_comment/<int:id>/delete/', views.ReviewCommentDeleteView.as_view()),
    path('review_comment/<int:id>/add_vote/', views.AddVoteReviewCommentView.as_view()),
    path('review_comment/<int:id>/remove_vote/', views.RemoveVoteReviewCommentView.as_view()),
    path('review_comment/<int:id>/add_down_vote/', views.AddDownVoteReviewCommentView.as_view()),
    path('review_comment/<int:id>/remove_down_vote/', views.RemoveDownVoteReviewCommentView.as_view()),
    # Interview
    path('interview/create/', views.InterviewCreateView.as_view()),
    path('interview/list/', views.InterviewListView.as_view()),
    path('interview/<int:id>/update/', views.InterviewUpdateView.as_view()),
    path('interview/<int:id>/reply/', views.CompanyInterReviewReplyView.as_view()),
    path('interview/<int:id>/delete/', views.InterviewDeleteView.as_view()),
    path('interview/<int:id>/add_vote/', views.AddVoteInterviewView.as_view()),
    path('interview/<int:id>/remove_vote/', views.RemoveVoteInterviewView.as_view()),
    path('interview/<int:id>/add_down_vote/', views.AddDownVoteInterviewView.as_view()),
    path('interview/<int:id>/remove_down_vote/', views.RemoveDownVoteInterviewView.as_view()),
    path('public/interview/<int:id>/', views.UserInterviewRetrieveView.as_view()),
    path('admin/interview/<int:id>/', views.AdminInterviewRetrieveView.as_view()),
    path('public/interview/<int:id>/comment_list/', views.InterviewCommentListView.as_view()),
    path('admin/interview/<int:id>/comment_list/', views.AdminInterviewCommentListView.as_view()),
    # interview comment
    path('interview_comment/create/', views.InterviewCommentCreateView.as_view()),
    path('interview_comment/<int:id>/update/', views.InterviewCommentUpdateView.as_view()),
    path('interview_comment/<int:id>/delete/', views.InterviewCommentDeleteView.as_view()),
    path('interview_comment/<int:id>/add_vote/', views.AddVoteInterviewCommentView.as_view()),
    path('interview_comment/<int:id>/remove_vote/', views.RemoveVoteInterviewCommentView.as_view()),
    path('interview_comment/<int:id>/add_down_vote/', views.AddDownVoteInterviewCommentView.as_view()),
    path('interview_comment/<int:id>/remove_down_vote/', views.RemoveDownVoteInterviewCommentView.as_view()),
    # bot
    path('bot_review/', views.BotApproveReviewView.as_view()),
    ]
