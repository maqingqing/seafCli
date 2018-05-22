# encoding=utf8
import baseAPI
import urllib
import urllib2
import json


def get_repo_download_info(url, token):
    headers = { 'Authorization': 'Token %s' % token }
    repo_info = baseAPI.urlopen(url, headers=headers)

    return json.loads(repo_info)


def seaf_download_file(url, token, repo_id, file_name):
    #curl  -v  -H 'Authorization: Token ' -H 'Accept: application/json; charset=utf-8; indent=4' 'https://cloud.seafile.com/api2/repos/dae8cecc-2359-4d33-aa42-01b7846c4b32/file/?p=/foo.c&reuse=1'
    headers = {'Authorization': 'Token %s' % token, 'Accept': 'application/json', 'charset': 'utf-8', 'indent': 4}

    url = "%s/api2/repos/%s/file/?%s" % (url, repo_id, urllib.urlencode({'p': file_name.encode('utf-8'), 'reuse': 1}))

    file_download_url = baseAPI.urlopen(url, headers=headers)
    return json.loads(file_download_url)

def seaf_file_list(url, token, repo_id, path):
    header = {'Authorization': 'Token %s' % token, 'Accept': 'application/json', 'charset': 'utf-8', 'indent': 4}
    if not path:
        path = '/'

    url = "%s/api2/repos/%s/dir/?%s" % (url, repo_id, urllib.urlencode({'p': path}))

    file_list = baseAPI.urlopen(url, headers=header)

    return json.loads(file_list)
