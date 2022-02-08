#!/usr/bin/env python

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from urllib.parse import urlparse
import urllib.request
import patoolib
import requests
import time
import os, pathlib
import glob
import shutil
import subprocess
import yaml

def download_file(url):
    local_filename = url.split('/')[-1]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0'}
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True, headers=headers) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk:
                f.write(chunk)
    return local_filename
#def download_file(url):
#    local_filename = url.split('/')[-1]
#    params = ['curl', url, '-o', local_filename]
#    proc = subprocess.Popen(params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
#    output, error = proc.communicate()
#    status = proc.wait()
#def download_file(url):
#    local_filename = url.split('/')[-1]
#    print(url)
#    urllib.request.urlretrieve(url, local_filename)
#    return local_filename


def vuln_download(url):
    try:
        result = urlparse(url)
        if result.hostname != 'download.vulnhub.com':
            raise ValidationError(f'The hostname {result.hostname} is not allowed.')
        else:
            print(url)
            add_download(url, 'downloading')
            begin = time.time()
            file_name = download_file(url)
            end = time.time()
            if os.path.isfile(f'./{file_name}'):
                add_download(url, 'downloaded')
            print(f'Took {end-begin} to download {file_name}')
    except:
        raise ValidationError('invalid url')
    if file_name.endswith('tar.gz'):
        folder_name = file_name[:-7]
    elif file_name.endswith('tar.bz2'):
        folder_name = file_name[:-8]
    else:
        folder_name = os.path.splitext(file_name)[0]
    if not os.path.isdir(os.path.expanduser('~')+f'/vulnlauncher_vms/{folder_name}'):
        pathlib.Path(os.path.expanduser('~')+f'/vulnlauncher_vms/{folder_name}').mkdir(parents=True, exist_ok=True)
    if not os.path.isdir('./tmp'):
        os.mkdir('./tmp')
    if not os.path.isdir(f'./tmp/{folder_name}'):
        os.mkdir(f'./tmp/{folder_name}')
    print("Trying to extract vm files...")
#    begin = time.time()
#    patoolib.extract_archive(file_name, outdir=f'./tmp/{folder_name}')
#    end = time.time()
#    print(f'Took {end-begin} to extract')
#    print(f'Deleting {file_name}')
#    os.remove(file_name)
    valid_archives = ['tar.gz', 'tar.bz2', 'zip', 'rar', '7z', 'tar']
    for ext in valid_archives:
        if file_name.endswith(ext):
            try:
                extract_files(file_name, f'./tmp/{folder_name}')
                return folder_name
            except:
                if os.path.isdir(os.path.expanduser('~')+f'/vulnlauncher_vms/{folder_name}'):
                    os.rmdir(os.path.expanduser('~')+f'/vulnlauncher_vms/{folder_name}')
                if os.path.isdir(f'./tmp/{folder_name}'):
                    os.rmdir(f'./tmp/{folder_name}')

    print("--WORKING--")
    valid_extensions = ['vmdk', 'ova', 'nvram', 'iso', 'img', 'vdi']
    for ext in valid_extensions:
        if file_name.endswith(ext):
            os.rename(f'./{file_name}',f'./tmp/{folder_name}/{file_name}')
            print("--RENAMED--")
            return folder_name
#    extract_files(file_name, f'./tmp/{folder_name}')
    return folder_name

def extract_files(file_name, outdir):
    begin = time.time()
    patoolib.extract_archive(file_name, outdir=outdir)
    end = time.time()
    print(f'Took {end-begin} to extract')
    print(f'Deleting {file_name}')
    os.remove(file_name)

def get_all_vm_file_path(folder_name, valid_extensions):
    valid_pathnames = []
    all_vm_file_path = []
    directory = folder_name
    for ext in valid_extensions:
        pathname = directory + "/**/*." + ext
        valid_pathnames.append(pathname)
    for pathname in valid_pathnames:
        possible_vm_paths = (glob.glob(pathname, recursive=True))
        for possible_vm_path in possible_vm_paths:
            all_vm_file_path.append(possible_vm_path)
    return all_vm_file_path

