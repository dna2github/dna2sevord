#!/usr/bin/python

# install chrome and xvfb to run e2e test with selenium

import sys
import os
import json
import time
import subprocess
import pexpect

GOOLGE_CHROME_REPO = '''[google-chrome]
name=google-chrome
baseurl=http://dl.google.com/linux/chrome/rpm/stable/\$basearch
enabled=1
gpgcheck=1
'''
BOOTSTRAP_NODE_VER = '8.9.0'
TARGET_NODE_VER = '6.11.4'
DISPLAY = ':98'

def printLog(log, prefix=None):
    if not log:
        return
    if not isinstance(log, str):
        log = str(log)
    for line in log.split('\n'):
        print line if not prefix else '%s %s' % (prefix, line)

def fnCheckOutput(*popenargs, **kwargs):
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    printLog("[DEBUG] %s" % popenargs[0])
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, error = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
    return output, error, retcode

def parseVMObject(log):
    # parse log for ipv4
    return { "ipv4": "0.0.0.0" }

def reportTest(testrunId, result='INVALID', resultType=''):
    o, e, r = fnCheckOutput('curl -v -XPOST https://tester/testruns/{0}/daemonupdate/ -d \'result={1}&result_type={2}&testrunid={0}\''.format(testrunId, result, resultType), shell=True)

def readArgs():
   opt = {
      'user': os.environ['USER'],
      'server_ovf': 'service.ovf',
      'tester_ovf': 'tester.ovf', # centos
      'server': None,
      'tester': None,
      'status': 'FAIL',
      'substatus': '',
      'vm_name_prefix': 'ui-test',
      'keep_vm': False,
      'preload_vm': False,
      'interactive': False,
   }
   for i, item in enumerate(sys.argv):
      if item == '--server-ovf':
         opt['server_ovf'] = sys.argv[i+1]
      elif item == '--tester-ovf':
         opt['tester_ovf'] = sys.argv[i+1]
      elif item == '--testrunid':
         opt['testrun'] = sys.argv[i+1]
      elif item == '--devtools_blddir':
         opt['build'] = '/build{0}'.format(sys.argv[i+1])
      elif item == '--resultsdir':
         opt['result'] = sys.argv[i+1]
      elif item == '--user':
         opt['user'] = sys.argv[i+1]
      elif item == '--vm-name-prefix':
         opt['vm_name_prefix'] = sys.argv[i+1]
      elif item == '--keep-vm':
         opt['keep_vm'] = True
      elif item == '--preload-vm':
         opt['preload_vm'] = True
      elif item == '--interactive':
         opt['interactive'] = True
   os.environ['USER'] = opt['user']
   o, e, r = fnCheckOutput('env', shell=True)
   printLog(o, prefix='[env]')
   return opt

def prepareEnvironment(opt):
    o, e, r = fnCheckOutput('mount', shell=True)
    printLog(o, prefix='[mount]')
    printLog(e)
    # kill previous machine if exists
    destroyVirtualMachine(opt['user'], '{0}-server'.format(opt['vm_name_prefix']))
    destroyVirtualMachine(opt['user'], '{0}-tester'.format(opt['vm_name_prefix']))
    return True

def deployVirtualMachineFromOVF(vmname, ovf, memory=512, cpus=1):
    o, e, r = fnCheckOutput('iaas deploy ovf --memory={2} --cpus={3} {0} {1}'.format(vmname, ovf, memory, cpus), shell=True)
    printLog(o, prefix='[nimbus-deploy/I]')
    printLog(e, prefix='[nimbus-deploy/E]')
    if r:
        destroyVirtualMachine(opt)
        reportTest(opt['testrun'], 'INVALID', 'I')
        return None
    obj = parseVMObject(o)
    printLog(json.dumps(obj), prefix='[iaas-deploy/R]')
    return obj

def destroyVirtualMachine(user, vmname, pod=None):
    cmd = 'iaas kill {0}-{1}'.format(user, vmname)
    if pod:
        cmd = 'NIMBUS={0} {1}'.format(pod, cmd)
    o, e, r = fnCheckOutput(cmd, shell=True)
    printLog(o, prefix='[iaas-kill/I]')
    printLog(e, prefix='[iaas-kill/E]')
    if r:
        return False
    return True

