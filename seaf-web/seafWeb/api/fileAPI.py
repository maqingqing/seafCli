# encoding=utf8
import baseAPI
import urllib
import urllib2
import json
import os.path


def get_repo_download_info(url, token):
    headers = { 'Authorization': 'Token %s' % token }
    repo_info = baseAPI.urlopen(url, headers=headers)

    return json.loads(repo_info)


def seaf_download_file(url, token, repo_id, file_name, file_type):
    #curl  -v  -H 'Authorization: Token ' -H 'Accept: application/json; charset=utf-8; indent=4' 'https://cloud.seafile.com/api2/repos/dae8cecc-2359-4d33-aa42-01b7846c4b32/file/?p=/foo.c&reuse=1'
    headers = {'Authorization': 'Token %s' % token, 'Accept': 'application/json', 'charset': 'utf-8', 'indent': 4}

    if file_type == 'dir':
        #GET https://cloud.seafile.com/api/v2.1/query-zip-progress/?token={token}
        file_server = url[:url.rfind(':')] + ":8082"
        file_type = "dir_zip"
        zip_token = seaf_download_file(url, token, repo_id, file_name, file_type)
        url = "%s/api/v2.1/query-zip-progress/?%s" % (url, urllib.urlencode({'token': zip_token.get('zip_token').encode('utf-8')}))
        zip_progress = json.loads(baseAPI.urlopen(url, headers=headers))
        if zip_progress.get('zipped') == zip_progress.get('total') :
            file_server = file_server + "/zip/" + zip_token.get('zip_token')
            print file_server
            return file_server
        else:
            return None
    elif file_type == 'dir_zip':
        # GET https://cloud.seafile.com/api/v2.1/repos/{repo-id}/zip-task/?parent_dir={parent_dir}&dirents={dir}
        parent_dir, dir_name = os.path.split(file_name)
        url = "%s/api/v2.1/repos/%s/zip-task/?%s" % (url, repo_id, urllib.urlencode({'parent_dir': parent_dir.encode('utf-8'), 'dirents': dir_name.encode('utf-8')}))
    else:
        url = "%s/api2/repos/%s/file/?%s" % (url, repo_id, urllib.urlencode({'p': file_name.encode('utf-8'), 'reuse': 1}))

    file_download_url = baseAPI.urlopen(url, headers=headers)
    return json.loads(file_download_url)


def delete_file(url, token, repo_id, file_name, file_type):
    #curl - X DELETE - v - H 'Authorization: Token {token}' - H 'Accept: application/json; charset=utf-8; indent=4' {serveraddr}/api2/repos/{repo-id}/file/?p=/foo
    headers = {'Authorization': 'Token %s' % token, 'Accept': 'application/json', 'charset': 'utf-8', 'indent': 4}

    if file_type == 'dir':
        #https: // cloud.seafile.com / api2 / repos / {repo - id} / dir /
        url = "%s/api2/repos/%s/dir/?%s" % (url, repo_id, urllib.urlencode({'p': file_name.encode('utf-8')}))
        print url
    else:
        url = "%s/api2/repos/%s/file/?%s" % (url, repo_id, urllib.urlencode({'p': file_name.encode('utf-8')}))

    err = baseAPI.urlopen(url, headers=headers, method='DELETE')
    print type(err)
    return json.loads(err)


def seaf_file_list(url, token, repo_id, path):
    header = {'Authorization': 'Token %s' % token, 'Accept': 'application/json', 'charset': 'utf-8', 'indent': 4}
    if not path:
        path = '/'

    url = "%s/api2/repos/%s/dir/?%s" % (url, repo_id, urllib.urlencode({'p': path}))

    file_list = baseAPI.urlopen(url, headers=header)

    return json.loads(file_list)

def get_file_upload_link(url, token, repo_id, file_path):
    '''curl - H
    "Authorization: Token "
    https: // cloud.seafile.com / api2 / repos / 99
    b758e6 - 91
    ab - 4265 - b705 - 925367374
    cf0 / upload - link /'''
    headers = {'Authorization': 'Token %s' % token}
    url = "%s/api2/repos/%s/upload-link/?%s" % (url, repo_id, urllib.urlencode({'from': 'web', 'p': file_path.encode('utf-8')}))
    print url,1111
    file_upload_url = baseAPI.urlopen(url, headers=headers)
    return json.loads(file_upload_url)

