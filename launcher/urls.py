#!/usr/bin/env python

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.search_query, name='search_query'),
    path('download', views.download_machine, name='download_machine'),
    path('my-machines', views.my_machines, name='my_machines'),
    path('toggle-vm', views.toggle_machine, name='toggle_vm'),
    path('vm-status', views.vm_status, name='vm_status'),
    path('vm-ip', views.vm_ip, name='vm_ip'),
    path('settings', views.settings, name='settings'),
]
