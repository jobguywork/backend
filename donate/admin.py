from django.contrib import admin

from donate.models import Donate


@admin.register(Donate)
class DonateAdmin(admin.ModelAdmin):
    fields = ('id', 'name', 'amount', 'coin', 'cost', 'created', 'link', 'is_active',)
    list_display = ('id', 'name', 'amount', 'coin', 'cost', 'created', 'link', 'is_active',)
    search_fields = ('name',)
    list_filter = ('is_active', 'coin')
    readonly_fields = ('id', 'created',)

    def has_delete_permission(self, request, obj=None):
        if obj and not obj.is_active:
            return True
        return False


admin.register(Donate, DonateAdmin)
