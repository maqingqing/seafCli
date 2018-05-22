import os
import json
import sys
import baseAPI
import repoAPI
from error import Error
from pysearpc.common import SearpcError

import ccnet
import seafile

seafile_datadir = None
seafile_worktree = None


def seaf_list(conf):
    '''List local libraries'''

    conf_dir = baseAPI.check_conf_dir(conf)

    pool = ccnet.ClientPool(conf_dir)
    seafile_rpc = seafile.RpcClient(pool, req_pool=False)

    repos = seafile_rpc.get_repo_list(-1, -1)
    print "Name\tID\tPath"
    for repo in repos:
        print repo.name, repo.id, repo.worktree

    return repos


def seaf_sync(conf_dir, repo, folder, token, url, passwd=None):
    ''' synchronize a library from seafile server '''

    folder = os.path.abspath(folder)

    if not os.path.exists(folder):
        print "The local directory does not exists"
        return Error(-1, "The local directory does not exists")

    pool = ccnet.ClientPool(conf_dir)
    seafile_rpc = seafile.RpcClient(pool, req_pool=False)

    tmp = repoAPI.get_repo_download_info("%s/api2/repos/%s/download-info/" % (url, repo), token)

    encrypted = tmp['encrypted']
    magic = tmp.get('magic', None)
    enc_version = tmp.get('enc_version', None)
    random_key = tmp.get('random_key', None)

    clone_token = tmp['token']
    relay_id = tmp['relay_id']
    relay_addr = tmp['relay_addr']
    relay_port = str(tmp['relay_port'])
    email = tmp['email']
    repo_name = tmp['repo_name']
    version = tmp.get('repo_version', 0)

    more_info = None
    base_url = baseAPI.get_base_url(url)
    if base_url:
        more_info = json.dumps({'server_url': base_url})

    print "Starting to download ..."
    if encrypted == 1:
        if not passwd:
            return Error(-1, "passwd is required.")
        else:
            repo_passwd = passwd
        #repo_passwd = args.libpasswd if args.libpasswd else getpass.getpass("Enter password for the library: ")
    else:
        repo_passwd = None
    try:
        repo_id =seafile_rpc.clone(repo,
                          version,
                          relay_id,
                          repo_name.encode('utf-8'),
                          folder,
                          clone_token,
                          repo_passwd, magic,
                          relay_addr,
                          relay_port,
                          email, random_key, enc_version, more_info)
    except SearpcError as e:
        return Error(-2, e.msg)

def seaf_sync_progress(conf_dir, repo_id = None):

    pool = ccnet.ClientPool(conf_dir)
    ccnet_rpc = ccnet.CcnetRpcClient(pool, req_pool=False)
    seafile_rpc = seafile.RpcClient(pool, req_pool=False)

    if repo_id:
        http_task = seafile_rpc.seafile_find_transfer_task(repo_id)
        print("http::", http_task.__dict__)

    sync_progress = {}
    tasks = seafile_rpc.get_clone_tasks()
    print "# Name\tStatus\tProgress"
    for task in tasks:
        if not repo_id:
            if task.state == 'done':
                continue
            elif task.state == "fetch":
                sync_progress[task.repo_id] = "downloading"
            else:
                sync_progress[task.repo_id] = task.state

        elif repo_id == task.repo_id:

            if task.state == "fetch":
                tx_task = seafile_rpc.find_transfer_task(task.repo_id)

                sync_progress = {'id':repo_id, 'name': task.repo_name, 'state': "downloading",
                                                'finish': tx_task.block_done, 'total': tx_task.block_total,
                                                   'rate': tx_task.rate / 1024.0}
            elif task.state == "checkout":
                checkout_task = seafile_rpc.get_checkout_task(task.repo_id)

                sync_progress = {'id': repo_id, 'name': task.repo_name, state: "checkout",
                                         'finish': checkout_task.finished_files,'total':checkout_task.total_files}
            elif task.state == "error":
                tx_task = seafile_rpc.find_transfer_task(task.repo_id)
                if tx_task:
                    err = tx_task.error_str
                else:
                    err = task.error_str
                sync_progress = {'id': repo_id, 'name': task.repo_name, 'state': "error", 'message': err}
            elif task.state == 'done':
                # will be shown in repo status
                sync_progress = {'id': repo_id, 'name': task.repo_name, 'state': "finish"}
            else:
                sync_progress = {'id': repo_id, 'name': task.repo_name, 'state': "unknown"}
            print(sync_progress)
            return sync_progress
    return sync_progress

def seaf_desync(conf, repo_path):
    '''Desynchronize a library from seafile server'''

    conf_dir = baseAPI.check_conf_dir(conf)
    if not repo_path:
        print "Must specify the local path of the library"
        sys.exit(1)
    repo_path = os.path.abspath(repo_path)

    pool = ccnet.ClientPool(conf_dir)
    seafile_rpc = seafile.RpcClient(pool, req_pool=False)

    repos = seafile_rpc.get_repo_list(-1, -1)
    repo = None
    for r in repos:
        if r.worktree == repo_path.decode('utf-8'):
            repo = r
            break

    if repo:
        print "Desynchronize %s" % repo.name
        seafile_rpc.remove_repo(repo.id)
    else:
        print "%s is not a library" % repo_path


