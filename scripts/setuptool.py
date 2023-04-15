import sys
import os
import paramiko
import logging
import time

import subprocess as sp
import xml.etree.ElementTree as ET


from collections import namedtuple
from argparse import ArgumentParser

Node = namedtuple('Node', ['name', 'intf_ip', 'host_ip', 'hostname', 'port', 'username'])
ETHEREUM_STR        = 'ethereum'
DATADIR_STR         = 'datadir'
BUILDDIR_STR        = 'build'
ASSETS_STR          = 'assets'
INSTALL_FILE_STR    = 'install.sh'
ACCOUNT_LOGS_STR    = 'logs.txt'
TMUX_STR            = 'tmux'
BOOTNODE_STR        = 'bootnode'
NODE_STR            = 'node'
BOOTNODE_IDX        = 0
MASTERNODE_IDX        = 1
FUSE_MOUNT_POINT    = 'FuseMnt'
ETHEREUM_DATA_DIR    = 'EthData'


def get_local_assets(app):
    return os.path.join(os.environ['PROJ_HOME'], ASSETS_STR, app)

def get_local_builddir():
    return os.path.join(os.environ['PROJ_HOME'], BUILDDIR_STR)

def get_target_assets(app, session):
    return os.path.join(os.environ['PROJ_PARENT'], FUSE_MOUNT_POINT)

def get_target_datadir(app, session):
    return os.path.join(get_target_assets(app, session), DATADIR_STR)

def get_target_installdir(app, session):
    return os.path.join(get_target_assets(app, session), ETHEREUM_STR)

def get_target_install_script(app, session):
    return os.path.join(get_target_assets(app, session), ETHEREUM_STR, INSTALL_FILE_STR)

def get_target_account_logs(app, session):
    return os.path.join(get_target_datadir(app, session), ACCOUNT_LOGS_STR)

def get_tmux_script(session):
    return os.path.join(get_local_builddir(), '.'.join([TMUX_STR, session, 'sh']))

def get_ethereum_bootnode_script(session):
    return os.path.join(get_local_builddir(), '.'.join([BOOTNODE_STR, session, 'sh']))

def get_ethereum_node_script(session):
    return os.path.join(get_local_builddir(), '.'.join([NODE_STR, session, 'sh']))

def get_launch_script(app, session):
    pass

# copy over relevant files and install libraries
def install_node(node, pkey, session):
    asset_dir = get_local_assets(ETHEREUM_STR)
    target_assets = get_target_assets(ETHEREUM_STR, session)
    target_filename = get_target_install_script(ETHEREUM_STR, session)


    logging.info('Preparing Node: {}'.format(node.name))

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=node.hostname, username=node.username, port=node.port, pkey=pkey)
    logging.info('Copying: {}'.format(asset_dir))
    scp_cmd = 'scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r {} {}@{}:{}'.format(
        asset_dir, node.username, node.hostname, target_assets
    )
    logging.info(scp_cmd)
    sp.check_call(scp_cmd, shell=True)

    stdin,stdout,stderr = client.exec_command("mkdir {}".format(get_target_datadir(ETHEREUM_STR, session))) 
    stdin,stdout,stderr = client.exec_command("chmod +x {}".format(target_filename)) 
    stdin,stdout,stderr = client.exec_command("{}".format(target_filename))
    for line in stdout.readlines(): print(line.strip())
    for line in stderr.readlines(): print(line.strip())
    client.close()
    # hopefully everything installed! 
    # error checks left as an exercise to the reader

def init_node_tmux(node, session):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -p {} {}@{}'.format(
        node.port, node.username, node.hostname
    )
    script = '''\

tmux new-window -d -t {0} -n {1}
tmux select-window -t '={1}'
tmux split-window -h
tmux send-keys -t 0 "{2}" Enter
tmux send-keys -t 1 "{2}" Enter
    '''.format(
        session, node.name, ssh_cmd
    )
    return script


