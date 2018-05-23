# coding=utf-8
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import time

from api import syncAPI, baseAPI, repoAPI, fileAPI, utilsAPI
from api.error import Error

CONF_DIR = "/home/qingqing/mqq/seafWeb/ccnet"
SERVER_ADDR = "http://192.168.123.117:8000"


class Repo(object):
    def __init__(self,name, size, id, mtime, sync_status, encrypted):
        self.name = name
        self.size = size
        self.mtime = mtime
        self.sync_status = sync_status
        self.encrypted = encrypted


def index(request):
    username = request.session.get('username')

    if username:
        # print request.session
        response = HttpResponseRedirect("/repo")
        return response
    else:
        resLogin = HttpResponseRedirect('/login')
        return resLogin


def login(request):

    if request.method == "GET":
       # baseAPI.seaf_start_all(CONF_DIR)
        return render_to_response("login.html")

    if request.method == "POST":

        username = request.POST.get('username', None)
        passwd = request.POST.get('passwd', None)
        serveraddr = request.POST.get('serveraddr', None)
        if not username or not passwd or not serveraddr:
            return render_to_response("login.html")

        token = baseAPI.get_token(serveraddr, username, passwd, CONF_DIR)

        if isinstance(token, Error):
            return render_to_response('login.html',{'err': token.errorMessage,
                                                    'username': username,
                                                    'passwd': passwd,
                                                    'serveraddr': serveraddr})

        if token is not None:
            response = HttpResponseRedirect("/repo")
            request.session['username'] = username
            request.session['passwd'] = passwd
            request.session['serveraddr'] = serveraddr
            request.session['token'] = token
            # response.set_cookie('token', token)
            # response.set_cookie('serveraddr', serveraddr)
            # response.set_cookie('user', username)
            return response


def logout(request):
    del request.session['username']
    return HttpResponseRedirect('/')


def error(request):
    return render_to_response('404.html')


def get_repo(request):
    ctx = {'repo_list': [], 'repo_id': [], 'repo_share_list': [], 'repo_share_all_list': [], 'repo_group_list': {}, 'repo_sync_list': []}

    serveraddr = request.session.get('serveraddr')
    token = request.session.get('token')

    repos = repoAPI.seaf_list_remote(serveraddr, token)
    repos_sync = sync_local_status(request)
    temp_repo_sync = []
    # repos_sync = {}
    new_sync = syncAPI.seaf_sync_progress(CONF_DIR)
    # print repos
    for r in repos:
        t = time.strftime("%Y-%m-%d %H:%M", time.localtime(r.get('mtime')))

        sync_status = "unsync"
        sync_path = None
        if r.get('id') in repos_sync:

            sync_status = repos_sync[r.get('id')]['state']
            sync_path = repos_sync[r.get('id')]['path']
            if r.get('id') not in temp_repo_sync:
                ctx['repo_sync_list'].append({'name': r.get('name'),
                                     'id': r.get('id'),
                                     'size': utilsAPI.convertBytes(r.get('size')),
                                     'time': t,
                                     'sync_path': sync_path,
                                     'sync_status': sync_status,
                                     'encrypted': r.get('encrypted'), })
                temp_repo_sync.append(r.get('id'))
        elif r.get('id') in new_sync:
            sync_status = new_sync[r.get('id')]

        ctx['repo_id'].append(r.get('id'))
        print 33333333333333333333333333333333
        print r.get('type')

        if r.get('type') == 'repo':
            ctx['repo_list'].append({'name': r.get('name'),
                                     'id': r.get('id'),
                                     'size': r.get('size_formatted'),
                                     'time': t,
                                     'sync_path': sync_path,
                                     'sync_status': sync_status,
                                     'encrypted': r.get('encrypted'), })

        elif r.get('type') == 'srepo':
            ctx['repo_share_list'].append({'name': r.get('name'),
                                           'id': r.get('id'),
                                           'size': r.get('size_formatted'),
                                           'time': t,
                                           'sync_path': sync_path,
                                           'sync_status': sync_status,
                                           'encrypted': r.get('encrypted'),
                                           'owner': r.get('owner'),
                                           'permission': r.get('permission')})

        else:
            # group repo
            if r.get('share_type') == 'public':
                ctx['repo_share_all_list'].append({'name': r.get('name'),
                                               'id': r.get('id'),
                                               'size': r.get('size_formatted'),
                                               'time': t,
                                               'sync_path': sync_path,
                                               'sync_status': sync_status,
                                               'encrypted': r.get('encrypted'),
                                               'owner': r.get('share_from'),
                                               'permission': r.get('permission')})
            else:
                if not ctx['repo_group_list'].get(r.get('group_name'),None):
                    ctx['repo_group_list'][r.get('group_name')] = []
                ctx['repo_group_list'][r.get('group_name')].append({'name': r.get('name'),
                                               'id': r.get('id'),
                                               'size': utilsAPI.convertBytes(r.get('size')),
                                               'time': t,
                                               'sync_path': sync_path,
                                               'sync_status': sync_status,
                                               'encrypted': r.get('encrypted'),
                                               'group_name':r.get('group_name'),
                                               'permission': r.get('permission')})

    ctx['username'] = request.session.get('username')
    server_addr_split = request.session.get('serveraddr').split('//')[1].split(':')[0]
    ctx['serveraddr'] = server_addr_split
    page = request.GET.get('page', None)

    if page:
        return render_to_response("repo/" + page.lower() + ".html", ctx)
    return render_to_response("homepage.html", ctx)


