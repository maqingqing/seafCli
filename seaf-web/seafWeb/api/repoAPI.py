import baseAPI
import os
import sys
import json


def get_repo_download_info(url, token):
    headers = { 'Authorization': 'Token %s' % token }
    repo_info = baseAPI.urlopen(url, headers=headers)

    return json.loads(repo_info)


def seaf_list_remote(url, token):
    '''List remote libraries'''

    # curl -H 'Authorization: Token ' -H 'Accept: application/json; indent=4' /api2/repos/
    repos = get_repo_download_info("%s/api2/repos/" % (url), token)
    printed = {}
    print "Name\tID"
    for repo in repos:
        if repo['id'] in printed:
            continue
        printed[repo['id']] = repo['id']
        print repo['name'], repo['id']
    return repos


def create_repo(url, token, name, desc, libpasswd):
    headers = { 'Authorization': 'Token %s' % token }
    data = {
        'name': name,
        'desc': desc,
    }
    if libpasswd:
        data['passwd'] = libpasswd
    repo_info_json = baseAPI.urlopen(url, data=data, headers=headers)
    repo_info = json.loads(repo_info_json)
    return repo_info['repo_id']


def seaf_create(url, token, name, desc, passwd=None, conf=None):
    '''Create a library'''
    conf_dir = baseAPI.DEFAULT_CONF_DIR
    if conf:
        conf_dir = conf
    conf_dir = os.path.abspath(conf_dir)

    # check url
    if not url:
        print "Seafile server url need to be presented"
        sys.exit(1)

    repo_id = create_repo("%s/api2/repos/" % (url), token, name, desc, passwd)
    print repo_id