def setup_account_ethereum(node, session, pkey):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -p {} {}@{}'.format(
        node.port, node.username, node.hostname
    )

    script = '''\
tmux new-window -d -t {0} -n {2}
tmux select-window -t '={2}'
tmux send-keys -t :. "{1}" Enter
tmux send-keys -t 0 "sleep 5" Enter
tmux send-keys -t 0 "yes '' | geth account new --datadir {3} |& tee -a {4}" Enter
tmux send-keys -t 0 "sleep 10" Enter
    '''.format(
            session,
            ssh_cmd,
            node.name+"_accountSetup",
            get_target_datadir(ETHEREUM_STR, session),
            get_target_account_logs(ETHEREUM_STR, session),
        )
    print("======Creating New Accounts===========")
    sp.check_call('{}'.format(script), shell=True)
    
    
    

# tmux select-window -t '={0}'
# tmux send-keys -t 1 "sleep 30" Enter
# tmux send-keys -t 0 "yes '' | geth account new --datadir {1} |& tee -a {2}" Enter
# tmux send-keys -t 0 "sleep 10" Enter

def init_node_ethereum(node, session, isBootNode = False):
    script = '''\
tmux select-window -t '={0}'
tmux send-keys -t 0 "yes '' | geth init --datadir {1} {4}/genesis.json |& tee -a {2}" Enter
tmux send-keys -t 0 "sleep 5" Enter
tmux send-keys -t 0 "tree -a {3} |& tee -a {2}" Enter
tmux send-keys -t 0 "ifconfig |& tee -a {2}" Enter

    '''.format(
            node.name,
            get_target_datadir(ETHEREUM_STR, session),
            get_target_account_logs(ETHEREUM_STR, session),
            get_target_assets(ETHEREUM_STR, session),
            get_target_installdir(ETHEREUM_STR, session)
        )

    bootnodeSript = '''\
tmux select-window -t '={0}'
tmux send-keys -t 1 "sleep 30" Enter
tmux send-keys -t 0 "yes '' | geth account new --datadir {1} |& tee -a {2}" Enter
tmux send-keys -t 0 "sleep 10" Enter
    '''.format(
            node.name,
            get_target_datadir(ETHEREUM_STR, session),
            get_target_account_logs(ETHEREUM_STR, session),
        )
    return script if not isBootNode else bootnodeSript+script

def generate_tmux_script(details, session):
    filename = get_tmux_script(session)
    if not os.path.exists(get_local_builddir()):
        os.makedirs(get_local_builddir())
    logging.info('Generating TMUX_STR Script: {}'.format(filename))
    with open(filename, 'w') as ff:
        ff.write('''\
#! /bin/bash
echo Session={0}
tmux kill-session -t {0}
tmux new -d -s {0}
tmux new-window -d -t '={0}' -n main
        '''.format(session))

        # create node windows
        for node in details:
            ff.write(init_node_tmux(node, session))
        
        # attach final tmux setup
        ff.write("""\

tmux select-window -t '=main'
        """.format(session))

    sp.check_call('chmod +x {}'.format(filename), shell=True)

def generate_ethereum_bootnode_script(bootnode, session):
    filename = get_ethereum_bootnode_script(session)
    logging.info('Generating ethereum bootnode script: {}'.format(filename))

    with open(filename, 'w') as ff:
        ff.write('''\

#! /bin/bash
echo Session={0}
tmux switch -t {0}
        '''.format(session))

        ff.write(init_node_ethereum(bootnode, session, True))

        ff.write('''\
tmux send-keys -t 1 "geth --datadir {0} --networkid 16 --nat extip:{1}" Enter
tmux send-keys -t 0 "sleep 30" Enter
tmux send-keys -t 0 "geth attach --exec admin.nodeInfo.enr {0}/geth.ipc" Enter
tmux send-keys -t 0 "geth attach {0}/geth.ipc" Enter
        '''.format(
                get_target_datadir(ETHEREUM_STR, session), bootnode.intf_ip
            )
        )
        
    sp.check_call('chmod +x {}'.format(filename), shell=True)

