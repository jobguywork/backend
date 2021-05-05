from django.contrib import admin

from .models import Question, Answer


class AnswerAdminInline(admin.TabularInline):
    model = Answer
    fields = ('question', 'body', 'creator', 'created', 'is_deleted')
    readonly_fields = ('created', 'question', 'body', 'creator',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    fields = ('company', 'title', 'question_slug', 'body', 'creator', 'created', 'is_deleted')
    list_display = ('company', 'title', 'question_slug', 'body', 'creator', 'created', 'is_deleted')
    readonly_fields = ('created', 'company', 'title', 'question_slug', 'body', 'creator', 'created',)
    inlines = (AnswerAdminInline,)


admin.register(Question, QuestionAdmin)
