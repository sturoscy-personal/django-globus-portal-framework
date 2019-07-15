"""globus_portal_framework URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path, include, register_converter
from django.conf import settings
from globus_portal_framework.views import (
    search, index_selection, detail, detail_transfer, detail_preview, logout
)
from globus_portal_framework.api import restricted_endpoint_proxy_stream


class IndexConverter:

    @property
    def regex(self):
        """Allowing the regex to be a property makes it more flexible in
        testing, allowing urlpatterns to be rebuilt for test indexes."""
        return '({})'.format('|'.join(settings.SEARCH_INDEXES.keys()))

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(IndexConverter, 'index')

# search detail for viewing info about a single search result
search_urlpatterns = [
    path('<index:index>/', search, name='search'),
    path('<index:index>/detail-preview/<subject>/',
         detail_preview, name='detail-preview'),
    path('<index:index>/detail-preview/<subject>/<endpoint>/<path:url_path>/',
         detail_preview, name='detail-preview'),
    path('<index:index>/detail-transfer/<subject>', detail_transfer,
         name='detail-transfer'),
    path('<index:index>/detail/<subject>/', detail, name='detail'),
]

urlpatterns = [
    # Proxy remote file requests
    path('api/proxy/', restricted_endpoint_proxy_stream,
         name='restricted_endpoint_proxy_stream'),
    # Globus search portal. Provides default url '/'.
    path('logout/', logout, name='logout'),
    path('', index_selection, name='index-selection'),
    path('', include(search_urlpatterns)),
]


# Only include non-globus-portal-framework core URLs in development
if getattr(settings, 'GLOBUS_PORTAL_FRAMEWORK_DEVELOPMENT_APP', False):
    urlpatterns.extend([
        path('admin', admin.site.urls),
        path('', include('social_django.urls', namespace='social')),
        path('', include('globus_portal_framework.urls_debugging'))
    ])


handler404 = 'globus_portal_framework.views.handler404'
handler500 = 'globus_portal_framework.views.handler500'
