#!/usr/bin/env python

from django import forms
import os
import psutil
import math

class SearchForm(forms.Form):
    search_query = forms.CharField(label='', max_length=100)
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control me-2'
            visible.field.widget.attrs['placeholder'] = 'Search Machines'

class DownloadForm(forms.Form):
    download_link = forms.CharField(label='Download Link', max_length=200)
    action = forms.CharField(label='action')

class MachineForm(forms.Form):
    machine_name = forms.CharField(label='Machine Name', max_length=200)
    machine_file = forms.CharField(label='Machine File', max_length=200)
    action = forms.CharField(label='Machine File', max_length=20)

class StatusForm(forms.Form):
    machine_name = forms.CharField(label='Machine Name', max_length=200)
    machine_file = forms.CharField(label='Machine File', max_length=200)

class SettingsForm(forms.Form):
    adapter_choices = [tuple([x,x]) for x in os.listdir('/sys/class/net/')]
    max_ram = [tuple([x,x]) for x in range(256,((math.floor(psutil.virtual_memory().total*(1e-6)))+1), 256)]
    cpuCount = [tuple([x,x]) for x in range(1,os.cpu_count()+1)]
    cpu = forms.IntegerField(widget=forms.Select(choices=cpuCount))
    nic = forms.CharField(label='NIC',widget=forms.Select(choices=adapter_choices))
    ram = forms.IntegerField(widget=forms.Select(choices=max_ram))
    headless = forms.BooleanField(required=False)
    show_ip = forms.BooleanField(required=False)
