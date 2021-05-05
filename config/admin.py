from django.contrib import admin

from .models import IntegerConfig


@admin.register(IntegerConfig)
class IntegerConfigAdmin(admin.ModelAdmin):
    fields = ('name', 'value', 'description')
    list_display = ('name', 'value', 'description')


admin.register(IntegerConfig, IntegerConfigAdmin)