def check_if_file_exists(file_name, folder_path):
    pathname = folder_path + f"/**/{file_name}"
    possible_path = glob.glob(pathname, recursive=True)
    if possible_path:
        return True
    else:
        return False

def move_vm_files(folder_name):
#    valid_extensions = ['vmdk', 'ova', 'nvram', 'iso', 'img', 'vdi']
#    valid_pathnames = []
#    directory = f"./tmp/{folder_name}"
#    for ext in valid_extensions:
#        pathname = directory + "/**/*." + ext
#        valid_pathnames.append(pathname)
#    for pathname in valid_pathnames:
#        possible_vm_paths = (glob.glob(pathname, recursive=True))
#        for possible_vm_path in possible_vm_paths:
#            possible_vm_file = os.path.basename(possible_vm_path)
#            os.rename(possible_vm_path, f'/home/p1xel/test/vms/{folder_name}/{possible_vm_file}')
    valid_extensions = ['vmdk', 'ova', 'nvram', 'iso', 'img', 'vdi']
    all_vm_file_path = get_all_vm_file_path(f'./tmp/{folder_name}', valid_extensions)
    print(all_vm_file_path)
    for vm_file_path in all_vm_file_path:
        vm_file = os.path.basename(vm_file_path)
        os.rename(vm_file_path, os.path.expanduser('~')+f'/vulnlauncher_vms/{folder_name}/{vm_file}')
    try:
        shutil.rmtree(f'./tmp/{folder_name}')
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))

def cancel_download(url):
    file_name = url.split('/')[-1]
    if os.path.exists(file_name):
        os.remove(file_name)
    remove_download(url,'downloading')

def get_download_status(url):
    file_name = url.split('/')[-1]
    status = []
    if os.path.exists(file_name):
        local_file_size = os.path.getsize(file_name)
        status.append('downloading')
    else:
        local_file_size = get_download_size(url)
        status.append('downloaded')
    status.append(local_file_size)
    return status

def get_download_size(url):
    r = requests.request('HEAD',url)
    total_file_size = r.headers['Content-Length']
    return total_file_size

def get_current_downloads():
    config_dir_path = os.path.expanduser('~/.config/vulnlauncher')
    download_file_path = config_dir_path + '/downloads.yaml'
    if not os.path.isdir(config_dir_path):
        pathlib.Path(config_dir_path).mkdir(parents=True, exist_ok=True)
    if not os.path.isfile(download_file_path):
        pathlib.Path(download_file_path).touch()
        with open(download_file_path, 'w') as file:
            yaml.dump({'downloading':{},'downloaded':{}},file)
    with open(download_file_path) as file:
        try:
            current_downloads = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(exc)
    return current_downloads

def add_download(url,status):
    config_dir_path = os.path.expanduser('~/.config/vulnlauncher')
    download_file_path = config_dir_path + '/downloads.yaml'
    if not os.path.isdir(config_dir_path):
        pathlib.Path(config_dir_path).mkdir(parents=True, exist_ok=True)
    if not os.path.isfile(download_file_path):
        pathlib.Path(download_file_path).touch()
        with open(download_file_path, 'w') as file:
            yaml.dump({'downloading':{},'downloaded':{}},file)
    current_downloads = get_current_downloads()
    try:
        if status == 'downloaded':
            current_downloads[status][url] = current_downloads['downloading'][url]
            current_downloads['downloading'].pop(url)
        elif status == 'downloading':
            current_downloads[status][url] = get_download_size(url)
        with open(download_file_path, 'w') as file:
            yaml.dump(current_downloads, file)
        return {'Success': 'True'}
    except KeyError:
        return {'Error': 'Section not found'}

def remove_download(url, status):
    config_dir_path = os.path.expanduser('~/.config/vulnlauncher')
    download_file_path = config_dir_path + '/downloads.yaml'
    current_downloads = get_current_downloads()
    current_downloads[status].pop(url)
    with open(download_file_path, 'w') as file:
        yaml.dump(current_downloads, file)
