"""seafWeb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
import settings
import views


urlpatterns = [
    url(r'^admin', include(admin.site.urls)),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_URL}),
    url(r'^$', views.index, name='index'),
    url(r'^login', views.login, name='login'),
    url(r'^logout', views.logout),
    url(r'^404', views.error),
    url(r'^repo$', views.get_repo),
    url(r'^repo/file_list$', views.get_file_list),
    url(r'^repo/file_list/download$', views.download_file),
    url(r'^repo/download$', views.download_repo),
    url(r'^repo/progress$', views.get_download_progress),
    url(r'^create', views.create_repo),
    url(r'^sync', views.sync),
    url(r'^desync', views.desync),
    url(r'^cancel', views.cancel_sync_task),
]