def create_repo(request):

    token = request.session.get('token')
    serveraddr = request.session.get('serveraddr')

    name = request.POST.get('name', 'library')
    desc = request.POST.get('desc', 'test')
    passwd = request.POST.get('passwd', None)

    repo_id = repoAPI.seaf_create(serveraddr, token, name, desc, passwd, CONF_DIR)

    if repo_id:
        return JsonResponse({'result': 'ok', 'state': 1})
    return JsonResponse({'result': 'failed', 'state': 0})


def download_repo(request):

    token = request.session.get('token')
    serveraddr = request.session.get('serveraddr')

    repo_id = request.POST.get('repo_id')
    download_dir = request.POST.get('path')
    passwd = request.POST.get('passwd')

    if not download_dir:
        return JsonResponse({"res": "local path err", "state": -2})
    err = syncAPI.seaf_download(CONF_DIR, repo_id, token, download_dir, serveraddr, passwd=passwd)
    if err:
        return JsonResponse({"res": err.errorMessage, "state": err.errorCode})
    return JsonResponse({"res": "ok", "state": 1})


def get_file_list(request):

    token = request.session.get('token')
    serveraddr = request.session.get('serveraddr')

    path = request.GET.get('path','')

    repo_id = request.GET.get('repo_id')

    file_list = fileAPI.seaf_file_list(serveraddr, token, repo_id, path)
    # print file_list
    for i in range(len(file_list)):
        file = file_list[i]
        file_list[i]['mtime'] = time.strftime("%Y-%m-%d %H:%M", time.localtime(file.get('mtime')))
        if file.get('size', None):
            file_list[i]['size'] = utilsAPI.convertBytes(file['size'])

    # print(type(file_list))
    return render_to_response('filelist.html', {'file_list': file_list, 'repo_id': repo_id, 'parent_dir': path})


def download_file(request):

    token = request.session['token']
    serveraddr = request.session['serveraddr']
    file_name = request.GET.get("file_name")
    repo_id = request.GET.get("repo_id")
    # print "%s %s" %(file_name, repo_id)
    download_file_url = fileAPI.seaf_download_file(serveraddr, token, repo_id, file_name)

    return JsonResponse({"res": "ok", "download_url": download_file_url, "state": 1})


def sync(request):
    sync_repo_id = request.POST.get("repo_id")
    sync_local_path = request.POST.get("path")
    passwd = request.POST.get('passwd')
    token = request.session['token']
    serveraddr = request.session['serveraddr']
    if not sync_local_path:
        return JsonResponse({"res": "local path err", "state": -2})
    err = syncAPI.seaf_sync(CONF_DIR, sync_repo_id, sync_local_path, token, serveraddr, passwd)
    if err:
        return JsonResponse({"res": err.errorMessage, "state": err.errorCode})
    return JsonResponse({"res": "ok", "state": 1})


