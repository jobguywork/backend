from django.contrib import admin
from django import forms
from django.urls import reverse
from django.utils.html import format_html

from .models import Pros, Cons, CompanyReview, Interview, ReviewComment, InterviewComment


def approve_company_review(modeladmin, request, queryset):
    queryset.update(approved=True)
    for item in queryset:
        item.company.handle_company_review_statics()


def approve_company_interview(modeladmin, request, queryset):
    queryset.update(approved=True)
    for item in queryset:
        item.company.handle_company_interview_statics()


approve_company_review.short_description = 'Approve selected company reviews and update company statics'
approve_company_interview.short_description = 'Approve selected company interviews and update company statics'


@admin.register(Pros)
class ProsAdmin(admin.ModelAdmin):
    fields = ('name', 'logo', 'icon', 'is_deleted')
    list_display = ('name', 'logo', 'icon', 'is_deleted')


@admin.register(Cons)
class ConsAdmin(admin.ModelAdmin):
    fields = ('name', 'logo', 'icon', 'is_deleted')
    list_display = ('name', 'logo', 'icon', 'is_deleted')


@admin.register(CompanyReview)
class CompanyReviewAdmin(admin.ModelAdmin):
    fields = ('company', 'link_to_company', 'job', 'recommend_to_friend', 'pros', 'cons', 'state', 'work_life_balance',
              'salary_benefit', 'security', 'management', 'culture', 'over_all_rate', 'anonymous_job', 'title',
              'description', 'salary', 'salary_type', 'is_deleted', 'has_legal_issue', 'creator', 'link_to_user',
              'approved', 'ip', 'reply')
    list_display = ('company', 'link_to_company', 'job', 'approved', 'has_legal_issue', 'over_all_rate', 'title',
                    'salary', 'is_deleted', 'creator', 'link_to_user', 'created',)

    list_filter = ('state', 'approved', 'is_deleted', 'has_legal_issue',)
    readonly_fields = ('company', 'link_to_company', 'job', 'recommend_to_friend', 'pros', 'cons', 'state',
                       'work_life_balance', 'salary_benefit', 'security', 'management', 'culture', 'over_all_rate',
                       'anonymous_job', 'creator', 'link_to_user', 'ip', 'reply')
    search_fields = ('id', 'title', 'company__name', 'company__name_en', 'creator__username')
    actions = [approve_company_review]

    def link_to_company(self, obj):
        link = reverse("admin:company_company_change", args=[obj.company.id])
        return format_html('<a href="{}">Check {}</a>', link, obj.company)

    link_to_company.short_description = 'Check Company'

    def link_to_user(self, obj):
        link = reverse("admin:auth_user_change", args=[obj.creator.id])
        return format_html('<a href="{}">Check {}</a>', link, obj.creator)

    link_to_user.short_description = 'Check User'

    def get_form(self, request, obj=None, **kwargs):
        kwargs['widgets'] = {'description': forms.Textarea, 'title': forms.Textarea, 'reply': forms.Textarea}
        return super().get_form(request, obj, **kwargs)


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    fields = ('company', 'link_to_company', 'job', 'pros', 'cons', 'status', 'apply_method', 'interviewer_rate',
              'total_rate', 'title', 'description', 'asked_salary', 'offered_salary', 'interview_date',
              'response_time_before_review', 'response_time_after_review', 'is_deleted', 'has_legal_issue', 'creator',
              'link_to_user', 'approved', 'ip', 'reply',)
    list_display = ('company', 'link_to_company', 'job', 'total_rate', 'is_deleted', 'has_legal_issue', 'creator',
                    'link_to_user', 'approved',)

    list_filter = ('status', 'approved', 'is_deleted', 'has_legal_issue',)
    readonly_fields = ('company', 'link_to_company', 'job', 'pros', 'cons', 'status', 'apply_method',
                       'interviewer_rate',  'total_rate', 'interview_date', 'response_time_before_review',
                       'response_time_after_review', 'creator', 'link_to_user', 'ip', 'reply',)
    search_fields = ('id', 'title', 'company__name', 'company__name_en', 'creator__username')
    actions = [approve_company_interview]

    def link_to_company(self, obj):
        link = reverse("admin:company_company_change", args=[obj.company.id])
        return format_html('<a href="{}">Check {}</a>', link, obj.company)

    link_to_company.short_description = 'Check Company'

    def link_to_user(self, obj):
        link = reverse("admin:auth_user_change", args=[obj.creator.id])
        return format_html('<a href="{}">Check {}</a>', link, obj.creator)

    link_to_user.short_description = 'Check User'

    def get_form(self, request, obj=None, **kwargs):
        kwargs['widgets'] = {'description': forms.Textarea, 'title': forms.Textarea, 'reply': forms.Textarea}
        return super().get_form(request, obj, **kwargs)


@admin.register(ReviewComment)
class ReviewCommentAdmin(admin.ModelAdmin):
    fields = ('creator', 'body', 'is_deleted', 'created', 'review', 'link_to_review', 'ip',)
    list_display = ('creator', 'body', 'is_deleted', 'created', 'link_to_review',)

    list_filter = ('is_deleted',)
    readonly_fields = ('creator', 'review', 'created', 'link_to_review', 'ip',)

    def link_to_review(self, obj):
        link = reverse("admin:review_companyreview_change", args=[obj.review.id])
        return format_html('<a href="{}">Check {}</a>', link, obj.review)

    link_to_review.short_description = 'Check review'

    def get_form(self, request, obj=None, **kwargs):
        kwargs['widgets'] = {'body': forms.Textarea}
        return super().get_form(request, obj, **kwargs)


@admin.register(InterviewComment)
class InterviewCommentAdmin(admin.ModelAdmin):
    fields = ('creator', 'body', 'is_deleted', 'created', 'interview', 'link_to_interview', 'ip',)
    list_display = ('creator', 'body', 'is_deleted', 'created', 'link_to_interview',)

    list_filter = ('is_deleted',)
    readonly_fields = ('creator', 'interview', 'created', 'link_to_interview', 'ip',)

    def link_to_interview(self, obj):
        link = reverse("admin:review_interview_change", args=[obj.interview.id])
        return format_html('<a href="{}">Check {}</a>', link, obj.interview)

    link_to_interview.short_description = 'Check interview'

    def get_form(self, request, obj=None, **kwargs):
        kwargs['widgets'] = {'body': forms.Textarea}
        return super().get_form(request, obj, **kwargs)


admin.register(CompanyReview, CompanyReviewAdmin)
admin.register(Interview, InterviewAdmin)
admin.register(ReviewComment, ReviewCommentAdmin)
admin.register(InterviewComment, InterviewCommentAdmin)
admin.register(Pros, ProsAdmin)
admin.register(Cons, ConsAdmin)