def runSSHCommand(host, vmuser, cmd, vmpass=None, sshkey=None, interactive=False):
    try:
        if sshkey:
            sshkey = '-i {0}'.format(sshkey)
        else:
            sshkey = ''
        cmd = 'ssh {3} {1}@{0} {2}'.format(host, vmuser, cmd, sshkey)
        printLog(cmd, '[DEBUG]')
        if interactive:
            ch = subprocess.Popen(cmd, shell=True)
            ch.communicate()
            retcode = ch.returncode
        else:
            ch = pexpect.spawn(cmd)
            while True:
                i = ch.expect([pexpect.EOF, 'password:', 'Are you sure you want to continue connecting (yes/no)?'], timeout=3600)
                if i == 1:
                   ch.sendline(vmpass)
                   continue
                elif i == 2:
                   ch.sendline('yes')
                   continue
                break
            printLog(ch.before, '[ssh/R]')
            while ch.status is None:
                ch.expect(pexpect.EOF, timeout=3600)
                printLog(ch.before, '[ssh/R]')
            retcode = ch.status
        if retcode != 0:
            printLog('exit code: {0}'.format(retcode), '[ssh/R]')
            return False
        return True
    except Exception as e:
        printLog(e, '[ssh/E]')
        import traceback
        traceback.print_exc()
        return False

def runSCPPush(host, vmuser, local, remote, vmpass=None, sshkey=None, interactive=False):
    try:
        if sshkey:
            sshkey = '-i {0}'.format(sshkey)
        else:
            sshkey = ''
        cmd = 'scp {4} {3} {1}@{0}:{2}'.format(host, vmuser, remote, local, sshkey)
        printLog(cmd, '[DEBUG]')
        if interactive:
            ch = subprocess.Popen(cmd, shell=True)
            ch.communicate()
            retcode = ch.returncode
        else:
            ch = pexpect.spawn(cmd)
            while True:
                i = ch.expect([pexpect.EOF, 'password:', 'Are you sure you want to continue connecting (yes/no)?'], timeout=3600)
                if i == 1:
                   ch.sendline(vmpass)
                   continue
                elif i == 2:
                   ch.sendline('yes')
                   continue
                break
            printLog(ch.before, '[scp-push/R]')
            while ch.status is None:
                ch.expect(pexpect.EOF, timeout=3600)
                printLog(ch.before, '[ssh/R]')
            retcode = ch.status
        if retcode != 0:
            printLog('exit code: {0}'.format(retcode), '[scp-push/R]')
            return False
        return True
    except Exception as e:
        printLog(e, '[scp-push/E]')
        import traceback
        traceback.print_exc()
        return False

def make_extract_script(remote_package):
    ext = remote_package.split('.')
    if len(ext) > 2:
        if ext[-1] == 'gz' and ext[-2] == 'tar':
            return 'tar zxvf {0}'.format(remote_package)
        if ext[-1] == 'bzip2' and ext[-2] == 'tar':
            return 'tar jxvf {0}'.format(remote_package)
        if ext[-1] == 'xz' and ext[-2] == 'tar':
            return 'tar Jxvf {0}'.format(remote_package)
    if len(ext) < 2:
        return 'echo {0}'.format(remote_package)
    if ext[-1] == 'tgz':
        return 'tar zxvf {0}'.format(remote_package)
    if ext[-1] == 'zip':
        return 'unzip {0}'.format(remote_package)
    raise Exception('cannot extract package: {0}'.format(remote_package))

def make_run_script(script):
    if not script:
        return 'echo "No Script"'
    if script[0] == ':':
        # e.g. :ls -l /
        return script[1:]
    cmd = script.split(' ')[0]
    ext = cmd.split('.')
    if len(ext) == 1:
        return script
    if ext[-1] == 'py':
        return 'python {0}'.format(script)
    if ext[-1] == 'sh':
        return 'bash {0}'.format(script)
    if ext[-1] == 'js':
        return 'node {0}'.format(script)
    if ext[-1] == 'rb':
        return 'ruby {0}'.format(script)
    if ext[-1] == 'pl':
        return 'perl {0}'.format(script)
    return script

