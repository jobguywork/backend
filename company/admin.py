from django.contrib import admin
from django.core.cache import cache
from django.conf import settings
from django import forms
from django.utils.safestring import mark_safe

from .models import Company, Industry, Benefit, Province, City, Gallery


def approve_company(modeladmin, request, queryset):
    queryset.update(approved=True)
    cache.delete(settings.COMPANY_NAME_LIST)


approve_company.short_description = 'Approve selected companies and clear company cache'


def update_company_statics(modeladmin, request, queryset):
    for company in queryset.all():
        company.handle_company_review_statics()
        company.handle_company_interview_statics()


update_company_statics.short_description = 'Update company static review & interview'


class GalleryAdminInline(admin.TabularInline):
    model = Gallery
    can_delete = False

    fields = ('path', 'image_tag', 'description', 'is_deleted')
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        return mark_safe('<img src="{}{}"  width="200" height="200" />'.format(settings.MEDIA_BASE_PATH, obj.path))

    image_tag.short_description = 'Image'


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    fields = ('name', 'name_en', 'description', 'user', 'logo', 'logo_tag', 'cover', 'cover_tag', 'industry',
              'company_slug', 'founded', 'benefit', 'size', 'is_deleted', 'has_legal_issue', 'is_cheater',
              'approved', 'tell', 'site', 'city', 'location_point', 'is_famous', 'has_panel_moderator',)
    list_display = ('name', 'name_en', 'size', 'is_deleted', 'has_legal_issue', 'is_cheater', 'approved',
                    'user_generated', 'site', 'total_review', 'over_all_rate', 'company_score')

    search_fields = ('name', 'name_en')
    readonly_fields = ('logo_tag', 'cover_tag', 'name', 'name_en',)
    list_filter = ('approved', 'user_generated', 'is_deleted', 'is_cheater', 'has_legal_issue', 'size')
    list_max_show_all = 100
    list_per_page = 100
    actions = [approve_company, update_company_statics]
    inlines = (GalleryAdminInline,)
    filter_horizontal = ('benefit',)
    autocomplete_fields = ('city', 'industry', 'user')

    def logo_tag(self, obj):
        return mark_safe('<img src="{}{}"  width="100" height="100" />'.format(settings.MEDIA_BASE_PATH, obj.logo))

    logo_tag.short_description = 'Logo display'

    def cover_tag(self, obj):
        return mark_safe('<img src="{}{}"  width="700" height="200" />'.format(settings.MEDIA_BASE_PATH, obj.cover))

    cover_tag.short_description = 'Cover display'

    def get_form(self, request, obj=None, **kwargs):
        kwargs['widgets'] = {'description': forms.Textarea}
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.delete(settings.COMPANY_NAME_LIST)


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'logo', 'icon', 'industry_slug', 'supported', 'is_deleted')
    list_display = ('name', 'description', 'logo', 'icon', 'industry_slug', 'supported', 'is_deleted')
    search_fields = ('name',)


@admin.register(Benefit)
class BenefitAdmin(admin.ModelAdmin):
    fields = ('name', 'logo', 'icon', 'supported', 'is_deleted')
    list_display = ('name', 'logo', 'icon', 'supported', 'is_deleted')


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    fields = ('name', 'latitude', 'longitude', 'supported', 'is_deleted')
    list_display = ('name', 'latitude', 'longitude', 'supported', 'is_deleted')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.delete(settings.CITY_CACHE_LIST)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    fields = ('name', 'latitude', 'longitude', 'supported', 'is_deleted', 'province',
              'show_name', 'city_slug', 'priority')
    list_display = ('name', 'latitude', 'longitude', 'supported', 'is_deleted', 'province', 'show_name', 'city_slug',
                    'priority')
    search_fields = ('name', 'show_name')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.delete(settings.CITY_CACHE_LIST)


admin.register(Company, CompanyAdmin)
admin.register(Industry, IndustryAdmin)
admin.register(Benefit, BenefitAdmin)
admin.register(Province, ProvinceAdmin)
admin.register(City, CityAdmin)
