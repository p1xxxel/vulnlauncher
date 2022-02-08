#!/usr/bin/env python

import subprocess
import glob
import os
import os.path
import shutil
import yaml
from .machine_info import get_default_config

def list_vms():
    params = ['VBoxManage', 'list', 'vms']
    proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = proc.communicate()
    status = proc.wait()
    return output

def list_running_vms():
    params = ['VBoxManage', 'list', 'runningvms']
    proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = proc.communicate()
    status = proc.wait()
    return output

def create_vm(name):
    params = ['VBoxManage', 'createvm', '--name', name, '--register']
    proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = proc.communicate()
    print(output)
    print(error)
    status = proc.wait()

def attach_drive(drive_path, name):
    params = ['VBoxManage', 'storagectl', name, '--name', '"SCSI Controller"', '--add', 'scsi', '--bootable', 'on']
    proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = proc.communicate()
    status = proc.wait()
    params = ['VBoxManage', 'storageattach', name, '--storagectl', '"SCSI Controller"', '--port', '0', '--device', '0', '--type', 'hdd', '--medium', drive_path]
    proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = proc.communicate()
    status = proc.wait()

def attach_iso(iso_path, name):
    params = ['VBoxManage', 'storagectl', name, '--name', '"IDE Controller"', '--add', 'ide']
    proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = proc.communicate()
    status = proc.wait()
    params = ['VBoxManage', 'storagectl', name, '--name', '"IDE Controller"', '--port', '0', '--device', '0', '--type', 'dvddrive', '--medium', iso_path]
    proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = proc.communicate()
    status = proc.wait()

def attach_interface(interface, name):
    params = ['VBoxManage', 'modifyvm', name, '--nic1', 'bridged', '--bridgeadapter1', interface]
    proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = proc.communicate()
    status = proc.wait()

def add_memory(name, memory_size):
    params = ['VBoxManage', 'modifyvm', name, '--memory', memory_size]
    proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = proc.communicate()
    status = proc.wait()

def modify_cpu(name, cpu_num):
    params = ['VBoxManage', 'modifyvm', name, '--cpus', cpu_num]
    proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = proc.communicate()
    status = proc.wait()

def toggle_headless(name, headless_config):
    if headless_config:
        params = ['VBoxManage', 'modifyvm', name, '--defaultfrontend', 'headless']
    else:
        params = ['VBoxManage', 'modifyvm', name, '--defaultfrontend', 'gui']
    proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = proc.communicate()
    status = proc.wait()

def import_vm(path, name):
    extension = name.split('.')[-1]
    config = get_default_config()
    net_interface = config['vm_settings']['nic']
    memory_size = str(config['vm_settings']['ram'])
    headless_config = config['vm_settings']['headless']
    if extension == 'ova':
        params = ['VBoxManage', 'import',  path, "--vsys", "0", "--vmname", name]
        print(str(params))
        proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        print('reached')
        output, error = proc.communicate()
        print('reached 2')
        status = proc.wait()
        print(output)
        print(error)
        attach_interface(net_interface, name)
        toggle_headless(name, headless_config)
    elif extension == 'vmdk':
        create_vm(name)
        attach_drive(path, name)
        attach_interface(net_interface, name)
        add_memory(name, memory_size)
        toggle_headless(name, headless_config)
    elif extension == 'iso':
        create_vm(name)
        attach_iso(path, name)
        attach_interface(net_interface, name)
        add_memory(name, memory_size)
        toggle_headless(name, headless_config)
    if name in list_vms():
        return True, []
    return False

def poweroff_vm(name):
    params = ['VBoxManage', 'controlvm', name, 'poweroff']
    proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = proc.communicate()
    status = proc.wait()
    return output

def poweron_vm(name):
    params = ['VBoxManage', 'startvm', name]
    proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = proc.communicate()
    status = proc.wait()
    return output

def toggle_vm(machine_name, machine_file):
    name = machine_name + '-' + machine_file
    if name not in list_running_vms():
        if name in list_vms():
            poweron_vm(name)
        else:
            pathname = os.path.expanduser("~/vulnlauncher_vms")+f"/**/{machine_file}"
            path = glob.glob(pathname, recursive=True)
            path = path[0]
            print(path)
            print('-----')
            print(name)
            if import_vm(path, name):
                poweron_vm(name)
            else:
                pass
    else:
        poweroff_vm(name)

def check_status(machine_name, machine_file):
    name = machine_name + '-' + machine_file
    if name in list_running_vms():
        status = 'running'
    elif name in list_vms():
        status = 'not running'
    else:
        status = 'VM not found'
    return {'status': status}

def find_vm_ip(machine_name, machine_file):
    name = machine_name + '-' + machine_file
    params = ['VBoxManage', 'showvminfo', name]
    proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = proc.communicate()
    status = proc.wait()
    output = output.split('\n')
    for line in output:
        if line.startswith('NIC 1:'):
            mac_address = line.split(' ')[25][0:-1].lower()
    params = ['nmap', '-sP', '192.168.29.0/24']
    proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = proc.communicate()
    status = proc.wait()
    params = ['ip', 'neigh', 'show']
    proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = proc.communicate()
    status = proc.wait()
    output = output.split('\n')
    ip_address = 'none'
    for line in output:
        try:
            possible_mac = line.split(' ')[4].replace(':', '')
            if possible_mac == mac_address:
                ip_address = line.split(' ')[0]
        except:
            continue
    return {'ip':ip_address}

def delete_vm_files(machine_name, machine_file):
    remove_vm(machine_name, machine_file)
    pathname = os.path.expanduser("~")+f"/vulnlauncher_vms/**/{machine_name}"
    path = glob.glob(pathname, recursive=True)
    path = path[0]
    shutil.rmtree(path)
    return {'success': True}

def remove_vm(machine_name, machine_file):
    name = machine_name + '-' + machine_file
    params = ['VBoxManage', 'unregistervm', name]
    proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    output, error = proc.communicate()
    status = proc.wait()
    pathname = os.path.expanduser("~")+f"/VirtualBox VMs/**/{name}"
    path = glob.glob(pathname, recursive=True)
    path = path[0]
    shutil.rmtree(path)
    return {'success': True}