def get_miner_address(node, app, session, pkey):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=node.hostname, username=node.username, port=node.port, pkey=pkey)       

    query ='cat {}'.format(get_target_account_logs(ETHEREUM_STR,session))
    print(query)
    #query='cat /users/Girish/EthData/datadir/logs.txt'
    stdin, stdout, stderr = client.exec_command(query)
    print("miner addr")
    print(stderr.read())
    net_dump = stdout.readlines()
    print(net_dump)
    result =""
    for line in net_dump:
        if 'Public address of the key:' in line:
            result =line.split("Public address of the key:")[1].strip()
    print(result)
    client.close()
    return result

def create_ethereum_account(details, session, pkey):
    for idx, node in enumerate(details):
        if idx == BOOTNODE_IDX:
            continue
        print("===========setting up account========")
        setup_account_ethereum(node,session,pkey)

def generate_ethereum_node_script(details, session, bootnodeenr, pkey):
    filename = get_ethereum_node_script(session)
    logging.info('Generating ethereum node script: {}'.format(filename))
    with open(filename, 'w') as ff:
        ff.write('''\

#! /bin/bash
echo Session={0}
tmux switch -t {0}
        '''.format(session))
        for idx, node in enumerate(details):
            mineCmd=""
            if idx == BOOTNODE_IDX:
                continue
            if idx == MASTERNODE_IDX:
                minerAddress = get_miner_address(node,ETHEREUM_STR, session, pkey)
                mineCmd= '--mine --miner.threads 10 --miner.etherbase {0}'.format(minerAddress)
            ff.write(init_node_ethereum(node, session))
            ff.write('''\
tmux send-keys -t 0 "sleep 30" Enter
tmux send-keys -t 1 "geth --datadir {0} --networkid 16 --port {1} {2} --bootnodes '{3}' " Enter
tmux send-keys -t 0 "geth attach {0}/geth.ipc" Enter
            '''.format(get_target_datadir(ETHEREUM_STR, session), 30305+idx, mineCmd ,bootnodeenr))
    
    sp.check_call('chmod +x {}'.format(filename), shell=True)

def parse_manifest(manifest):
    tree = ET.parse(manifest)
    root = tree.getroot()

    # is this subject to change?
    nsmap = {'ns': 'http://www.geni.net/resources/rspec/3'}

    details = []

    for node in root.findall('ns:node', nsmap):
        name = node.get('client_id')
        intf_ip = node.find('ns:interface', nsmap).find('ns:ip', nsmap).get('address')
        host_ip = node.find('ns:host', nsmap).get('ipv4')
        auth = node.find('ns:services', nsmap).find('ns:login', nsmap)
        hostname = auth.get('hostname')
        port = auth.get('port')
        username = auth.get('username')
        details.append(Node(name=name, intf_ip=intf_ip, host_ip=host_ip, hostname=hostname, port=port, username=username))

    return details

def read_enr(node, pkey, session):
    logging.info('Attempting to read bootnode enr (node record)')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=node.hostname, username=node.username, port=node.port, pkey=pkey)
    stdin,stdout,stderr = client.exec_command(
        "geth attach --exec admin.nodeInfo.enr {0}/geth.ipc".format(get_target_datadir(ETHEREUM_STR, session))) 
    enr = stdout.readlines()[0].strip()
    logging.info('Read record: {}'.format(enr))
    client.close()
    return enr

