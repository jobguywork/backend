"""ratecompany URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls import url
from django.views.decorators.cache import cache_page
from django.views.static import serve
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework_swagger.views import get_swagger_view
from django.contrib.sitemaps import views as sitemap_views

from authnz import urls as authnz_urls
from company import urls as company_urls
from donate import urls as donate_urls
from job import urls as job_urls
from review import urls as review_urls
from question import urls as question_urls
from utilities import urls as utils_urls
from ratecompany.site_map import CompanySitemap, ReviewSitemap, InterviewSitemap, index as sitemap_index


schema_view = get_swagger_view(title='Job Guy API')


urlpatterns = [
    path('swagger/', schema_view),
    path('admin/', admin.site.urls),
    path('authnz/', include(authnz_urls)),
    path('utilities/', include(utils_urls)),
    path('', include(company_urls)),
    path('', include(donate_urls)),
    path('', include(job_urls)),
    path('', include(review_urls)),
    path('', include(question_urls)),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    path('sitemap.xml', cache_page(10, key_prefix='sitemap_index')(sitemap_index),
         {'sitemaps': {'company': CompanySitemap, 'review': ReviewSitemap, 'interview': InterviewSitemap}}),
    path('sitemap-<section>.xml', cache_page(10, key_prefix='sitemap_company')(sitemap_views.sitemap),
         {'sitemaps': {'company': CompanySitemap, 'review': ReviewSitemap, 'interview': InterviewSitemap},
          'template_name': 'utilities/sitemap.xml'}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += [
        path('swagger/', schema_view),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'utilities.responses.handler404'
handler500 = 'utilities.responses.handler500'
