#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import hashlib
from .vuln_download import get_download_size

def search_machine(search_term):
    site = 'https://www.vulnhub.com/'
    r = requests.get(site + '?q=' + search_term)
    soup = BeautifulSoup(r.text, 'lxml')
    link_set = set()
    for tags in soup.find_all('a'):
        try:
            url = tags.get('href')
            if(url.split('/')[1] == 'entry' and '#download' not in url):
#                print(url)
                link_set.add('https://www.vulnhub.com'+url)
        except:
            continue
#        if(url.split('/')[1] == 'entry' and '#download' not in url):
#            print(url)
#            link_set.add('https://www.vulnhub.com'+url)
    print(link_set)
    return link_set

def display_machine(link_set):
    all_machine_list = []
    for link in link_set:
        r = requests.get(link)
        soup = BeautifulSoup(r.text, 'lxml')
        machine_info = soup.find(id='release').find_all('li')
        machine_name = machine_info[0].get_text()
        date_of_release = machine_info[1].get_text()
        author_name = machine_info[2].get_text()
        machine_p_tag = soup.find(id='description').find_all('p')
        for tags in soup.find(id='download').find_all('a'):
            try:
                url = tags.get('href')
                if url.startswith("https://download.vulnhub.com") and not url.endswith(".torrent"):
                    machine_url = url
                    dl_file = url.split('/')[-1]
                    dl_file = dl_file.replace('.', '-')
                    print(machine_url)
            except:
                continue

        try:
            if len(machine_p_tag[0].get_text()) < 50:
                mini_desc = machine_p_tag[0].get_text()
            else:
                mini_desc = machine_p_tag[0].get_text()[0:50]
        except Exception as e:
            mini_desc = 'could not get machine description'
            print(e)
        machine_list = []
        try:
            machine_list.append(machine_name)
            machine_list.append(date_of_release)
            machine_list.append(author_name)
            machine_list.append(mini_desc)
            machine_list.append(machine_url)
            machine_list.append(dl_file)
            all_machine_list.append(machine_list)
        except UnboundLocalError as e:
            print(e)
            print(r.text)
    return all_machine_list
