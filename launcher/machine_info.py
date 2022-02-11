#!/usr/bin/env python
from .vuln_download import get_all_vm_file_path
import os.path
import pathlib
import yaml

def get_machine_info():
    valid_extensions = ['vmdk', 'ova', 'iso', 'img', 'vdi']
    directory = os.path.expanduser('~/vulnlauncher_vms')
    all_vm_file_path = get_all_vm_file_path(directory, valid_extensions)
    vm_dict = dict()
    for vm_file_path in all_vm_file_path:
        vm_file = os.path.basename(vm_file_path)
        vm_name = vm_file_path.replace(f'/{vm_file}','').replace(f'{directory}/','')
        try:
            vm_dict[vm_name].append(vm_file)
        except KeyError:
            vm_dict[vm_name] = []
            vm_dict[vm_name].append(vm_file)
    print(vm_dict)
    return vm_dict

def write_default_settings(config_file_path):
    settings = {'vm_settings' : {'cpu': 1, 'nic': 'wlan0', 'ram': 512, 'headless': False, 'show_ip': True}}
    with open(config_file_path, 'w') as file:
        outputs = yaml.dump(settings, file)
        print(outputs)

def get_default_config():
    config_dir_path = os.path.expanduser('~/.config/vulnlauncher')
    config_file_path = config_dir_path + '/settings.yaml'
    if not os.path.isdir(config_dir_path):
        pathlib.Path(config_dir_path).mkdir(parents=True, exist_ok=True)
    if not os.path.isfile(config_file_path):
        pathlib.Path(config_file_path).touch()
        write_default_settings(config_file_path)
    with open(config_file_path) as file:
        try:
            vuln_config = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(exc)
    return vuln_config

def set_default_config(settings):
    config_dir_path = os.path.expanduser('~/.config/vulnlauncher')
    config_file_path = config_dir_path + '/settings.yaml'
    print(settings)
    with open(config_file_path, 'w') as file:
        outputs = yaml.dump({'vm_settings' : settings}, file)
        print(outputs)

def get_machine_config(name):
    config_dir_path = os.path.expanduser('~/.config/vulnlauncher')
    config_file_path = config_dir_path + '/settings.yaml'
    settings_name = f'{name}'
    with open(config_file_path) as file:
        try:
            config = yaml.safe_load(file)
            machine_config = config.get(settings_name)
        except yaml.YAMLError as exc:
            print(exc)
        if machine_config == None :
            machine_config = config.get('vm_settings')
            update_config(settings_name, machine_config)
    return {name:machine_config}

def update_config(name, settings):
    config_dir_path = os.path.expanduser('~/.config/vulnlauncher')
    config_file_path = config_dir_path + '/settings.yaml'
    with open(config_file_path, 'r') as file:
        temp = yaml.safe_load(file)
        temp[f'{name}'] = settings
    with open(config_file_path, 'w') as file:
        yaml.dump(temp, file)