"""cmdb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from web import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^acc_logout/',views.acc_logout),
    url(r'^index/',views.index),
    url(r'^create_project/',views.create_project),
    url(r'^create_task/',views.create_task),
    url(r'^create_template/',views.create_template),
    url(r'^accepting_task/',views.accepting_task),
    url(r'^handling_task/',views.handling_task),
    url(r'^handle_accepting_task/',views.handle_accepting_task),
    url(r'^show_accepting_task/',views.show_accepting_task),
    url(r'^show_handling_task/',views.show_handling_task),
    url(r'^download/',views.download),
    url(r'^handle_task/',views.handle_task),
    url(r'^launched_task/',views.list_launched_task),
    url(r'^all_task/',views.list_all_task),
    url(r'^participated_project/',views.list_participated_project),
    url(r'^participated_task/',views.list_participated_task),
    url(r'^delayed_task/',views.list_delayed_task),
    url(r'^record_talk/',views.record_talk),
]