def desync(request):
    path_local = request.GET.get("path")
    syncAPI.seaf_desync(CONF_DIR, path_local)
    return JsonResponse({"result": "ok", "state": 1})


def cancel_sync_task(request):

    repo_id = request.GET.get('repoid')
    if not repo_id:
        return JsonResponse({"res": "err", "state": -2})
    err = syncAPI.seaf_cancel_sync_task(CONF_DIR,repo_id)
    if err:
        return JsonResponse({"res": err, "state": -2})
    return JsonResponse({"res": "ok", "state": 1})


def sync_local_status(request):
    return syncAPI.seaf_status(CONF_DIR)


def sync_local_list(request):
    return syncAPI.seaf_list(CONF_DIR)


def get_download_progress(request):

    print 'sync'

    download_rate, upload_rate = syncAPI.seaf_get_rate(CONF_DIR)

    upload_rate_s = str(utilsAPI.convertBytes(upload_rate)) + "/s"
    download_rate_s = str(utilsAPI.convertBytes(download_rate)) + "/s"
    # print "download_rate: %s  upload_rate: %s " %(download_rate_s, upload_rate_s)

    repo_id = request.GET.get('repo_id')
    print repo_id
    if not repo_id:
        return JsonResponse({"state": "unknown", 'download_rate': download_rate_s, 'upload_rate': upload_rate_s})
    print 1
    progress = syncAPI.seaf_sync_progress(CONF_DIR, repo_id)
    print 2
    state = progress.get('state', None)
    # the sync_task have existed
    repos_sync = sync_local_status(request)
    if repo_id in repos_sync:
        if repos_sync[repo_id]['state'] == "uploading" or repos_sync[repo_id]['state'] == "downloading":
            rate = str(utilsAPI.convertBytes(repos_sync[repo_id]['rate'])) + "/s"
            if repos_sync[repo_id]['total'] != 0:
                finish = float(repos_sync[repo_id]['finish'])
                total = float(repos_sync[repo_id]['total'])
                return JsonResponse({"state": repos_sync[repo_id]['state'], 'progress': str(round(finish / total, 3) * 100),
                                     'rate': rate, 'download_rate': download_rate_s,
                                     'upload_rate': upload_rate_s})
            else:
                return JsonResponse({"state": repos_sync[repo_id]['state'], 'progress': -1,
                                     'rate': rate, 'download_rate': download_rate_s,
                                     'upload_rate': upload_rate_s})
        else:
            return JsonResponse(
                {"state": repos_sync[repo_id]['state'], 'progress': -1, 'rate': None, 'download_rate': download_rate_s,
                 'upload_rate': upload_rate_s})

    if state == 'downloading':
        finish = float(progress.get('finish'))
        total = float(progress.get('total'))
        # print round(finish / total, 3) * 100
        # print type(round(finish / total, 3) * 100)
        return JsonResponse({"state": state, 'progress': str(round(finish / total, 3) * 100) ,
                             'rate': str(utilsAPI.convertBytes(progress.get('rate') * 1024)) + "/s",
                             'download_rate': download_rate_s, 'upload_rate': upload_rate_s})
    elif state == 'checkout':
        finish = float(progress.get('finish'))
        total = float(progress.get('total'))
        # print "rate : %s" % progress.get('rate')
        return JsonResponse({"state": state, 'progress': str(round(finish / total, 3) * 100),
                             'rate': str(utilsAPI.convertBytes(progress.get('rate') * 1024)) + "/s",
                             'download_rate': download_rate_s, 'upload_rate': upload_rate_s})
    elif state == 'finish':

        return JsonResponse({"state": state, 'download_rate': download_rate_s, 'upload_rate': upload_rate_s})
    elif state == 'error':
        return JsonResponse({"state": state,'message': progress.get('message'), 'download_rate': download_rate_s,
                             'upload_rate': upload_rate_s})
    else :
        return JsonResponse({"state": "unknown", 'download_rate': download_rate_s, 'upload_rate': upload_rate_s})

