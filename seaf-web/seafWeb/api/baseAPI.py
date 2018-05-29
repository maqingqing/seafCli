import time
import os
import json
import subprocess
import sys
from urlparse import urlparse
import urllib
import urllib2

from error import Error

import ccnet

if 'HOME' in os.environ:
    DEFAULT_CONF_DIR = "%s/.ccnet" % os.environ['HOME']
else:
    DEFAULT_CONF_DIR = None


def _check_seafile():
    ''' Check ccnet and seafile have been installed '''

    dirs = os.environ['PATH'].split(':')

    def exist_in_path(prog):
        ''' Check whether 'prog' exists in system path '''
        for d in dirs:
            if d == '':
                continue
            path = os.path.join(d, prog)
            if os.path.exists(path):
                return True

    progs = ['ccnet', 'ccnet-init', 'seaf-daemon']

    for prog in progs:
        if not exist_in_path(prog):
            print "%s not found in PATH. Have you installed seafile?" % prog
            sys.exit(1)


def _config_valid(conf):
    ''' Check config directory valid '''

    if not os.path.exists(conf) or not os.path.isdir(conf):
        print "%s not exists" % conf
        return False

    config_conf = conf + "/ccnet.conf"
    seafile_ini = conf + "/seafile.ini"
    if not os.path.exists(config_conf):
        print "Could not load %s" % config_conf
        return False
    if not os.path.exists(seafile_ini):
        print "Could not load %s" % seafile_ini
        return False

    with open(seafile_ini) as f:
        for line in f:
            global seafile_datadir, seafile_worktree
            seafile_datadir = line.strip()
            seafile_worktree = os.path.join(
                os.path.dirname(seafile_datadir), "seafile")
            break

    if not seafile_datadir or not seafile_worktree:
        print "Could not load seafile_datadir and seafile_worktree"
        return False
    return True


def _conf_dir(conf):
    ''' Determine and return the value of conf_dir '''
    conf_dir = DEFAULT_CONF_DIR
    if conf:
        conf_dir = conf
    conf_dir = os.path.abspath(conf_dir)

    if not _config_valid(conf_dir):
        print "Invalid config directory"
        sys.exit(1)
    else:
        return conf_dir


def check_conf_dir(conf):
    return _conf_dir(conf)


def run_argv(argv, cwd=None, env=None, suppress_stdout=False, suppress_stderr=False):
    '''Run a program and wait it to finish, and return its exit code. The
    standard output of this program is supressed.

    '''
    with open(os.devnull, 'w') as devnull:
        if suppress_stdout:
            stdout = devnull
        else:
            stdout = sys.stdout

        if suppress_stderr:
            stderr = devnull
        else:
            stderr = sys.stderr

        proc = subprocess.Popen(argv,
                                cwd=cwd,
                                stdout=stdout,
                                stderr=stderr,
                                env=env)
        print "%s %s\n" %(argv[0], proc.pid)
        return proc.wait()


def get_env():
    env = dict(os.environ)
    ld_library_path = os.environ.get('SEAFILE_LD_LIBRARY_PATH', '')
    if ld_library_path:
        env['LD_LIBRARY_PATH'] = ld_library_path

    return env


def seaf_start_ccnet(conf):
    ''' Start ccnet daemon : parameter {confdir}'''

    conf_dir = _conf_dir(conf)
    print "Starting ccnet daemon ..."

    cmd = ["ccnet", "--daemon", "-c", conf_dir]
    if run_argv(cmd, env=get_env()) != 0:
        print "CCNet daemon failed to start."
        sys.exit(1)

    print "Started: ccnet daemon ..."


def seaf_start_seafile(conf):
    ''' start seafile daemon: parameter  {confdir}'''

    conf_dir = _conf_dir(conf)
    print "Starting seafile daemon ..."

    cmd = ["seaf-daemon", "--daemon", "-c", conf_dir, "-d", seafile_datadir,
           "-w", seafile_worktree]
    if run_argv(cmd, env=get_env()) != 0:
        print 'Failed to start seafile daemon'
        sys.exit(1)

    print "Started: seafile daemon ..."


def seaf_start_all(conf):
    ''' Start ccnet and seafile daemon '''

    _check_seafile()

    seaf_start_ccnet(conf)
    # wait ccnet process
    time.sleep(1)
    seaf_start_seafile(conf)


def seaf_init(conf=None, data_path=None):
    ''' Initialize config directories'''

    ccnet_conf_dir = DEFAULT_CONF_DIR
    if conf:
        ccnet_conf_dir = conf
    if data_path:
        seafile_path = data_path
    else:
        print "Must specify the parent path for put seafile-data"
        sys.exit(0)
    seafile_path = os.path.abspath(seafile_path)

    if os.path.exists(ccnet_conf_dir):
        print "%s already exists" % ccnet_conf_dir
        sys.exit(0)

    cmd = [ "ccnet-init", "-c", ccnet_conf_dir, "-n", "anonymous" ]
    if run_argv(cmd, env=get_env()) != 0:
        print "Failed to init ccnet"
        sys.exit(1)

    if not os.path.exists(seafile_path):
        print "%s not exists" % seafile_path
        sys.exit(0)
    seafile_ini = ccnet_conf_dir + "/seafile.ini"
    seafile_data = seafile_path + "/seafile-data"
    fp = open(seafile_ini, 'w')
    fp.write(seafile_data)
    fp.close()
    print "Writen seafile data directory %s to %s" % (seafile_data, seafile_ini)


def seaf_stop(conf):
    '''Stop seafile daemon: parameter {confdir} '''

    conf_dir = _conf_dir(conf)

    pool = ccnet.ClientPool(conf_dir)
    client = pool.get_client()
    try:
        client.send_cmd("shutdown")
    except:
        # ignore NetworkError("Failed to read from socket")
        pass


def get_peer_id(conf_dir):
    pool = ccnet.ClientPool(conf_dir)
    ccnet_rpc = ccnet.CcnetRpcClient(pool)
    info = ccnet_rpc.get_session_info()
    return info.id


def get_base_url(url):
    parse_result = urlparse(url)
    scheme = parse_result.scheme
    netloc = parse_result.netloc

    if scheme and netloc:
        return '%s://%s' % (scheme, netloc)

    return None



def urlopen(url, data=None, headers=None, method=None):
    if data:
        data = urllib.urlencode(data)
    headers = headers or {}
    req = urllib2.Request(url, data=data, headers=headers)
    if method == 'DELETE':
        req.get_method = lambda: 'DELETE'
    try:
        resp = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        return Error(e.code, e.msg)
    except urllib2.URLError as e:
        return Error(404, e.reason)
    return resp.read()


SEAF_CLI_VERSION = ""


def get_token(url, username, password, conf_dir):
    platform = 'linux'
    device_id = get_peer_id(conf_dir)
    #device_id = '802b03fd542e2367e3a68254a4db240157c21a76'
    device_name = 'terminal-' + os.uname()[1]
    client_version = SEAF_CLI_VERSION
    platform_version = ''
    data = {
        'username': username,
        'password': password,
        'platform': platform,
        'device_id': device_id,
        'device_name': device_name,
        'client_version': client_version,
        'platform_version': platform_version,
    }

    token_json = urlopen("%s/api2/auth-token/" % url, data=data)
    if isinstance(token_json, Error):
        print token_json
        return token_json
    tmp = json.loads(token_json)
    token = tmp['token']
    return token