def get_unreliabefs_scripts(node,session):
    ssh_cmd = 'ssh -oStrictHostKeyChecking=no -p {} {}@{}'.format(
        node.port, node.username, node.hostname
    )
    script = '''\
tmux new-window -d -t {0} -n {2}
tmux select-window -t '={2}'
tmux send-keys -t :. "{1}" Enter
tmux send-keys -t :. "sudo umount -f FuseMnt" Enter

tmux new-window -d -t {0} -n {3}
tmux select-window -t '={3}'
tmux send-keys -t :. "{1}" Enter
tmux send-keys -t :. "rm -rf FuseMnt" Enter
tmux send-keys -t :. "rm -rf EthData" Enter
tmux send-keys -t :. "mkdir FuseMnt" Enter
tmux send-keys -t :. "mkdir EthData" Enter
tmux send-keys -t :. "sudo apt-get install -y gcc fuse libfuse-dev" Enter

tmux new-window -d -t {0} -n {4}
tmux select-window -t '={4}' 
tmux send-keys -t :. "{1}" Enter
tmux send-keys -t :. "bash" Enter
tmux send-keys -t :. "git clone https://github.com/ligurio/unreliablefs.git" Enter
tmux send-keys -t :. "cd unreliablefs" Enter
tmux send-keys -t :. "cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug" Enter
tmux send-keys -t :. "cmake --build build --parallel" Enter
tmux send-keys -t :. "./build/unreliablefs/unreliablefs ../FuseMnt/ -basedir=../EthData -d" Enter

    '''.format(
            session,
            ssh_cmd,
            node.name+"_UnmountFs",
            node.name+"_CmakeSetup",
            node.name+"_FuseSetup",
        )
    sp.check_call('{}'.format(script), shell=True)
    


def unreliablefs_setup(node, session):
    logging.info('== Installing Fuse FS ==')
    get_unreliabefs_scripts(node, session)
            

def handle_ethereum(details, pkey, session):
    logging.info('== Installing Ethereum Tools ==')
    logging.info('Initialising tmux session: {}'.format(session))
    sp.check_call('{}'.format(get_tmux_script(session)), shell=True)

    for node in details:
            unreliablefs_setup(node, session)
            time.sleep(10)
            install_node(node, pkey, session)
    
    # generate_ethereum_bootnode_script(details[BOOTNODE_IDX], session)

    # logging.info('Working to setup bootnode at: {}'.format(details[BOOTNODE_IDX].name))
    # sp.check_call('{}'.format(get_ethereum_bootnode_script(session)), shell=True)

    # logging.info('Sleeping while bootnode setup is in progress')
    # time.sleep(45)

    # bootnode_enr = read_enr(details[BOOTNODE_IDX], pkey, session)

    create_ethereum_account(details, session, pkey)
    logging.info('Sleeping while accounts setup is in progress')
    # time.sleep(30)

    generate_ethereum_node_script(details, session, "bootnode_enr",pkey)

    logging.info('Working to setup other nodes')
    # sp.check_call('{}'.format(get_ethereum_node_script(session)), shell=True)

    logging.info('Sleeping while other node setup is in progress')
    # time.sleep(45)

    # sp.check_call('tmux attach -t {}'.format(session), shell=True)


    
def main():
    logging.basicConfig(level=logging.INFO)

    parser = ArgumentParser()
    
    parser.add_argument("--manifest", help="manifest for cloudlab")
    parser.add_argument("--pvt-key", help="private key (file)")
    parser.add_argument("--session", help="unique session identifier")
    parser.add_argument("--app", help="which app to prepare (currently only ethereum)")

    args = parser.parse_args()

    # !!! this will fail if you use RSA, change the following accordingly
    pkey = paramiko.Ed25519Key.from_private_key_file(args.pvt_key)
    session = args.session

    details = parse_manifest(args.manifest)

    logging.info('Discovered N={} Nodes: {}'.format(len(details), details))
    logging.info('Authentication enabled via ssh keys only')

    # generate tmux setup
    generate_tmux_script(details, session)

    
    if args.app == ETHEREUM_STR:
        # prepare remote hosts: copy over data, install relevant libraries
        handle_ethereum(details, pkey, session)
    else:
        logging.error('Unsupported application. Check back again later!')
        exit(1)


if __name__ == '__main__':
    main()
