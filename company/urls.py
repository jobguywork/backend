from django.urls import path, re_path
from django.views.decorators.cache import cache_page

from company import views as company_views


urlpatterns = [
    path('public/home/', company_views.HomeView.as_view()),
    path('public/faq/', cache_page(24*60*60, key_prefix='home_faq')(company_views.HomeFAQView.as_view())),
    # Benefit
    path('benefit/create/', company_views.BenefitCreateView.as_view()),
    path('benefit/list/', company_views.BenefitListView.as_view()),
    path('public/benefit/list/', company_views.UserBenefitListView.as_view()),
    path('benefit/<int:id>/update/', company_views.BenefitUpdateView.as_view()),
    path('benefit/<int:id>/delete/', company_views.BenefitDeleteView.as_view()),
    # City
    path('city/create/', company_views.CityCreateView.as_view()),
    path('city/list/', company_views.CityListView.as_view()),
    path('public/city/list/', company_views.UserCityListView.as_view()),
    path('city/<int:id>/update/', company_views.CityUpdateView.as_view()),
    path('city/<int:id>/delete/', company_views.CityDeleteView.as_view()),
    # Company
    path('company/approve/', company_views.CompaniesApproveView.as_view()),
    path('company/create/', company_views.CompanyCreateView.as_view()),
    path('company/insert/', company_views.CompanyInsertView.as_view()),
    path('company/insert/user/', company_views.UserCompanyInsertView.as_view()),
    path('company/list/', company_views.CompanyListView.as_view()),
    path('public/company/list/', company_views.UserCompanyListView.as_view()),
    path('public/company/name_list/', company_views.CompanyNameListView.as_view()),
    re_path(r'public/company/(?P<slug>[\w-]+)/interview/', company_views.CompanyInterReviewListView.as_view()),
    re_path(r'public/company/(?P<slug>[\w-]+)/review/', company_views.CompanyReviewListView.as_view()),
    re_path(r'public/company/(?P<slug>[\w-]+)/questions/', company_views.CompanyQuestionListView.as_view()),
    re_path(r'public/company/(?P<slug>[\w-]+)/salary/', company_views.CompanySalaryChartView.as_view()),
    re_path(r'admin/company/(?P<slug>[\w-]+)/interview/', company_views.AdminCompanyInterReviewListView.as_view()),
    re_path(r'admin/company/(?P<slug>[\w-]+)/review/', company_views.AdminCompanyReviewListView.as_view()),
    re_path(r'admin/company/(?P<slug>[\w-]+)/questions/', company_views.AdminCompanyQuestionListView.as_view()),
    path('company/<int:id>/update/', company_views.CompanyUpdateView.as_view()),
    path('company/<int:id>/delete/', company_views.CompanyDeleteView.as_view()),
    path('company/<int:id>/statics/', company_views.CompanyStaticsView.as_view()),
    re_path(r'public/company/(?P<slug>[\w-]+)/$', company_views.CompanyRetrieveView.as_view()),
    # Industry
    path('industry/create/', company_views.IndustryCreateView.as_view()),
    path('industry/list/', company_views.IndustryListView.as_view()),
    path('public/industry/list/', company_views.UserIndustryListView.as_view()),
    path('industry/<int:id>/update/', company_views.IndustryUpdateView.as_view()),
    path('industry/<int:id>/delete/', company_views.IndustryDeleteView.as_view()),
    # Province
    path('province/create/', company_views.ProvinceCreateView.as_view()),
    path('province/list/', company_views.ProvinceListView.as_view()),
    path('province/<int:id>/update/', company_views.ProvinceUpdateView.as_view()),
    path('province/<int:id>/delete/', company_views.ProvinceDeleteView.as_view()),
]
