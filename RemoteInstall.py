'''
@author: lvcongqing
@contact: woaiwojialcq@163.com
@summary: the main function of the program is a remote login to specified host and install application.
@group BEIJING ZHIWANG: bei jing zhiwang
@note: the progrom only suppoort Linux os. 
@version: V0.1.0.0
@change: 
    1.2014-9-03 create program. 
    2.2014-9-05 modify param.
@bug:    
'''
import psshlib
import pxssh
import os
import sys
import pexpect
import subprocess
import paramiko
import socket

class RemoteInstall():
    '''
    @summary: the class function is remote login to specified host and install application.
    '''
    def __init__(self,Host='127.0.0.1',Username='root',Password='',Port=22,InstallDir='/opt/'):
        '''
        @param Host: specified host's IP address.
        @type Host: string
        @param Username: a user is used login to specified host.
        @type Username: string
        @param Password: login password.
        @type Password: string
        @param Port: ssh port.
        @type Port:int
        @param InstallDir: Software installtion path.
        @type InstallDir: string
        '''
        self.installdir = InstallDir
        self.ip = Host
        self.user = Username
        self.passwd = Password
        self.port = Port
    
    def ChkeckHostStatus(self):
        '''
        @summary: To check a specified host network.
        @return: bool 
        '''
        if os.uname()[0] == 'Linux':
            try:
                ping = pexpect.spawn("ping -c3 -W3 %s" %(self.ip))
                check = ping.expect([pexpect.TIMEOUT, "3 packets transmitted, 3 received, 0% packet loss"], 3)
                if check == 0:
                    '''
                    @note: ping timeout.
                    '''
                    return False
                elif check == 1:
                    '''
                    @note: ping OK.
                    '''
                    return True
                else:
                    '''
                    @note: ping false.
                    '''
                    return False
            except pexpect.ExceptionPexpect, e:
                print str(e)
                return False
    
    def AddMissHostKey(self):
        '''
        @summary: Add a host key to /root/.ssh/know_hosts.
        @return: bool
        '''
        if self.ChkeckHostStatus():
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.ip, self.port, self.user, self.passwd, timeout=5)
            ssh.close()
        else:
            return False
    	return True

    def RunCommand(self,cmd):
        '''
        @summary: On specified host to run a command.
        @param cmd: command string.
        @type cmd: string
        @return: bool
        '''
        try:
            '''
            @note: check the status of the host network.
            '''
            if self.ChkeckHostStatus():
                ssh = paramiko.SSHClient()
                '''
                @note: Auto add the host ssh auth key.
                '''
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(self.ip, self.port, self.user, self.passwd, timeout=5)
                stdin,stdout,stderr = ssh.exec_command(cmd)
                ssh.close()
                #print stdout.readlines()
                return stdin , stdout ,stderr
            else:
                return False
        except paramiko.SSHException ,e:
            print str(e)
            return False
        
    def TranstationFile(self,filename):
        '''
        @param filename: Transtation file path.the file type is tar.gz.
        @type filename: string
        '''
        try:
            source = filename
            dest = self.user + '@' + self.ip + ':' + self.installdir
            scp = pexpect.spawn('scp',[source,dest])
            scp.logfile = sys.stdout
            ask = 'Are you sure you want to continue connecting'
            i = scp.expect([ask,'password:',pexpect.EOF,pexpect.TIMEOUT])
            if i == 0:
                scp.sendline('yes')
                i = scp.expect([ask,'password:',pexpect.EOF,pexpect.TIMEOUT])
            elif i == 1:
                scp.sendline(self.passwd)
                scp.expect(pexpect.EOF)
            elif i == 2:
                return False
            elif i == 3:
                return False
        except pexpect.ExceptionPexpect,e:
            print str(e)
            return False
    
    def CheckAppStatus(self,Name=None,Port=None):
        '''
        @summary: Check whether a program has been installed. 
        @param cmd: Check app status command.
        @param cmd: string
        '''
        try:
            s = socket.socket(self.ip,Port)
            r = s.connect_ex()
            if r == 0:
                return True
                s.close()
            else:
                return False
        except socket.error,e:
            print str(e)
            return False
        