def main():
    opt = readArgs()
    testrunId = opt['testrun']

    try:
        printLog('start ...', '[launcher/I]')

        printLog('deploying server ...', '[launcher/I]')
        if opt['preload_vm']:
            o, e, r = fnCheckOutput('iaas ip', shell=True)
            printLog(o, '[launcher/I]')
            machine_ips = filter(lambda x: len(x) == 3,
                map(lambda y: y.split(': '), o.split('\n'))
            )
            server = { 'ip4': None }
            tester = { 'ip4': None }
            for ip in machine_ips:
                printLog(ip, '[launcher/I]')
                if ip[1].strip() == '{0}-{1}-server'.format(opt['user'], opt['vm_name_prefix']):
                    server['ip4'] = ip[2].strip()
                elif ip[1].strip() == '{0}-{1}-tester'.format(opt['user'], opt['vm_name_prefix']):
                    tester['ip4'] = ip[2].strip()
                printLog(server, '[launcher/I]')
                printLog(tester, '[launcher/I]')
        else:
            prepareEnvironment(opt)
            server = deployVirtualMachineFromOVF('{0}-server'.format(opt['vm_name_prefix']), opt['server_ovf'])
            if not server:
                opt['status'] = 'INVALID'
                opt['substatus'] = 'I'
                raise Exception('failed to deploy {0}-[server]'.format(opt['vm_name_prefix']))
            printLog(server, '[launcher/I]')

            printLog('deploying tester ...', '[launcher/I]')
            tester = deployVirtualMachineFromOVF('{0}-tester'.format(opt['vm_name_prefix']), opt['tester_ovf'])
            if not tester:
                opt['status'] = 'INVALID'
                opt['substatus'] = 'I'
                raise Exception('failed to deploy {0}-test-[tester]'.format(opt['vm_name_prefix']))
            printLog(tester, '[launcher/I]')

        printLog('copying source to server ...', '[launcher/I]')
        sshkey = '/nfs/id_rsa'
        local_package = '{0}/source.tar.gz'.format(opt['build'])
        if not runSCPPush(server['ip4'], 'user', local_package, '/data/source.tar.gz', sshkey=sshkey, interactive=opt['interactive']):
            opt['status'] = 'INVALID'
            opt['substatus'] = ''
            raise Exception('failed to scp source code to [server]')

        printLog('copying source to tester ...', '[launcher/I]')
        if not runSCPPush(tester['ip4'], 'root', local_package, '/tester/source.tar.gz', vmpass='???', interactive=opt['interactive']):
            opt['status'] = 'INVALID'
            opt['substatus'] = ''
            raise Exception('failed to scp source code to [tester]')

        printLog('set up server ...', '[launcher/I]')
        printLog('extract source code and restart supervisor service ...', '[launcher/I]')
        server_setup_cmds = '\'{0}\''.format(' && '.join([
            'cd /data',
            'tar zxvf /data/source.tar.gz',
            'echo do preparation and restart service ...',
        ]))
        printLog(server_setup_cmds, '[launcher/I]')
        if not runSSHCommand(server['ip4'], 'user', server_setup_cmds, sshkey=sshkey, interactive=opt['interactive']):
            opt['status'] = 'INVALID'
            opt['substatus'] = ''
            raise Exception('failed to update source code and restart service on [server]')

        printLog('set up tester ...', '[launcher/I]')
        printLog('extract source code ...', '[launcher/I]')
        printLog('import google chrome package repository ...', '[launcher/I]')
        with open('/tmp/google-chrome.repo', 'w+') as f:
            f.write(GOOLGE_CHROME_REPO)
        if not runSCPPush(tester['ip4'], 'root', '/tmp/google-chrome.repo', '/etc/yum.repos.d/google-chrome.repo', vmpass='???', interactive=opt['interactive']):
            opt['status'] = 'INVALID'
            opt['substatus'] = ''
            raise Exception('failed to scp google chrome repo config to [tester]')

        tester_setup_cmds = '\'{0}\''.format(' && '.join([
            'cd /root',
            'tar zxvf /root/source.tar.gz',
            'rpm --import https://dl-ssl.google.com/linux/linux_signing_key.pub',
        ]));
        printLog(tester_setup_cmds, '[launcher/I]')
        if not runSSHCommand(tester['ip4'], 'root', tester_setup_cmds, vmpass='???', interactive=opt['interactive']):
            opt['status'] = 'INVALID'
            opt['substatus'] = ''
            raise Exception('failed to update source code and restart service on [server]')
        printLog('install dependency packages ...', '[launcher/I]')
        for package in [
            'git', 'gcc', 'gcc-c++', 'java-1.8.0-openjdk', 'curl', 'wget', 'google-chrome-stable',
            'openssl-devel', 'openldap-devel', 'xorg-x11-server-Xvfb'
        ]:
            tester_setup_cmds = 'yum install -y {0}'.format(package)
            printLog(tester_setup_cmds, '[launcher/I]')
            if not runSSHCommand(tester['ip4'], 'root', tester_setup_cmds, vmpass='???', interactive=opt['interactive']):
                opt['status'] = 'INVALID'
                opt['substatus'] = ''
                raise Exception('failed to update source code and restart service on [server]')
        printLog('install node and prepare selenium ...', '[launcher/I]')
        tester_setup_cmds = '\'{0}\''.format(' && '.join([
            'cd /root',
            'curl -L -o node.tar.xz https://nodejs.org/dist/v{0}/node-v{0}-linux-x64.tar.xz'.format(BOOTSTRAP_NODE_VER),
            'tar Jxf node.tar.xz',
            '/root/node-v{0}-linux-x64/bin/node /root/node-v{0}-linux-x64/bin/npm install -g n'.format(BOOTSTRAP_NODE_VER),
            '/root/node-v{0}-linux-x64/bin/n {1}'.format(BOOTSTRAP_NODE_VER, TARGET_NODE_VER),
            'cd /root/src/client',
            'npm install',
            '/root/src/client/node_modules/protractor/bin/webdriver-manager update'
        ]))
        printLog(tester_setup_cmds, '[launcher/I]')
        if not runSSHCommand(tester['ip4'], 'root', tester_setup_cmds, vmpass='???', interactive=opt['interactive']):
            opt['status'] = 'INVALID'
            opt['substatus'] = ''
            raise Exception('failed to update source code and restart service on [server]')
        printLog('run xvfb server ...', '[launcher/I]')
        tester_setup_cmds = '\'{0}\''.format(' && '.join([
            'cd /root',
            'git clone git://github.com/bmc/daemonize.git',
            'cd daemonize',
            './configure',
            'make',
            '/root/daemonize/daemonize /usr/bin/Xvfb -ac {0} -screen 0 1280x1024x16'.format(DISPLAY)
        ]))
        printLog(tester_setup_cmds, '[launcher/I]')
        if not runSSHCommand(tester['ip4'], 'root', tester_setup_cmds, vmpass='???', interactive=opt['interactive']):
            opt['status'] = 'INVALID'
            opt['substatus'] = ''
            raise Exception('failed to update source code and restart service on [server]')
        time.sleep(5) # wait xvfb ready
        printLog('run test ...', '[launcher/I]')
        # DISPLAY=${DISPLAY} webdriver_manager start
        if not runSSHCommand(tester['ip4'], 'root', '\'cd /root/src && node launcher.js -d {1} -s https://{0}\''.format(server['ip4'], DISPLAY), vmpass='???', interactive=opt['interactive']):
            opt['status'] = 'FAIL'
            opt['substatus'] = ''
            raise Exception('failed in testing service on the [server]')
        else:
            opt['status'] = 'PASS'
            opt['substatus'] = ''
    except Exception as e:
        printLog(e, '[run-test/E]')
        import traceback
        traceback.print_exc()
    finally:
        if not opt['keep_vm']:
            destroyVirtualMachine(opt['user'], '{0}-server'.format(opt['vm_name_prefix']))
            destroyVirtualMachine(opt['user'], '{0}-tester'.format(opt['vm_name_prefix']))
        reportTest(opt['testrun'], opt['status'], opt['substatus'])

if __name__ == '__main__':
    main()