def seaf_status(conf_dir):
    '''Show status'''

    pool = ccnet.ClientPool(conf_dir)
    ccnet_rpc = ccnet.CcnetRpcClient(pool, req_pool=False)
    seafile_rpc = seafile.RpcClient(pool, req_pool=False)

    # show repo status
    print ""
    print "# Name\tStatus"
    repos = seafile_rpc.get_repo_list(-1, -1)
    repos_sync = {}
    for repo in repos:
        auto_sync_enabled = seafile_rpc.is_auto_sync_enabled()
        if not auto_sync_enabled or not repo.auto_sync:
            print "%s\t%s" % (repo.name, "auto sync disabled")
            continue

        t = seafile_rpc.get_repo_sync_task(repo.id)
        http_task = seafile_rpc.seafile_find_transfer_task(repo.id)
        print(seafile_rpc.seafile_get_repo_sync_info(repo.id).__dict__)
        if not t:
            repos_sync[repo.id] = {'state': "waiting for sync", 'path': repo.worktree, }
            print "%s\twaiting for sync" % repo.name
        elif t.state == "error":
            repos_sync[repo.id] = {'state': t.state, 'path': repo.worktree}
            print "%s\t%s" % (repo.name, t.error)
        elif t.state == "uploading" or t.state == "downloading":
            repos_sync[repo.id] = {'state': t.state, 'path': repo.worktree, 'total': http_task.block_total, 'finish': http_task.block_done, 'rate': http_task.rate}
            print "%s\t%s" % (repo.name, t.state)
            print http_task.__dict__
        else:
            repos_sync[repo.id] = {'state': t.state, 'path': repo.worktree}
            print "%s\t%s" % (repo.name, t.state)

    return repos_sync


def seaf_download(conf, repo_id, token, download_dir, url, passwd=None):
    '''Download a library from seafile server '''

    conf_dir = baseAPI.check_conf_dir(conf)

    repo = repo_id
    if not repo:
        print "Library id is required"
        sys.exit(1)

    if not url:
        print "Seafile server url need to be presented"
        sys.exit(1)

    if download_dir:
        download_dir = os.path.abspath(download_dir)
    else:
        download_dir = seafile_worktree

    print(download_dir)
    pool = ccnet.ClientPool(conf_dir)
    seafile_rpc = seafile.RpcClient(pool, req_pool=False)

    tmp = repoAPI.get_repo_download_info("%s/api2/repos/%s/download-info/" % (url, repo), token)

    encrypted = tmp['encrypted']
    magic = tmp.get('magic', None)
    enc_version = tmp.get('enc_version', None)
    random_key = tmp.get('random_key', None)

    clone_token = tmp['token']
    relay_id = tmp['relay_id']
    relay_addr = tmp['relay_addr']
    relay_port = str(tmp['relay_port'])
    email = tmp['email']
    repo_name = tmp['repo_name']
    version = tmp.get('repo_version', 0)

    more_info = None
    base_url = baseAPI.get_base_url(url)
    if base_url:
        more_info = json.dumps({'server_url': base_url})

    print "Starting to download ..."
    print "Library %s will be downloaded to %s" % (repo, download_dir)
    if encrypted == 1:
        if not passwd:
            return Error(-1, "passwd is required.")
        else:
            repo_passwd = passwd
        #repo_passwd = args.libpasswd if args.libpasswd else getpass.getpass("Enter password for the library: ")
    else:
        repo_passwd = None
    try:
        seafile_rpc.download(repo,
                         version,
                         relay_id,
                         repo_name.encode('utf-8'),
                         download_dir.encode('utf-8'),
                         clone_token,
                         repo_passwd, magic,
                         relay_addr,
                         relay_port,
                         email, random_key, enc_version, more_info)
    except SearpcError as e:
        return Error(-2, e.msg)

def seaf_get_rate(conf_dir):

    pool = ccnet.ClientPool(conf_dir)
    seafile_rpc = seafile.RpcClient(pool, req_pool=False)

    download_rate = seafile_rpc.get_download_rate()
    upload_rate = seafile_rpc.get_upload_rate()

    return download_rate, upload_rate

def seaf_cancel_sync_task(conf_dir, repo_id):
    pool = ccnet.ClientPool(conf_dir)
    seafile_rpc = seafile.RpcClient(pool, req_pool=False)

   # err = seafile_rpc.seafile_cancel_clone_task()
    try:
        seafile_rpc.seafile_cancel_clone_task(repo_id)
        err = seafile_rpc.seafile_remove_clone_task(repo_id)
    except Exception as e:
        print e
        print type(e)
        return e
    return err