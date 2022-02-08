#!/usr/bin/env python

from django import forms

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
    cpu = forms.IntegerField(min_value=1)
    nic = forms.CharField(label='NIC', max_length=100)
    ram = forms.IntegerField(min_value=256)
    headless = forms.BooleanField(required=False)
    show_ip = forms.BooleanField(required=False)
