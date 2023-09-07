"""
/SSH.py
封装paramiko, 提供SSH连接、登录、下发命令行、读取回显等操作
添加paramiko_expect扩展使用正则表达式读数据
"""
import logging
import sys
import paramiko
from paramiko_expect import SSHClientInteraction


class SSH(object):
    def __init__(self):
        self.ssh = None
        self.chanel = None
        self.interact = None

    def link(self, host, port, username, password):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        logging.info("{}:{} SSH连接中...".format(host, port))
        self.ssh.connect(hostname=host, port=port, username=username, password=password)
        logging.info('登录成功')

    # new login: 进入诊断视图
    def login(self):
        # 创建一个SSH交互对象，用于与远程主机交互
        self.interact = SSHClientInteraction(self.ssh, timeout=10, display=False)
        while True:
            index = self.interact.expect([r'.*Y/N.*', r'.*-diagnose]', r'.*]', r'.*>'], timeout=3)
            if index == 0:
                logging.info('执行：N')
                self.interact.send('N')
            elif index == 3:
                logging.info('进入用户视图')
                self.interact.send('system-view')
            elif index == 2:
                logging.info('进入系统视图')
                self.interact.send('diagnose')
            elif index == 1:
                logging.info('进入诊断视图')
                break
            else:
                logging.warning('SSH目标客户端未响应')
                logging.warning(self.interact.current_output_clean)
                sys.exit()

    def shell_expect(self, command, prompts, timeout=120):
        logging.info('执行：' + command)
        self.interact.send(command)
        index = self.interact.expect(prompts, timeout=timeout)
        if index == -1:
            logging.warning('SSH目标客户端未响应')
        else:
            return self.interact.current_output_clean

    def __del__(self):
        # 关闭连接
        self.ssh.close()
