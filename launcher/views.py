from django.shortcuts import render
from .forms import SearchForm, DownloadForm, MachineForm, StatusForm, SettingsForm
from .scrape import search_machine, display_machine
from .vuln_download import vuln_download, cancel_download, move_vm_files, get_download_status, get_download_size, get_current_downloads
from .machine_info import get_machine_info, get_default_config, set_default_config, get_machine_config
from .vbox_interact import toggle_vm, check_status, find_vm_ip, delete_vm_files, remove_vm, settings_vm
from django.http import HttpResponse, HttpResponseRedirect
import json as simplejson

def index(request):
    search_form = SearchForm
    return render(request, 'launcher/index.html', {'search_form':search_form})

def search_query(request):
    if request.method == 'POST':
        search_form = SearchForm(request.POST)
        download_form = DownloadForm
        if search_form.is_valid():
            search_query = search_form.cleaned_data['search_query']
            all_machine_list = display_machine(search_machine(search_query))
            return render(request, 'launcher/search_result.html', {'machines':all_machine_list, 'form':download_form, 'search_form': search_form})
    return HttpResponseRedirect('/')

def download_machine(request):
    results = {'success':False}
    if request.method == 'POST':
        download_form = DownloadForm(simplejson.loads(request.body))
        if download_form.is_valid():
            download_link = download_form.cleaned_data['download_link']
            action = download_form.cleaned_data['action']
            results = {'success':True}
            if action == 'download':
                folder_name = vuln_download(download_link)
                move_vm_files(folder_name)
            elif action == 'cancel':
                cancel_download(download_link)
            elif action == 'size':
                total_size = get_download_size(download_link)
                results = {'success':True, 'total_size':total_size}
            elif action == 'status':
                status = get_download_status(download_link)
                results = {'status':status[0],'downloaded':status[1]}
        json = simplejson.dumps(results)
        return HttpResponse(json, content_type='application/json')
    elif request.method == 'GET':
        search_form = SearchForm()
        context = get_current_downloads()
        context['search_form'] = search_form
        print(context)
        return render(request, 'launcher/my_downloads.html', context)

def my_machines(request):
    search_form = SearchForm()
    machine_info = get_machine_info()
    print(machine_info)
    return render(request, 'launcher/my_machines.html', {'machine_info':machine_info, 'search_form':search_form})

def toggle_machine(request):
    results = {'success':False}
    if request.method == 'POST':
        machine_form = MachineForm(simplejson.loads(request.body))
        if machine_form.is_valid():
            action = machine_form.cleaned_data['action']
            if action == 'toggle':
                machine_file = machine_form.cleaned_data['machine_file']
                machine_name = machine_form.cleaned_data['machine_name']
                toggle_vm(machine_name, machine_file)
                results = {'success':True}
            elif action == 'delete':
                machine_file = machine_form.cleaned_data['machine_file']
                machine_name = machine_form.cleaned_data['machine_name']
                delete_vm_files(machine_name, machine_file)
                results = {'success':True}
            elif action == 'remove':
                machine_file = machine_form.cleaned_data['machine_file']
                machine_name = machine_form.cleaned_data['machine_name']
                remove_vm(machine_name, machine_file)
    json = simplejson.dumps(results)
    return HttpResponse(json, content_type='application/json')

def vm_status(request):
    results = {'status': 'Error'}
    if request.method == 'POST':
        status_form = StatusForm(simplejson.loads(request.body))
        if status_form.is_valid():
            machine_file = status_form.cleaned_data['machine_file']
            machine_name = status_form.cleaned_data['machine_name']
            results = check_status(machine_name, machine_file)
    json = simplejson.dumps(results)
    return HttpResponse(json, content_type='application/json')

def vm_ip(request):
    results = {'status': 'Error'}
    if request.method == 'POST':
       ip_form = StatusForm(simplejson.loads(request.body))
       if ip_form.is_valid():
            machine_file = ip_form.cleaned_data['machine_file']
            machine_name = ip_form.cleaned_data['machine_name']
            results = find_vm_ip(machine_name, machine_file)
    json = simplejson.dumps(results)
    return HttpResponse(json, content_type='application/json')

def settings(request):
    results = {'success': False}
    if request.method == 'GET':
        search_form = SearchForm()
        config = get_default_config()
        settings_form = SettingsForm(initial=config['vm_settings'])
        return render(request, 'launcher/settings.html', {'form': settings_form, 'vm_settings': config['vm_settings'], 'search_form': search_form})
    elif request.method == 'POST':
        settings_form = SettingsForm(request.POST)
        if settings_form.is_valid():
            cleaned_settings = settings_form.cleaned_data
            set_default_config(cleaned_settings)
            results = {'success': True}
    json = simplejson.dumps(results)
    return HttpResponse(json, content_type='application/json')

def machine_settings(request):
    results = {'success': False}
    if request.method == 'GET':
        machine_info = get_machine_info()
        name = list(machine_info.keys())[0] + '-' + (list(machine_info.values())[0])[0] + '_settings'
        print(name)
        search_form = SearchForm()
        config = get_machine_config(name)
        print(config)
        settings_form = SettingsForm(initial=config[name])
        return render(request, 'launcher/my_machines.html', {'form': settings_form, name: config[name], 'search_form': search_form})
    elif request.method == 'POST':
        settings_form = SettingsForm(request.POST)
        if settings_form.is_valid():
            cleaned_settings = settings_form.cleaned_data
            settings_vm(name, cleaned_settings)
            results = {'success': True}
    json = simplejson.dumps(results)
    return HttpResponse(json, content_type='application/json')