from django.contrib import admin

from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    fields = ('name', 'job_slug', 'cover', 'icon', 'description', 'is_deleted', 'approved')
    list_display = ('name', 'job_slug', 'cover', 'icon', 'description', 'is_deleted', 'approved')


admin.register(Job, JobAdmin)
